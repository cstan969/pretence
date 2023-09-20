from unittest import TestCase
import pprint
from mongo_fncs import *

class mongo_fncs_unittests(TestCase):

    def test_collection_npcs(self):
        '''Included Functions to test:
        upsert_npc
        get_npc
        get_npcs_in_world'''
        delete_items(collection_name='npcs',query={'world_name':'test_world_name'})
        upsert_npc(world_name='test_world_name',npc_name='test_npc_name',npc_metadata={})
        npc = get_npc(world_name='test_world_name',npc_name='test_npc_name')
        npcs = get_npcs_in_world(world_name='test_world_name')
        expected_values = {
            '_id': 'npcs-test_world_name-test_npc_name', 'npc_name': 'test_npc_name',
            'world_name': 'test_world_name'
        }
        for key in expected_values.keys():
            self.assertEqual(npc[0][key],expected_values[key])
            self.assertEqual(npcs[0][key],expected_values[key])
        delete_items(collection_name='npcs',query={'world_name':'test_world_name'})
        npcs = get_npcs_in_world(world_name='test_world_name')
        self.assertEqual(npcs,[])
        print('test_collection_npcs: successful')

    def test_collection_users(self):
        delete_items(collection_name='users',query={'user_name':'test_user_name'})
        upsert_user(user_name='test_user_name')
        user = get_user(user_name='test_user_name')
        users = get_all_users()
        expected_values={'_id': 'users-test_user_name','user_name': 'test_user_name'}
        for key in expected_values.keys():
            self.assertEqual(expected_values[key],user[0][key])
            self.assertEqual(expected_values[key],users[0][key])
        delete_items(collection_name='users',query={'user_name':'test_user_name'})
        user = get_user(user_name='test_user_name')
        self.assertEqual(user,[])
        print('test_collection_users: successful')

    def test_collection_worlds(self):
        '''Included Functions to test:
        upsert_world
        get_all_worlds
        get_world'''
        delete_items(collection_name='worlds',query={'world_name':'test_world_name'})
        upsert_world(world_name='test_world_name')
        world=get_world(world_name='test_world_name')
        worlds=get_all_worlds()
        expected_values={'_id': 'worlds-test_world_name', 'world_name': 'test_world_name'}
        for key in expected_values.keys():
            self.assertEqual(expected_values[key],world[0][key])
            self.assertEqual(expected_values[key],worlds[0][key])
        delete_items(collection_name='worlds',query={'world_name':'test_world_name'})
        world=get_world(world_name='test_world_name')
        self.assertEqual(world,[])
        print('test_collection_worlds: successful')

    # def test_collection_scenes(self):
    #     '''Included Functions to test:
    #     upsert_scene
    #     get_all_scenes
    #     get_next_scene
    #     delete_scene'''
    #     scene1 = insert_scene(world_name='test_world_name',scene_info={})
    #     pprint.pprint(scene1)
    #     scene2 = insert_scene(world_name='test_world_name',scene_info={},previous_scene=scene1['_id'])
    #     pprint.pprint(scene2)
    #     next_scene = get_next_scene(scene_id=scene1['_id'])
    #     pprint.pprint(next_scene)
    #     scenes_in_order = get_all_scenes_in_order(world_name='test_world_name')
    #     pprint.pprint(scenes_in_order)
    #     delete_scene(id=scene1['_id'])
    #     delete_scene(id=scene2['_id'])

    # def test_get_scene_objectives_completed(self):
    #     items = get_scene_objectives_completed(scene_id="scenes-TraumaGame-20230711145400",user_name="Carl2")
    #     print(items)


    # def test_progress_user_to_next_scene(self):
    #     progress_user_to_next_scene(world_name='NocturnalVeil',user_name='Carl5')

    # def test_play_test_scene_in_renpy(self):
    #     world_name='NocturnalVeil'
    #     scene_id='scenes-NocturnalVeil-07112023093300'
    #     play_test_scene_in_renpy(world_name=world_name,scene_id=scene_id)

    # def test_get_progress_of_user_in_game(self):
    #     world_name='TraumaGame'
    #     user_name='James Thomas Stanhope'
    #     get_progress_of_user_in_game(world_name=world_name,user_name=user_name)

    # def test_get_all_scenes_in_order(self):
    #     world_name='Fun with Food'
    #     get_all_scenes_in_order(world_name=world_name)

    # def test_get_scene_objectives_status(self):
    #     scene_id = 'scenes-Fun with Food-20230730202644869837'
    #     user_name='James Thomas Stanhope'
    #     obj_status = get_scene_objectives_status(scene_id=scene_id,user_name=user_name)
    #     print('---')
    #     pprint.pprint(obj_status)

    # def test_get_scene(self):
    #     scene_id = 'scenes-TraumaGame-20230711145400'
    #     scene = get_scene(scene_id=scene_id)
    #     print('---')
    #     pprint.pprint(scene['objectives'])

    # def test_mark_objectives_completed(self):
    #     obj = {'objectives_completed': {"Chef Celine shares the story about the time her friend baguette was taken by humans her story": 'completed'}}
    #     scene_id = "scenes-Fun with Food-20230802112545611010"
    #     user_name = "James Thomas Stanhope"
    #     mark_objectives_completed(objectives_completed=obj['objectives_completed'],scene_id=scene_id,user_name=user_name)

    def test_upsert_knowledge(self):
        upsert_knowledge(world_name="test",tag="tag",knowledge_description="test_description",level="1",knowledge="test knowledge")
        upsert_npc(world_name='test',npc_name='test',npc_metadata={'knowledge':[['tag',1]]})
    
    def test_get_knowledge_files_npc_has_access_to(self):
        knowledge_files = get_knowledge_files_npc_has_access_to(world_name='test',npc_name='test')
        print(knowledge_files)

    def test_get_formatted_conversational_chain(self):
        chain = get_formatted_conversational_chain(world_name='Fun with Food',user_name='Carl',npc_name='Dr. Daikon')
        print(chain)

    def test_knowledge_end_to_end(self):
        tag = 'Callum'
        level = 5
        world_name = 'test'
        user_name='James Thomas Stanhope'
        npc_name='Callum'
        callum_5 = """In the days before the cataclysm, Callum was known throughout the lands as a hero of unmatched bravery and joyous spirit. Born in the bustling city of Eldoria, he was the youngest of five siblings. While his brothers and sisters took to crafts and trade, Callum's heart was always in the wilderness, drawn to adventure and the promise of uncharted territories.
As an adventurer, Callum's tales of bravery were woven into the very fabric of local legends. He crossed the Treacherous Peaks, where he saved a village from a monstrous ice wyrm; explored the mystical Whispering Caves and returned with treasures that many thought were mere myths. His laugh was infectious, his stories captivating, and wherever he went, people found hope.
However, after the cataclysm, the world Callum once knew was no more. Eldoria was among the first cities to fall, and with it, the entirety of his family. The weight of his losses bore heavily upon him, causing a shift in his demeanor. The jovial hero became a quiet, introspective wanderer.
He spent years moving from one desolate place to another. Initially, he found solace in the Silent Forest, a once-vibrant place now rendered hauntingly quiet. Here, he encountered the spirits of nature, mourning the loss of their home. They shared ancient knowledge with Callum, deepening his wisdom.
From the forest, he traveled to the Ruins of Verathis, a place that used to be a grand citadel. It was here that a significant trauma further changed him. Callum was captured by a group of raiders who saw value in ransoming the famed hero. Though he eventually escaped, the experience left deep scars, both physical and emotional, reminding him of the cruelty the world had come to harbor.
In his journey for healing and understanding, Callum stumbled upon the settlement of Sunken Hearth. Though he intended to move on, the plight of the people touched what remained of his heroic heart. The settlement became his home, a place to protect and serve."""
        upsert_knowledge(world_name='test',tag=tag,knowledge=callum_5,knowledge_description='test_backstory',level=level)
        callum = get_npc(world_name='test',npc_name='Callum')
        if 'knowledge' in callum and callum['knowledge'] != '':
            callum_knowledge = callum['knowledge']
            callum_knowledge.append([tag, level])
        else:
            callum_knowledge = [[tag,level]]
        callum['knowledge'] = callum_knowledge
        upsert_npc(world_name=world_name,npc_name='Callum',npc_metadata=callum)
        user_message = "Hey there buddy how are you?  What're you thinking about?"
        npc_response = 'Nothing important, just reminiscing about the past'
        upsert_user_npc_interaction(world_name=world_name,user_name=user_name,npc_name=npc_name,user_message=user_message,npc_response=npc_response,scene_id='scenes-test-20230815140955910513')
        # user_message = "Oh, can you tell me more about that?"
        # npc_response = 'Nothing important, just reminiscing about the past'
        # upsert_user_npc_interaction(world_name=world_name,user_name=user_name,npc_name=npc_name,user_message=user_message,npc_response=npc_response,scene_id='scenes-test-20230815140955910513')

    def test_get_number_of_user_npc_interactions(self):
        out = get_number_of_user_npc_interactions(world_name='test',
                                            user_name='James Thomas Stanhope',
                                            npc_name='Callum',
                                            scene_id='scenes-test-20230815140955910513'
                                            )
        print(out)
        

    def test_missions(self):
        upsert_mission(
            world_name='TestWorldName',
            mission_name='TavernBrawl',
            mission_briefing="Ruffians have been causing trouble at the tavern. They have been getting into fights with patrons and stealing beer from the barkeep. Your mission is to stop this.",
            possible_outcomes=[
                {
                'npcs': [],
                'outcome_summary': 'kill all of the ruffians',
                'effects': "",
                'outcome_name': "Slaughter"
                 },
                {
                'npcs': [],
                'outcome_summary': 'incapacitate all of the ruffians',
                'outcome_name': 'Mass Incapacitation',
                'effects': ""
                },
                {
                'npcs': ['Andre'],
                'outcome_summary': 'Andre attempts to intimidate the ruffians and instead pisses them off.  The ruffians burn down the tavern.',
                'outcome_name': 'Andre-Intimidation',
                'effects': ""
                }
            ]
        )

    def test_npc_objectives(self):
        # objective = create_npc_objective(world_name='TraumaGame',npc_name='Callum')
        # print(objective)
        # _id = "npc_objectives-TraumaGame-Callum-20230907120204278204"
        # update_npc_objective(
        #     npc_objective_id=_id,
        #     world_name='TraumaGame',
        #     npc_name='Callum',
        #     objective_name='Handling the Ruffians',
        #     objective_completion_string='Callum tells the player about the ruffians messing with the tavern folks.')
        

        # obj = create_npc_objective(world_name='TraumaGame',npc_name='Callum')
        # update_npc_objective(
        #     npc_objective_id=obj['_id'],
        #     world_name='TraumaGame',
        #     npc_name='Callum',
        #     objective_name='Recruit Callum',
        #     objective_completion_string='Callum agrees to join your party'
        # )

        objs = get_npc_objectives(world_name='TraumaGame',npc_name='Callum')
        print(objs)

    def test_init_game_state(self):
        '''running test for initing the game state, '''
        init_game_state(user_name='TestUser',world_name='Mercenary Manager')

    def test_update_npc_objective_game_state(self):
        update_npc_objective_game_state(
            world_name="Mercenary Manager",
            user_name="Carl11",
            npc_name="TumTum",
            npc_objective_id="npc_objectives-Mercenary Manager-TumTum-20230912162042051734",
            npc_objective_status="available"
        )

        update_npc_objective_game_state(
            world_name="Mercenary Manager",
            user_name="Carl11",
            npc_name="TumTum",
            npc_objective_id="npc_objectives-Mercenary Manager-TumTum-20230912162042051734",
            npc_objective_status="completed"
        )

    def test_get_completed_missions(self):
        miss = get_completed_missions(
            world_name="Mercenary Manager",
            user_name="Carl11"
        )
        print(miss)

tc = mongo_fncs_unittests()
# tc.test_collection_npcs()
# tc.test_collection_users()
# tc.test_collection_worlds()
# tc.test_collection_scenes()
# tc.test_get_scene_objectives_completed()
# tc.test_progress_user_to_next_scene()
# tc.test_play_test_scene_in_renpy()
# tc.test_get_progress_of_user_in_game()
# tc.test_get_all_scenes_in_order()
# tc.test_get_scene_objectives_status()
# tc.test_get_scene()
# tc.test_mark_objectives_completed()
# tc.test_upsert_knowledge()
# tc.test_get_knowledge_files_npc_has_access_to()
# tc.test_get_formatted_conversational_chain()
# tc.test_knowledge_end_to_end()
# tc.test_get_number_of_user_npc_interactions()
# tc.test_missions()
# tc.test_npc_objectives()
# tc.test_init_game_state()
# tc.test_update_npc_objective_game_state()
tc.test_get_completed_missions()