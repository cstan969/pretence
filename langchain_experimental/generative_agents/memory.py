import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.retrievers import TimeWeightedVectorStoreRetriever
from langchain.schema import BaseMemory, Document
from langchain.schema.language_model import BaseLanguageModel
from langchain.utils import mock_now
from langchain.chat_models.base import BaseChatModel

logger = logging.getLogger(__name__)

from mongodb.mongo_fncs import get_generative_agent_memory_aggregate_importance, upsert_generative_agent_state, upsert_observation

from pydantic import BaseModel, Field, root_validator

class GenerativeAgentMemory(BaseMemory, BaseModel):
    """Memory for the generative agent."""
    llm: BaseChatModel
    memory_retriever: TimeWeightedVectorStoreRetriever
    reflection_threshold: float = Field(7, alias="reflection_threshold")
    max_tokens_limit: int = 1200  # : :meta private:
    # input keys
    queries_key: str = "queries"
    most_recent_memories_token_key: str = "recent_memories_token"
    add_memory_key: str = "add_memory"
    # output keys
    relevant_memories_key: str = "relevant_memories"
    relevant_memories_simple_key: str = "relevant_memories_simple"
    most_recent_memories_key: str = "most_recent_memories"
    now_key: str = "now"
    reflecting: bool = False
    current_plan: List[str] = []
    importance_weight: float = 0.15
    verbose: bool = Field(False, alias="verbose")
    world_name: str
    user_name: str
    npc_name: str
    aggregate_importance: Optional[float]=0

    @root_validator(pre=True)
    def set_aggregate_importance(cls, values):
        world_name = values.get("world_name")
        user_name = values.get("user_name")
        npc_name = values.get("npc_name")

        if world_name and user_name and npc_name:
            values["aggregate_importance"] = get_generative_agent_memory_aggregate_importance(world_name, user_name, npc_name)

        return values       

    def chain(self, prompt: PromptTemplate) -> LLMChain:
        return LLMChain(llm=self.llm, prompt=prompt, verbose=self.verbose)

    @staticmethod
    def _parse_list(text: str) -> List[str]:
        """Parse a newline-separated string into a list of strings."""
        lines = re.split(r"\n", text.strip())
        lines = [line for line in lines if line.strip()]  # remove empty lines
        return [re.sub(r"^\s*\d+\.\s*", "", line).strip() for line in lines]

    def _get_topics_of_reflection(self, last_k: int = 50) -> List[str]:
        """Return the 3 most salient high-level questions about recent observations."""
        prompt = PromptTemplate.from_template(
            "{observations}\n\n"
            "Given only the information above, what are the 3 most salient "
            "high-level questions we can answer about the subjects in the statements?\n"
            "Provide each question on a new line."
        )
        observations = self.memory_retriever.memory_stream[-last_k:]
        print('observations: ', observations)
        observation_str = "\n".join(
            [self._format_memory_detail(o) for o in observations]
        )
        result = self.chain(prompt).run(observations=observation_str)
        return self._parse_list(result)

    def _get_insights_on_topic(
        self, topic: str, now: Optional[datetime] = None
    ) -> List[str]:
        """Generate 'insights' on a topic of reflection, based on pertinent memories."""
        prompt = PromptTemplate.from_template(
            "Statements relevant to: '{topic}'\n"
            "---\n"
            "{related_statements}\n"
            "---\n"
            "What 5 high-level novel insights can you infer from the above statements "
            "that are relevant for answering the following question?\n"
            "Do not include any insights that are not relevant to the question.\n"
            "Do not repeat any insights that have already been made.\n\n"
            "Question: {topic}\n\n"
            "(example format: insight (because of 1, 5, 3))\n"
        )

        related_memories = self.fetch_memories(topic, now=now)
        related_statements = "\n".join(
            [
                self._format_memory_detail(memory, prefix=f"{i+1}. ")
                for i, memory in enumerate(related_memories)
            ]
        )
        result = self.chain(prompt).run(
            topic=topic, related_statements=related_statements
        )
        # TODO: Parse the connections between memories and insights
        return self._parse_list(result)

    def pause_to_reflect(self, now: Optional[datetime] = None) -> List[str]:
        """Reflect on recent observations and generate 'insights'."""
        if self.verbose:
            logger.info("Character is reflecting")
        new_insights = []
        topics = self._get_topics_of_reflection()
        for topic in topics:
            insights = self._get_insights_on_topic(topic, now=now)
            for insight in insights:
                self.add_memory(insight, now=now)
            new_insights.extend(insights)
        print('here are the insights: ', new_insights)
        return new_insights

    def _score_memory_importance(self, memory_content: str) -> float:
        """Score the absolute importance of the given memory."""
        prompt = PromptTemplate.from_template(
            "On the scale of 1 to 10, where 1 is purely mundane"
            + " (e.g., brushing teeth, making bed) and 10 is"
            + " extremely poignant (e.g., a break up, college"
            + " acceptance), rate the likely poignancy of the"
            + " following piece of memory. Respond with a single integer."
            + "\nMemory: {memory_content}"
            + "\nRating: "
        )
        score = self.chain(prompt).run(memory_content=memory_content).strip()
        if self.verbose:
            logger.info(f"Importance score: {score}")
        match = re.search(r"^\D*(\d+)", score)
        if match:
            return (float(match.group(1)) / 10) * self.importance_weight
        else:
            return 0.0

    def _score_memories_importance(self, memory_content: str) -> List[float]:
        """Score the absolute importance of the given memory."""
        prompt = PromptTemplate.from_template(
            "On the scale of 1 to 10, where 1 is purely mundane"
            + " (e.g., brushing teeth, making bed) and 10 is"
            + " extremely poignant (e.g., a break up, college"
            + " acceptance), rate the likely poignancy of the"
            + " following piece of memory. Always answer with only a list of numbers."
            + " If just given one memory still respond in a list."
            + " Memories are separated by semi colans (;)"
            + "\Memories: {memory_content}"
            + "\nRating: "
        )
        scores = self.chain(prompt).run(memory_content=memory_content).strip()

        if self.verbose:
            logger.info(f"Importance scores: {scores}")

        # Split into list of strings and convert to floats
        scores_list = [float(x) for x in scores.split(";")]

        return scores_list

    def add_memories(
        self, memory_content: str, now: Optional[datetime] = None
    ) -> List[str]:
        """Add an observations or memories to the agent's memory."""
        importance_scores = self._score_memories_importance(memory_content)
        self.aggregate_importance += max(importance_scores)
        memory_list = memory_content.split(";")

        documents = []

        for i in range(len(memory_list)):
            documents.append(
                Document(
                    page_content=memory_list[i],
                    metadata={"importance": importance_scores[i]},
                )
            )

        result = self.memory_retriever.add_documents(documents, current_time=now)
        for mem in memory_list:
            upsert_observation(world_name=self.world_name,user_name=self.user_name,npc_name=self.npc_name,observation=mem)


        # After an agent has processed a certain amount of memories (as measured by
        # aggregate importance), it is time to reflect on recent events to add
        # more synthesized memories to the agent's memory stream.
        if (
            self.reflection_threshold is not None
            and self.aggregate_importance > self.reflection_threshold
            and not self.reflecting
        ):
            self.reflecting = True
            self.pause_to_reflect(now=now)
            # Hack to clear the importance from reflection
            self.aggregate_importance = 0.0
            self.reflecting = False
        upsert_generative_agent_state(world_name=self.world_name,user_name=self.user_name,npc_name=self.npc_name,gen_ag_memory_aggregate_importance=self.aggregate_importance)
        return result

    def add_memory(
        self, memory_content: str, now: Optional[datetime] = None
    ) -> List[str]:
        """Add an observation or memory to the agent's memory."""
        print('memory_content: ', memory_content)
        importance_score = self._score_memory_importance(memory_content)
        print('importance_score: ', importance_score)


        self.aggregate_importance += importance_score
        print('aggregate importance: ', self.aggregate_importance)
        document = Document(
            page_content=memory_content, metadata={"importance": importance_score}
        )
        result = self.memory_retriever.add_documents([document], current_time=now)
        upsert_observation(world_name=self.world_name,user_name=self.user_name,npc_name=self.npc_name,observation=memory_content)

        # After an agent has processed a certain amount of memories (as measured by
        # aggregate importance), it is time to reflect on recent events to add
        # more synthesized memories to the agent's memory stream.
        if (
            self.reflection_threshold is not None
            and self.aggregate_importance > self.reflection_threshold
            and not self.reflecting
        ):
            self.reflecting = True
            self.pause_to_reflect(now=now)
            # Hack to clear the importance from reflection
            self.aggregate_importance = 0.0
            self.reflecting = False
        upsert_generative_agent_state(world_name=self.world_name,user_name=self.user_name,npc_name=self.npc_name,gen_ag_memory_aggregate_importance=self.aggregate_importance)
        return result

    def fetch_memories(
        self, observation: str, now: Optional[datetime] = None
    ) -> List[Document]:
        """Fetch related memories."""
        if now is not None:
            with mock_now(now):
                return self.memory_retriever.get_relevant_documents(observation)
        else:
            return self.memory_retriever.get_relevant_documents(observation)

    def format_memories_detail(self, relevant_memories: List[Document]) -> str:
        content = []
        for mem in relevant_memories:
            content.append(self._format_memory_detail(mem, prefix="- "))
        return "\n".join([f"{mem}" for mem in content])

    def _format_memory_detail(self, memory: Document, prefix: str = "") -> str:
        created_time = memory.metadata["created_at"].strftime("%B %d, %Y, %I:%M %p")
        return f"{prefix}[{created_time}] {memory.page_content.strip()}"

    def format_memories_simple(self, relevant_memories: List[Document]) -> str:
        return "; ".join([f"{mem.page_content}" for mem in relevant_memories])

    def _get_memories_until_limit(self, consumed_tokens: int) -> str:
        """Reduce the number of tokens in the documents."""
        result = []
        for doc in self.memory_retriever.memory_stream[::-1]:
            if consumed_tokens >= self.max_tokens_limit:
                break
            consumed_tokens += self.llm.get_num_tokens(doc.page_content)
            if consumed_tokens < self.max_tokens_limit:
                result.append(doc)
        return self.format_memories_simple(result)

    @property
    def memory_variables(self) -> List[str]:
        """Input keys this memory class will load dynamically."""
        return []

    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, str]:
        """Return key-value pairs given the text input to the chain."""
        queries = inputs.get(self.queries_key)
        now = inputs.get(self.now_key)
        if queries is not None:
            relevant_memories = [
                mem for query in queries for mem in self.fetch_memories(query, now=now)
            ]
            return {
                self.relevant_memories_key: self.format_memories_detail(
                    relevant_memories
                ),
                self.relevant_memories_simple_key: self.format_memories_simple(
                    relevant_memories
                ),
            }

        most_recent_memories_token = inputs.get(self.most_recent_memories_token_key)
        if most_recent_memories_token is not None:
            return {
                self.most_recent_memories_key: self._get_memories_until_limit(
                    most_recent_memories_token
                )
            }
        return {}

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, Any]) -> None:
        """Save the context of this model run to memory."""
        # TODO: fix the save memory key
        mem = outputs.get(self.add_memory_key)
        now = outputs.get(self.now_key)
        if mem:
            self.add_memory(mem, now=now)

    def clear(self) -> None:
        """Clear memory contents."""
        # TODO
