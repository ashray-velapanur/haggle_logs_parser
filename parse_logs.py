import re
import sys
import json
from time import mktime
from datetime import timedelta, datetime

def get_url_and_params(line):
    url = line.split(' ')[6].split('?') 
    if len(url) > 1:
        return url[0], url[1].split('&')
    return url[0], None

def get_http_response(line):
    return line.split(' ')[8]

def get_http_method(line):
    return line.split(' ')[5].split('"')[1]

def get_user(line):
    if re.match(r"[^@]+@[^@]+\.[^@]+", line.split(' ')[1]):
        return line.split(' ')[1].strip()
    return None

def get_string_from_datetime(time_struct, format):
    return datetime.strftime(time_struct, format)

def get_timestamp(line):
    return line.split(' ')[0].split(':')[1]

def get_string_from_timestamp(timestamp, format):
    return datetime.fromtimestamp(float(timestamp)).strftime(format)

def get_datetime_from_timestamp(timestamp):
    return datetime.fromtimestamp(float(timestamp))

def get_mapping(url, params, method, timestamp):
    format = '%H:%M'
    time_struct = get_datetime_from_timestamp(timestamp)
    time_plus_15 = get_string_from_datetime(time_struct + timedelta(minutes=15), format)
    if url == '/users/login':
        return 'Login'
    if params and url == '/api/vendors/search' and not [param for param in params if param.startswith('q=')]:
        if time_plus_15 in [param.split('=')[1] for param in params if param.startswith('time=')]:
            if 'party_size=2' in params:
                return 'Refresh Button/Home Screen'
            return 'Party Size Button'
        elif 'category=' not in params or 'radius=' not in params:
            return ' Filters Screen'
        return 'Time Button'
    if url == '/api/haggles' and params is not None and 'status=INTERESTED' in params and 'status=ACCEPTED' in params and 'status=AVAILED' in params:
        return 'Your Bargains Screen'
    if url == '/api/haggles' and params is not None and 'status=INTERESTED' in params and 'status=ACCEPTED' in params:
        return 'Deal Count Badge'
    if url == '/api/haggles' and method == 'POST':
        return 'Haggle'
    if url.startswith('/api/haggles') and method == 'PUT':
        return 'Accept/Avail Deal'
    if url == '/api/users/me/scores/info':
        return 'Score Info'
    if url == '/users/update_accesstoken':
        return 'Exposed Data'
    if url == '/api/users/me/networks':
        return 'Settings/Data Request Screen'
    if url == '/logout':
        return 'Logout'
    return 'Other'

def write_to_files(requests):
    for user in set([request['user'] for request in requests if request['user']]):
        file = open(user + '_logs.csv', 'w')
        file.write('Endpoint,URL,Params,Time,Method,Response\n')
        for request in requests:
            if request['user'] == user: 
                with open(user + '_logs.csv', 'a') as file:
                    file.write(request['endpoint'] + ',' + request['url'] + ',' + str(request['params']).replace(',','/') + ',' + request['time'] + ',' + request['http_method'] + ',' + request['http_response'] + '\n')
        file.close()

with open('logs.txt') as file:
    logs = file.readlines()

requests = []

for line in logs:
    if not line.startswith('\t'):
        request = {}
        skip = False
        request['url'], request['params'] = get_url_and_params(line)
        request['http_response'] = get_http_response(line)
        request['http_method'] = get_http_method(line)
    elif skip is not True:
        request['user'] = get_user(line)
        request['timestamp'] = get_timestamp(line)
        request['time'] = get_string_from_timestamp(request['timestamp'], '%d/%b/%Y:%H:%M:%S')
        request['endpoint'] = get_mapping(request['url'], request['params'], request['http_method'], request['timestamp'])
        requests.append(request)
        skip = True

write_to_files(requests)

with open('out.txt', 'w') as file:
    json.dump(requests, file, indent=4)

