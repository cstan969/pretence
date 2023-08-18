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

    def test_collection_scenes(self):
        '''Included Functions to test:
        upsert_scene
        get_all_scenes
        get_next_scene
        delete_scene'''
        scene1 = insert_scene(world_name='test_world_name',scene_info={})
        pprint.pprint(scene1)
        scene2 = insert_scene(world_name='test_world_name',scene_info={},previous_scene=scene1['_id'])
        pprint.pprint(scene2)
        next_scene = get_next_scene(scene_id=scene1['_id'])
        pprint.pprint(next_scene)
        scenes_in_order = get_all_scenes_in_order(world_name='test_world_name')
        pprint.pprint(scenes_in_order)
        delete_scene(id=scene1['_id'])
        delete_scene(id=scene2['_id'])

    def test_get_scene_objectives_completed(self):
        items = get_scene_objectives_completed(scene_id="scenes-TraumaGame-20230711145400",user_name="Carl2")
        print(items)


    def test_progress_user_to_next_scene(self):
        progress_user_to_next_scene(world_name='NocturnalVeil',user_name='Carl5')

    def test_play_test_scene_in_renpy(self):
        world_name='NocturnalVeil'
        scene_id='scenes-NocturnalVeil-07112023093300'
        play_test_scene_in_renpy(world_name=world_name,scene_id=scene_id)

    def test_get_progress_of_user_in_game(self):
        world_name='TraumaGame'
        user_name='James Thomas Stanhope'
        get_progress_of_user_in_game(world_name=world_name,user_name=user_name)

    def test_get_all_scenes_in_order(self):
        world_name='Fun with Food'
        get_all_scenes_in_order(world_name=world_name)

    def test_get_scene_objectives_status(self):
        scene_id = 'scenes-Fun with Food-20230730202644869837'
        user_name='James Thomas Stanhope'
        obj_status = get_scene_objectives_status(scene_id=scene_id,user_name=user_name)
        print('---')
        pprint.pprint(obj_status)

    def test_get_scene(self):
        scene_id = 'scenes-TraumaGame-20230711145400'
        scene = get_scene(scene_id=scene_id)
        print('---')
        pprint.pprint(scene['objectives'])

    def test_mark_objectives_completed(self):
        obj = {'objectives_completed': {"Chef Celine shares the story about the time her friend baguette was taken by humans her story": 'completed'}}
        scene_id = "scenes-Fun with Food-20230802112545611010"
        user_name = "James Thomas Stanhope"
        mark_objectives_completed(objectives_completed=obj['objectives_completed'],scene_id=scene_id,user_name=user_name)

    def test_get_number_of_user_npc_interactions(self):
        out = get_number_of_user_npc_interactions(world_name='test',
                                            user_name='James Thomas Stanhope',
                                            npc_name='Callum',
                                            scene_id='scenes-test-20230815140955910513'
                                            )
        print(out)
        

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
tc.test_get_number_of_user_npc_interactions()

