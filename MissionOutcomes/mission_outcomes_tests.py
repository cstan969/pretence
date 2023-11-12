import unittest
from MissionOutcomes.mission_outcomes import MissionOutcomes
from mongodb.mongo_fncs import upsert_mission, upsert_npc
from LongTermMemory.long_term_memory import LongTermMemory

POSSIBLE_OUTCOMES = [
    {
      "npcs": "",
      "outcome_summary": "Murder all of the ruffians",
      "outcome_name": "Slaughter",
      "effects": []
    },
    {
      "npcs": "",
      "outcome_summary": "Incapacitate all of the ruffians",
      "outcome_name": "Incapacitation",
      "effects": []
    },
    {
      "npcs": [
        "TumTum"
      ],
      "outcome_summary": "Scare the wits out of the ruffians",
      "outcome_name": "Intimidation",
      "effects": []
    },
    {
      "npcs": [
        "Andre"
      ],
      "outcome_summary": "Andre specific - Andre attempts to intimidate the ruffians, but long story short, the tavern burns down",
      "outcome_name": "Intimidation (Andre)",
      "effects": []
    }
  ]


class TestMissionOutcomes():

    def test_get_mission_outcome_and_debriefing(self):
        upsert_npc(world_name='TestWorldName',
                   npc_name='Andre',
                   npc_metadata={
                       'personality': "A young, lean man with a smirk that hardly ever leaves his face and a glint of mischief in his hazel eyes. Andre's armor, while of modest make, is polished to a shine and he often parades in it as if it's the armor of a legendary hero. He carries a standard sword he named 'Dragon's Bane,' though it has yet to see any real combat. Andre loves to spin tales of his 'adventures' — slaying mythical beasts, rescuing damsels from impossible perils, and single-handedly defeating bandit camps. He has an uncanny ability to make even the most mundane event sound like an epic quest, often at the expense of the truth. Despite his tall tales, Andre's actual combat skills are rudimentary at best. Those who've adventured with him often roll their eyes at his grandiose claims, but some can't help but admire his unshakeable confidence and wonder if one day, with enough real experience, his tales might just come true."
                   })
        upsert_mission(
            world_name='TestWorldName',
            mission_name='TavernBrawl',
            mission_briefing="Ruffians have been causing trouble at the tavern. They have been getting into fights with patrons and stealing beer from the barkeep. Your mission is to stop this.",
            possible_outcomes=POSSIBLE_OUTCOMES
        )
     
        mo = MissionOutcomes(
            world_name='TestWorldName',
            user_name='TestUser',
            mission_id="missions-TestWorldName-TavernBrawl",
            npc_names=['Andre'])

        outcome = mo.get_mission_outcome_and_debriefing()


        print(outcome)

tmo = TestMissionOutcomes()
tmo.test_get_mission_outcome_and_debriefing()


