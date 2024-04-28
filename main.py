import parsl
from Apps import *
from Config import transcode_config

with parsl.load(transcode_config):
    req_str = "{\"path\": \"" + "0" + "\", \"object\": \"video1\", \"args\": {\"format\": \"mkv\"}}"
    result = transcode(req_str)
    print(result)
