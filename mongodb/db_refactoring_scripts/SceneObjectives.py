'''The purpose of this refactor is for converting old objectives format of List[List[str]] -> List[List[Dict]] '''

from mongodb.mongo_utils import *

scenes = query_collection(collection_name='scenes',query={})
print(len(scenes))

for scene in scenes:
    #this is for converting old objectives format of List[List[str]] -> List[List[Dict]]
    old_objectives = scene['objectives']
    if isinstance(old_objectives, list) and len(old_objectives) > 0:
        if isinstance(old_objectives, list) and len(old_objectives[0]) > 0:
            if isinstance(old_objectives[0][0], dict):#scene objectives of correct format lready
                new_objectives = old_objectives
            else:#scene objectives are of the old format and need switching
                new_objectives = [[{"objective": item} for item in inner_list] for inner_list in scene['objectives']]
    scene['objectives'] = new_objectives
    upsert_item(collection_name='scenes',item=scene)