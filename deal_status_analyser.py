import datetime
from os import listdir
from os.path import isfile, join

class Deal():
    def __init__(self, time):
        self.status = 'Interested'
        self.time = datetime.datetime.strptime(time, '%d/%b/%Y:%H:%M:%S')

    def inc_status(self):
        if self.status == 'Interested':
            self.status = 'Offered'
        elif self.status == 'Offered':
            self.status = 'Availed'
        elif self.status == 'Availed':
            self.status = 'Multiple Avails'

mypath = "./logs"
onlyfiles = [ f for f in listdir(mypath) if isfile(join(mypath,f)) ]

for curr_file_name in onlyfiles:
    curr_user_deals = []
    curr_deal = None
    with open(mypath + "/" + curr_file_name) as f:
        content = f.readlines()
        for line in content:
            activity = line.strip().split(',')[0]
            if activity == 'Haggle':
                curr_deal = Deal(line.strip().split(',')[-3])
                curr_user_deals.append(curr_deal)
            elif activity == 'Accept/Avail Deal/Entering Vendor Code':
                curr_deal.inc_status()
    curr_user_deals.sort(key=lambda r: r.time)
    print "USER : " + curr_file_name
    for deal in curr_user_deals:
        print deal.status + " : " + str(deal.time)
    print "------------------------------------"

