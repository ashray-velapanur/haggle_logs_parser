'''
1) Make sure to Sync Google Drive to local home directory such that google drive path is '~/Google Drive' where ~ is home directory
2) Go to '~/Google Drive/Alpha/downloaded_logs/logs.txt' and make sure that there are only the LAST TWO LOG RECORDS from the previous run(empty file if no previous run)
3) From '~/Google Drive/Alpha/downloaded_logs' execute the following command if there was already a previous run:
    appcfg.py --verbose --append --severity=0 --application=haggle-prod --version=1 request_logs logs.txt
   Else if there was no previous run, then execute the below command replacing <no_of_days> with number of days of logs required(do not execute this command if there was a previous run):
    appcfg.py --verbose --num_days=<no_of_days> --severity=0 --application=haggle-prod --version=1 request_logs logs.txt
4) Now execute parse_logs.py
5) On executing parse_logs.py, you should notice the following:
    a) The log.txt file should now have only the LAST TWO LOG RECORDS(most recent at time of running appcfg)
    b) The ~/Google Drive/Alpha/logs/ folder should have been updated with the latest logs for each user
    c) The ~/Google Drive/Alpha/timelines/ folder should have been updated with the latest timelines for each user
6) If you wish to run this on a local folder other than the Google Drive, then please point the LOG_BASE in the script appropriately
'''
import re
import os
import sys
import json
from time import mktime
from datetime import timedelta, datetime
from pytz import timezone

TZ_EASTERN = timezone('US/Eastern')
LOG_BASE = os.path.expanduser('~') + '/Google Drive/Logs/Launch/'
format = '%d/%b/%Y:%H:%M:%S'

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
    return 'other'

def get_string_from_datetime(time_struct, format):
    return datetime.strftime(time_struct, format)

def get_timestamp(line):
    return line.split(' ')[0].split(':')[1]

def get_string_from_timestamp(timestamp, format):
    return datetime.fromtimestamp(float(timestamp), TZ_EASTERN).strftime(format)

def get_datetime_from_timestamp(timestamp):
    return datetime.fromtimestamp(float(timestamp), TZ_EASTERN)

def get_mapping(url, params, method, timestamp):
    format = '%H:%M'
    time_struct = get_datetime_from_timestamp(timestamp)
    time_plus_15 = 'time=' + get_string_from_datetime(time_struct + timedelta(minutes=15), format)
    if url == '/users/login':
        return 'Login'
    if params and url == '/api/vendors/search': 
        ret_str = ''
        if len(params) < 6:
            if [param for param in params if param.startswith('q=')]:
                ret_str += 'Text Search'
                return ret_str
            return 'Other Search'
        if 'party_size=2' not in params:
            ret_str += 'Party Size Button/'
        if time_plus_15 not in params: 
            ret_str += 'Time Button/'
        if 'category=' not in params or 'radius=' not in params:
            ret_str += 'Filters Screen'
        if ret_str == '':
            ret_str = 'Refresh/Home Screen'
        return ret_str
    if url == '/api/haggles' and params and 'status=INTERESTED' in params and 'status=ACCEPTED' in params and 'status=AVAILED' in params:
        return 'Your Bargains Screen'
    if url == '/api/haggles' and params and 'status=INTERESTED' in params and 'status=ACCEPTED' in params:
        return 'Deal Count Badge'
    if url == '/api/haggles' and method == 'POST':
        return 'Haggle'
    if url.startswith('/api/haggles') and method == 'PUT':
        return 'Accept/Avail Deal/Entering Vendor Code'
    if url == '/api/users/me/scores/info':
        return 'Score Info'
    if url == '/users/update_accesstoken':
        return 'Exposed Data'
    if url == '/api/users/me/networks':
        return 'Settings/Data Request Screen'
    if url == '/logout':
        return 'Logout'
    if url == '/showcase/leaderboard' and method == 'GET':
        return 'Leaderboards'
    if url == '/showcase/leaderboard' and method == 'POST':
        return 'Haggle Challenge'
    if url == '/showcase/haggle_challenge':
        return 'Haggle Challenge'
    if url == '/nytd':
        return 'NYTD'
    return 'Other'

def write_to_files(requests):
    users_requests = {}
    for request in requests:
        if request['user'] == 'other' and request['endpoint'] == 'Other':
            continue
        if request['date'] not in users_requests:
            users_requests[request['date']] = {}
        if request['user'] not in users_requests[request['date']]:
            users_requests[request['date']][request['user']] = []
        users_requests[request['date']][request['user']].append(request)
    
    for date in users_requests.keys():
        for user in users_requests[date].keys():
            if not os.path.exists(LOG_BASE + 'logs/' + date + '/'):
                os.mkdir(LOG_BASE + 'logs/' + date + '/')
            if not os.path.exists(LOG_BASE + 'timelines/' + date + '/'):
                os.mkdir(LOG_BASE + 'timelines/' + date + '/')
            with open(os.path.expanduser(LOG_BASE + 'logs/') + date + '/' + user + '.csv', 'w+') as log_file:
                for request in users_requests[date][user]:
                    log_file.write(request['endpoint'] + ',' + request['url'] + ',' + str(request['params']).replace(',','/') + ',' + request['time'] + ',' + request['http_method'] + ',' + request['http_response'] + '\n')
            with open(os.path.expanduser(LOG_BASE + 'timelines/') + date + '/' + user + '.csv', 'w+') as timeline_file:
                first_line = first_time = None
                timeline_file.seek(0)
                first_line = timeline_file.readline()
                if first_line and first_line != '':
                    first_time = datetime.strptime(first_line.split(',')[1], format)
                for request in users_requests[date][user]:
                    current_time = datetime.strptime(request['time'], format)
                    if not first_time:
                        first_time = current_time
                    time_delta = current_time - first_time
                    timeline_file.write(request['endpoint'] + ',' + request['time'] + ',' + str(time_delta) + '\n')

with open(os.path.expanduser(LOG_BASE + 'downloaded_logs/logs.txt')) as downloaded_log_file:
    logs = downloaded_log_file.readlines()

requests = []

record_count = 0
skip = True
record_last = None
record_second_last = None
for line in logs:
    if not line.startswith('\t'):
        record_second_last = record_last
        record_last = []
        if record_count < 2:
            record_count = record_count + 1
            record_last.append(line)
            continue
        record_count = record_count + 1
        request = {}
        skip = False
        request['url'], request['params'] = get_url_and_params(line)
        request['http_response'] = get_http_response(line)
        request['http_method'] = get_http_method(line)
    elif skip is not True:
        request['user'] = get_user(line)
        request['timestamp'] = get_timestamp(line)
        request['time'] = get_string_from_timestamp(request['timestamp'], '%d/%b/%Y:%H:%M:%S')
        request['date'] = get_string_from_timestamp(request['timestamp'], '%d-%b')
        request['endpoint'] = get_mapping(request['url'], request['params'], request['http_method'], request['timestamp'])
        requests.append(request)
        skip = True
    record_last.append(line)

'''
if record_count > 2:
    with open(os.path.expanduser(LOG_BASE + 'downloaded_logs/logs.txt'), 'w') as downloaded_log_file:
        if record_second_last:
            for line in record_second_last:
                downloaded_log_file.write(line)
        if record_last:
            for line in record_last:
                downloaded_log_file.write(line)
'''

write_to_files(requests)

#with open('out.txt', 'w') as file:
#    json.dump(requests, file, indent=4)

