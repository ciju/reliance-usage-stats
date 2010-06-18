#!/usr/bin/python
import csv, sys, urllib2, time, datetime, string

__author__  = "ciju.ch3rian@gmail.com (ciju cherian)"

PHONENO     = YOUR_PHONE_NO
URL         = "http://myservices.relianceada.com/datausage/jsp/ProcessCDRRequest?Mdn="+str(PHONENO)+"&StartDate=$sdate&EndDate=$edate&ProductType=1&RequestType=Download"
PEAKSTART   = 6                # morning 6
PEAKEND     = 22               # night 10 pm
BILLINGDATE = 14               # 14th of month is there billing cycle!

def peak_time(t):
    hr = int(t.strip().split(':')[0])
    if hr >= PEAKSTART and hr < PEAKEND:
        return True
    return False

def get_url(day):
    if not day:
        today = datetime.date.today()
    else:
        today = day
        
    start_month = today.month
    if today.day < BILLINGDATE:
        start_month = today.month - 1

    start = datetime.datetime(today.year, start_month, BILLINGDATE).isoformat().split('T')[0]
    end   = today.isoformat()

    print string.Template(URL).substitute(sdate=start, edate=end)
    
    return string.Template(URL).substitute(sdate=start, edate=end)
        

def fetch_and_read():
    f = urllib2.urlopen(get_url(None))
    return [i for i in csv.reader(f, delimiter=',')][1:]

day_wise = {}
peak, off_peak = 0.0, 0.0

for i in fetch_and_read():
    usage = float(i[-1])
    pt = peak_time(i[1])
    d = i[0]

    def uday(pt, u, d):
        if pt:
            res = (d[0]+u, d[1])
        else:
            res = (d[0], d[1]+u)
        return res
    
    if d not in day_wise:
        day_wise[d] = (0, 0)

    day_wise[d] = uday(pt, usage, day_wise[d])

    if pt:
        peak += usage
    else:
        off_peak += usage

    # print '%s : %10.2f : %s : %10.2f' % (d, usage/1000, str(peak_time(i[1])), day_wise[d])


    
print 'peak: %.2f Kb  -- off-peak: %.2f Kb' % (peak, off_peak)
print 'Gbs = %.2f  --  %.2f' % (peak/1000000, off_peak/1000000)

print "Day wise breakup"

for i, v in sorted(day_wise.items()):
    print '%s: peak %8.2f Mb : off-peak %8.2f Mb' % (i, v[0]/1000, v[1]/1000)

