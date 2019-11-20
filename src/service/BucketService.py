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
            created = iss.created
            # JIRA string format of datetime: 2019-10-26 08:51:32.506000+02:00
            # WARNING 1: the parsing string below does not work for python versions < 3.2 and might not work on all platforms
            #date_time_obj = datetime.datetime.strptime(created, '%Y-%m-%dT%H:%M:%S.%f%z')
            # WARNING 2: cutting of the timezone information
            #print(date_time_obj)
#            if date_time_obj < lastWeek:
#                print("older %s: %s" % (iss.key, date_time_obj))
#            else:
#                print("newer %s: %s" % (iss.key, date_time_obj))
    def cumulative(self, dictionary):
        '''
        Count up the values in the dictionary, that is, to every next higher value, the sum of all previous values is added.
        '''
        output = dictionary.copy()
        sortedKeys = list(output.keys())
        sortedKeys.sort()
        
        total = 0
        for k in sortedKeys:
            output[k] = output[k] + total
            total = output[k]
        return output

class Period(object):
    '''
    Deal with periods to be analysed.
    '''
    def __init__(self):
        pass
    def datelist(self, issues):
        (start, end) = self.interval(issues)
        print("start=%s; end=%s" % (start,end))
        end = datetime.datetime.now()
        return self.generate(start,end)
    def generate(self, start, end):
        '''
        Generate list of periods (dates) based on start date and end date.
        All dates are set to the beginning of the day, except the last one which is set to the
        end of the day.
        '''
        lst = []
        for i in range(int((end - start).days)+1):
            # code below for excluding weekends, but I work during weekends, so leaving it out now
            #nextDate = start + datetime.timedelta(i)
            #if nextDate.weekday() not in (5, 6):
            #    lst.append(start + datetime.timedelta(i))
            lst.append(start + datetime.timedelta(i))
        # set all period dates to the start of the day, except for the last one, which is set to the end of the day
        # reason is to be maximally inclusive.
        lst = (list(map(lambda x: datetime.datetime(x.year, x.month, x.day, 0, 0, 0), lst)))
        d = lst[len(lst)-1]
        lst[len(lst)-1] = datetime.datetime(d.year, d.month, d.day, 23, 59, 59)
        return lst
    def interval(self, issues):
        start = datetime.datetime.now()
        end = datetime.datetime(1970,1,1)
        for iss in issues:
            if iss.created < start:
                start = iss.created
            if iss.created > end:
                end = iss.created
        if start > end:
            start = end
        print("Start = %s; End = %s" % (start, end))
        return (start,end)
    def interval_dates(self, dates):
        dates.sort()
        start = min(dates)
        end = max(dates)
        return (start, end)

    def periodMatch(self, matchDate, interval=[]):
        for d in interval:
            if matchDate < d:
                return d
        return interval[-1]

    def analyse_monotonic(self, issues, matchfunction):
        '''
        Value changes only once from false to true.
        matchfunction returns the date at which the condition changes for an issue from false to true
        Resulting dictionary: dates to amounts of issues for which the condition is true, that is, where
        the matching date is equal or larger than the date of the period. Dates are sorted old to new
        '''
        (start, end) = self.interval(issues)
        res = {}
        periodlist = self.generate(start, end)
        if not periodlist:
            # FIXME: raise some specific error
            print("GOT NO PERIODLIST for (%s,%s)" % (start, end))
        for iss in issues:
            d = matchfunction(iss)
            if d:
                md = self.periodMatch(d, periodlist)
                if md in res:
                    res[md] = res[md] + 1
                else:
                    res[md] = 1

        # Sort the dictionary by key
        x = list(res.keys())
        x.sort()
        output = {}
        for k in x:
            output[k] = res[k]
        return output

    def analyse_group(self, issues, datelist, groupfunction, groupsortfunction=None):
        '''

        :param issues:
        :param datelist:
        :param groupfunction:
        :param groupsortfunction:
        :return:
        '''
        # cumulative flow diagram
        cflowdata = {}
        allgroups = []
        for d in datelist:
            cflowdata[d] = {}
            for iss in issues:
                group = groupfunction(iss, d)
                if group:
                    if group not in allgroups:
                        allgroups.append(group)

                    if group not in list(cflowdata[d].keys()):
                        cflowdata[d][group] = 1
                    else:
                        cflowdata[d][group] = cflowdata[d][group] + 1

        # Set default of zero occurrences where
        for d in datelist:
            for g in allgroups:
                if g not in cflowdata[d].keys():
                    cflowdata[d][g] = 0

        return allgroups, cflowdata

    def analyse_dates(self, dates):
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