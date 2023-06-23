from langchain.llms.base import LLM, LLMResult
from langchain.schema import Generation
from typing import Optional, List, Mapping, Any
import pprint

import requests

class VicunaLLM(LLM):        
    @property
    def _llm_type(self) -> str:
        return "custom"
    
    def _generate(self, prompts: List[str], stop: Optional[List[str]]=[]):
        payload={
                "prompt": prompts[0],
                "temperature": 0,
                "max_new_tokens": 512,
                "stop": stop
            }
        response = requests.post(
            "http://127.0.0.1:8000/prompt",
            json=payload
        )
        response.raise_for_status()
        return LLMResult(
            generations=[[Generation(text=response.json()["response"])]]
        )
        # return response.json()["response"]

    def prompt(self, prompt: str, stop: Optional[List[str]] = [], temperature: Optional[float]=0, max_new_tokens=512):
        response = requests.post(
            "http://127.0.0.1:8000/prompt",
            json={
                "prompt": prompt,
                "temperature": 0,
                "max_new_tokens": max_new_tokens,
                "stop": stop + ["Observation:"]
            }
        )
        response.raise_for_status()
        return response.json()["response"]
        
    def _call(self, prompt: str, stop: Optional[List[str]] = []) -> str:
        response = requests.post(
            "http://127.0.0.1:8000/prompt",
            json={
                "prompt": prompt,
                "temperature": 0,
                "max_new_tokens": 256,
                "stop": stop + ["Observation:"]
            }
        )
        response.raise_for_status()
        return response.json()["response"]
    

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {

        }
    




