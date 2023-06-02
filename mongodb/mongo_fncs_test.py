from unittest import TestCase
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



tc = mongo_fncs_unittests()
tc.test_collection_npcs()
tc.test_collection_users()
tc.test_collection_worlds()