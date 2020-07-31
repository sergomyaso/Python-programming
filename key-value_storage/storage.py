import json
import os
import tempfile
import argparse

STORAGE_PATH = os.path.join(tempfile.gettempdir(), 'storage.data')

def get_data():
    if not os.path.exists(STORAGE_PATH):
        return dict()
    with open(STORAGE_PATH, 'r') as f:
        raw_data = f.read()
        if raw_data:
            return json.loads(raw_data)
        return dict()

def get_value_from_storage(key):
    dictionary = get_data()
    if(key not in dictionary):
        print(None)
        return
    result = str()
    for values in dictionary[key]:
        result = result + values + ", "
    print(result[0:-2])

        
def put_value_by_key(key, value):
    dictionary = get_data()
    if(key not in dictionary):
        dictionary[key] = list()
        dictionary[key].append(value)
    else:
        dictionary[key].append(value)

    with open(STORAGE_PATH, 'w') as storageFile:
        storageFile.write(json.dumps(dictionary))
   
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Key-value storage')
    parser.add_argument('--key', type=str)
    parser.add_argument('--val', type=str)
    args = parser.parse_args()

    if(args.val == None):
        get_value_from_storage(args.key)
    else:
        put_value_by_key(args.key, args.val)
