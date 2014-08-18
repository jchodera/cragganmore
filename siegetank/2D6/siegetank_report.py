import base64 # This may require Python 3
import os
import gzip
import siegetank
import datetime as dt

# Need a more secure way to store and load this.
my_token = os.environ["SIEGETANK_TOKEN"]
siegetank.login(my_token)

targets = siegetank.list_targets()

def data_from_target(target):
    data = {
        'steps_per_frame': target.options['steps_per_frame'],
        'description' : target.options['description'],
        'date' : dt.datetime.fromtimestamp(target.creation_date),
        'date_string' : dt.datetime.fromtimestamp(target.creation_date).strftime("%B %d, %Y"),
        'engines' : target.engines,
        'stage' : target.stage,
        'weight' : target.weight,
        'id' : target.id,
        'owner' : target.owner,
        'shards' : target.shards,
        'uri' : target.uri
        }
    return data

def data_from_stream(stream):
    data = {
        'active' : stream.active,
        'error_count' : stream.error_count,
        'frames' : stream.frames,
        'status' : stream.status,
        'id' : stream.id,
        'uri' : stream.uri
        }
    return data

for target in targets:
    td = data_from_target(target)
    streams = target.streams
    print ('{id:s>20} {date_string} {description}'.format(**td))