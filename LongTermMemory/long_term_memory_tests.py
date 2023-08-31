from LongTermMemory.long_term_memory import LongTermMemory
import unittest
import os
from config import LONG_TERM_MEMORY_PATH


class TestLongTermMemory(unittest.TestCase):

    def setUp(self):
        # Setting up a testing environment
        self.ltm = LongTermMemory(world_name="TestWorld", user_name="TestUser", npc_name="TestNPC")
        self.observations = [
            "In days long past, I was celebrated as a hero, known for my courage and spirited joy.",
            "I was born in the vibrant city of Eldoria, the youngest among my five siblings.",
            "While my siblings found their paths in crafts and trade, my heart pulled me towards the wilderness and the allure of unexplored lands.",
            "Many of my adventures became legendary tales; I can still vividly recall my journey across the Treacherous Peaks and the confrontation with the fearsome ice wyrm.",
            "The Whispering Caves, a place others thought to be just myths, proved real to me. I ventured inside and returned with unimaginable treasures.",
            "My laughter used to be contagious, my stories an escape for many. In my presence, people found solace and hope.",
            "The cataclysm devastated everything. Eldoria, my birthplace, was among the first cities to crumble, and with its downfall, I lost my entire family.",
            "Grief transformed me. The lively, spirited Callum morphed into a silent, contemplative wanderer.",
            "I sought tranquility in the Silent Forest, which now echoed an eerie calm. The spirits of nature bestowed upon me ancient knowledge that furthered my wisdom.",
            "The once majestic citadel known as the Ruins of Verathis was another place I ventured to.",
            "During my time at the Ruins of Verathis, raiders captured me, seeing an opportunity to ransom me. The ordeal left me with scars, both on my skin and deep within my soul, reminding me daily of the world's newfound cruelty.",
            "Sunken Hearth was supposed to be just another stop in my journey, but the people's struggles resonated with the hero still left inside of me. They became my purpose, and their settlement became my refuge, a place I now call home."
        ]

        
    # def test_add_memories(self):
    #     self.ltm.add_memories(self.observations)
    #     self.assertTrue(os.path.exists(self.ltm.vector_store_index_path))

    def test_fetch_memories(self):
        observation_query = "Tell me about your birthplace."
        memories = self.ltm.fetch_memories(observation=observation_query)
        # We're expecting memories related to Eldoria
        self.assertIn("I was born in the vibrant city of Eldoria, the youngest among my five siblings.", memories)

    # Add more tests as needed

    # def tearDown(self):
    #     # Cleanup after tests. Remove created index and directory for a clean state.
    #     if os.path.exists(self.ltm.vector_store_index_path):
    #         # os.remove(self.ltm.vector_store_index_path)
    #         os.rmdir(os.path.join(LONG_TERM_MEMORY_PATH, self.ltm.world_name))

if __name__ == "__main__":
    unittest.main()