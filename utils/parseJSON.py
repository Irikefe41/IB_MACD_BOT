import json

def readJson(filename):
    
    with open('IBbot/config/'+filename, 'r') as read_file:
        data = json.load(read_file)
    return data

def jsonAdd(filename, data_dict):

    d = readJson(filename)
    d.append(data_dict)
    jsonWrite(filename, d)

def jsonWrite(filename, data_dict):
	
    with open('IBbot/config/'+filename, 'w') as write_file:
        json.dump(data_dict, write_file, default=str)
        write_file.close()