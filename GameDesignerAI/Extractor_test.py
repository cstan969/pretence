from unittest import TestCase
from Extractor import Extractor
import pprint

class ExtractorTests(TestCase):

    def __init__(self):
        self.ex = Extractor(world_name='test2')

    def test_extract_all_npcs(self):
        all_npcs = self.ex.extract_all_npcs()
    

    
ext = ExtractorTests()
ext.test_extract_all_npcs()
# ext.test_extract_npc()