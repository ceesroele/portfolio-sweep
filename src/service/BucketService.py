'''
Created on Oct 27, 2019

@author: cjr
'''
import datetime
from data.JiraObjectData import jiraDate2Datetime

class TimeBucket(object):
    '''
    Divide issues into buckets for time intervals
    '''


    def __init__(self, config, issues):
        '''
        Constructor
        '''
        self.config = config
        self.issues = issues
    def allocate(self, criterion):
        lastWeek = datetime.datetime(2019,10,25)
        for iss in self.issues:
            # note that in "fields" 'created' has 'schema':  {type: 'datetime}
            #print(self.config.getFieldType("created"))
            created = iss.jiraIssue.fields.created
            # JIRA string format of datetime: 2019-10-26 08:51:32.506000+02:00
            # WARNING 1: the parsing string below does not work for python versions < 3.2 and might not work on all platforms
            #date_time_obj = datetime.datetime.strptime(created, '%Y-%m-%dT%H:%M:%S.%f%z')
            # WARNING 2: cutting of the timezone information
            date_time_obj = datetime.datetime.strptime(created[:-6], '%Y-%m-%dT%H:%M:%S.%f')
            #print(date_time_obj)
#            if date_time_obj < lastWeek:
#                print("older %s: %s" % (iss.jiraIssue.key, date_time_obj))
#            else:
#                print("newer %s: %s" % (iss.jiraIssue.key, date_time_obj))
    def cumulative(self, dictionary):
        '''
        Count up the values in the dictionary
        '''
        sortedKeys = list(dictionary.keys())
        sortedKeys.sort()
        
        total = 0
        for k in sortedKeys:
            dictionary[k] = dictionary[k] + total
            total = dictionary[k]
        return dictionary

class Period(object):
    '''
    Deal with periods to be analysed.
    '''
    def __init__(self):
        pass
    def generate(self,start,end):
        '''
        Generate list of periods (dates) based on start date and end date
        '''
        lst = []
        for i in range(int((end - start).days)):
            # code below for excluding weekends, but I work during weekends, so leaving it out now
            #nextDate = start + datetime.timedelta(i)
            #if nextDate.weekday() not in (5, 6):
            #    lst.append(start + datetime.timedelta(i))
            lst.append(start + datetime.timedelta(i))
        return lst
    def interval(self,issues):
        start = datetime.datetime.now()
        end = datetime.datetime(1970,1,1)
        for iss in issues:
            created = datetime.datetime.strptime(iss.jiraIssue.fields.created[:-6], '%Y-%m-%dT%H:%M:%S.%f')
            if created < start:
                start = created
            if created > end:
                end = created
        if start > end:
            start = end
        print("Start = %s; End = %s" % (start,end))
        return (start,end)
    def interval_dates(self,dates):
        dates.sort()
        start = min(dates)
        end = max(dates)
        return (start,end)
    def periodMatch(self, matchDate, interval=[]):
        for d in interval:
            if matchDate < d:
                return d
        return interval[-1]
    def analyse(self,issues):
        (start,end) = self.interval(issues)
        res = {}
        periodlist = self.generate(start,end)
        for iss in issues:
            created = jiraDate2Datetime(iss.jiraIssue.fields.created) # datetime.datetime.strptime(iss.jiraIssue.fields.created[:-6], '%Y-%m-%dT%H:%M:%S.%f')
            md = self.periodMatch(created, periodlist)
            #print("created %s -> %s" % (created,md))
            
            
            if md in res:
                res[md] = res[md] + 1
            else:
                res[md] = 1
        return res

    def analyse_dates(self,dates):
        dates.sort()
        (start,end) = self.interval_dates(dates)
        res = {}
        periodlist = self.generate(start,end)
        for d in dates:
            md = self.periodMatch(d, periodlist)
            #print("created %s -> %s" % (created,md))
            if md in res:
                res[md] = res[md] + 1
            else:
                res[md] = 1
        return res
            
        