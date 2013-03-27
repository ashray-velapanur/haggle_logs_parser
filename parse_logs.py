import re
import json
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

def get_time(line):
    timestamp = line.split(' ')[0].split(':')[1]
    return datetime.fromtimestamp(float(timestamp)).strftime('%d/%b/%Y:%H:%M:%S')

def get_mapping(url, params, method, time):
    if url == '/users/login':
        return 'Login'
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
        request['time'] = get_time(line)
        request['endpoint'] = get_mapping(request['url'], request['params'], request['http_method'], request['time'])
        requests.append(request)
        skip = True

users = set()

for request in requests:
    if request['user'] is not None:
        users.add(request['user'])

for user in users:
    file = open(user + '_logs.csv', 'a')
    file.write('Endpoint,URL,Params,Time,Method,Response\n')
    for request in requests:
        if request['user'] == user:
            with open(user + '_logs.csv', 'a') as file:
                file.write(request['endpoint'] + ',' + request['url'] + ',' + str(request['params']).replace(',','/') + ',' + request['time'] + ',' + request['http_method'] + ',' + request['http_response'] + '\n')
    file.close()

