import os
import glob
from datetime import datetime

format = '%d/%b/%Y:%H:%M:%S'

def generate_timeline(file):
    timelines = []
    last_time = None 
    count = 0
    for line in file.readlines():
        timeline = {}
        timeline['number'] = count
        timeline['endpoint'] = line.split(',')[0]
        current_time = datetime.strptime(line.split(',')[3], format)
        if last_time is None:
            last_time = current_time
        timeline['time'] = current_time - last_time
        timelines.append(timeline)
        last_time = current_time 
        count += 1
    return timelines

file_names = []

for file in os.listdir('logs/'):
    file_names.append(file)

for file_name in file_names:
    f = open('logs/' + file_name)
    timelines = generate_timeline(f)
    with open('timelines/' + file_name, 'w') as file:
        for timeline in timelines:
            print >>file, str(timeline['number']) + ',' + timeline['endpoint'] + ',' + str(timeline['time'])


