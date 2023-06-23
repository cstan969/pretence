from NPC.NpcUserInteraction import NpcUserInteraction
from unittest import TestCase


class NpcUserInteractionUnitTests(TestCase):

    def test_get_conversation(self):
        npc = NpcUserInteraction(npc_name='Captain Valeria',user_name='Carl')
        conversation = npc.get_conversation()

    def test_message_npc_and_get_response(self):
        npc = NpcUserInteraction(npc_name='Captain Valeria',user_name='Carl')
        response = npc.message_npc_and_get_response('what type of monsters am I fighting again?  Can you give me any potions or anything?')
        print(response)


npc_tests = NpcUserInteractionUnitTests()
npc_tests.test_message_npc_and_get_response()
