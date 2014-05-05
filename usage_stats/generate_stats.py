import os
from config import GOOGLE_DRIVE
from os import listdir
from os.path import isdir, join, isfile, expanduser
from datetime import datetime

usage_by_user_file = open(GOOGLE_DRIVE + '/1-Users/Analytics/usage_by_user.csv', 'w')
usage_by_day_file = open(GOOGLE_DRIVE + '/1-Users/Analytics/usage_by_day.csv', 'w')
f = open('users_info.csv')
lines = f.readlines()
f.close()

users_dict = {}
for line in lines:
    name, email, id = line.strip().split(' , ')
    users_dict[email] = (name, id)

google_drive = GOOGLE_DRIVE + '/Logs/Launch/timelines'
days = [d for d in listdir(google_drive) if isdir(join(google_drive, d))]

days_dict = {}
days_list = []
for day in days:
    curr_dir = join(google_drive, day)
    users_list = [f for f in listdir(curr_dir) if f.endswith('.csv')]
    days_dict[day] = users_list
    days_list.append((datetime.strptime(day, '%d-%b'), users_list))

usage_dict = {}
for day in sorted(days_dict.keys()):
    curr_users = days_dict[day]
    for user in curr_users:
        if user in usage_dict:
            usage_dict[user] = usage_dict[user] + 1
        else:
            usage_dict[user] = 1

#print 'Usage by user:'
for user_file, usage in usage_dict.iteritems():
    email = user_file[:-4]
    if email in users_dict:
        print >> usage_by_user_file, users_dict[email][0], ',', 'http://www.facebook.com/'+users_dict[email][1], ',', usage

#print ''
unique_users = set()
print >> usage_by_day_file, 'day, unique, return'
for day in sorted(days_list):
    curr_users = set([user[:-4] for user in day[1] if user[:-4] in users_dict])
    return_users = unique_users.intersection(curr_users)
    num_unique_users = len(curr_users.difference(return_users))
    num_return_users = len(return_users)
    unique_users = unique_users.union(curr_users)
    print >> usage_by_day_file, day[0].strftime('%d-%b'), ',', num_unique_users, ',', num_return_users

usage_by_user_file.close()
usage_by_day_file.close()
