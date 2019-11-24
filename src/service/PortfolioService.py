'''
Created on Aug 15, 2019

@author: cjr

getting changelogs: https://community.atlassian.com/t5/Jira-questions/Is-it-possible-to-get-the-issue-history-using-the-REST-API/qaq-p/510094
issue = jira.issue('FOO-100', expand='changelog')
changelog = issue.changelog

for history in changelog.histories:
    for item in history.items:
        if item.field == 'status':
            print 'Date:' + history.created + ' From:' + item.fromString + ' To:' + item.toString
'''
import pickle
import jira.resources
from data.JiraObjectData import PortfolioData, InitiativeData, EpicData, IssueData, jira2DataObject
import sys
import datetime



class PortfolioService(object):
    '''
    classdocs
    '''

    def __init__(self, config):
        '''
        Constructor
        Using api token with label evolution
        '''
        self.config = config
        self.jira = config.getJira()
        self.persist = Persist(config)
    def loadPortfolio(self):
        if self.config.loadingMode() == 'jira':
            return self.loadPortfolioJira()
        elif self.config.loadingMode() == 'database':
            return self.loadPortfolioDatabase()
        elif self.config.loadingMode() == 'mixed':
            return self.loadPortfolioMixed()
        else:
            print("Unknown loading mode: %s\n[loading: [mode={..}]] in %s " % (self.config.loadingMode(),self.config.configfile))
            sys.exit(0)
            
    def loadPortfolioJira(self):
        start = datetime.datetime.now()
        initiatives = self.jira.search_issues('project=PORT')
            
        initiativeDataList = []
        #print("Sagas")
        #print(list(filter(lambda x: x.issuetype == 'Epic', initiatives)))
        #print("Initiatives")
        #print(list(filter(lambda x: x.issuetype != 'Epic', initiatives)))
        for initiative in initiatives:
            #print(initiative.key+"; type="+initiative.issuetype)
            #self.persist.load(key=initiative.key)
            #pprint.pprint(issueData.raw)
            epics = []
            for link in initiative.fields.issuelinks:
                if hasattr(link, "outwardIssue"):
                    outwardIssue = link.outwardIssue
                    # FIXME: this is already a mixed mode!
                    #data = self.persist.load(key=outwardIssue.key)
                    #if data is not None:
                    #    outwardIssue = data
                    #else:
                    #    outwardIssue = jira2DataObject(self.jira.issue(outwardIssue.key))
                    # FIXME: convert into object here
                    outwardIssue = jira2DataObject(self.jira.issue(outwardIssue.key))
                    if outwardIssue.issuetype == 'Epic':
                        # Get the issues for the epic
                        epicIssues = self.jira.search_issues("'Epic Link'="+outwardIssue.key)
                        epicDataIssues = []
                        for eI  in epicIssues:
                            print("under epic "+outwardIssue.key+": "+eI.key)
                            #self.persist.load(key=eI.key)

                            eI = self.jira.issue(eI.key, expand="changelog")
                            epicIssueData = IssueData(jiraIssue=eI)
                            self.persist.store(epicIssueData)
                            epicDataIssues.append(epicIssueData)
                        epicData = outwardIssue #EpicData(jiraIssue=outwardIssue, issues=epicDataIssues)
                        epicData.issues = epicDataIssues
                        epics.append(epicData)
                        self.persist.store(epicData)
                    else:
                        print("type = '%s'" % (outwardIssue.issuetype,))
                if hasattr(link, "inwardIssue"):
                    inwardIssue = link.inwardIssue
                    print("\tInward: " + inwardIssue.key)
            initiativeData = InitiativeData(jiraIssue=initiative, epics=epics)
            initiativeDataList.append(initiativeData)
            self.persist.store(initiativeData)
        pd = PortfolioData(self.config.getPortfolio(), initiativeDataList)
        print("Loaded portfolio in %s" % (datetime.datetime.now()-start),)
        return pd
    def loadPortfolioDatabase(self):
        #initiatives = self.jira.search_issues('project=PORT')
        start = datetime.datetime.now()
        initiatives = self.persist.loadInitiatives()
            
        initiativeDataList = []
        #print("Sagas")
        #print(list(filter(lambda x: x.issuetype == 'Epic', initiatives)))
        #print("Initiatives")
        #print(list(filter(lambda x: x.issuetype != 'Epic', initiatives)))
        for initiative in initiatives:
            print(initiative.key+"; type="+initiative.issuetype)
            epics = []
            for link in initiative.issuelinks:
                if hasattr(link, "outwardIssue"):
                    outwardIssue = self.persist.load(key=link.outwardIssue.key)
                    if outwardIssue.issuetype == 'Epic':
                        # Get the issues for the epic
                        #epicIssues = self.jira.search_issues("'Epic Link'="+outwardIssue.jiraIssue.key)
                        epicDataIssues = []
                        for ekey in outwardIssue.getStructure()['children']:
                            epicIssueData = self.persist.load(ekey)
                            epicDataIssues.append(epicIssueData)
                        epicData = outwardIssue #EpicData(jiraIssue=outwardIssue, issues=epicDataIssues)
                        epicData.issues = epicDataIssues
                        epics.append(epicData)
                    else:
                        print("type = '%s'" % (outwardIssue.issuetype,))
                if hasattr(link, "inwardIssue"):
                    inwardIssue = link.inwardIssue
                    print("\tInward: " + inwardIssue.key)
            #initiativeData = InitiativeData(jiraIssue=initiative, epics=epics)
            initiative.epics = epics
            initiativeDataList.append(initiative)
        pd = PortfolioData(self.config.getPortfolio(), initiativeDataList)
        print("Loaded portfolio in %s" % (datetime.datetime.now()-start),)
        return pd

    def loadPortfolioMixed(self):
        print("Loading mixed style (optimum from jira+database) is not implemented")
        sys.exit(0)

    def get(self, key=None):
        return self.persist.load(key, None)

    def jira(self):
        return self.jira

    def issue(self, key, expand=None):
        return self.jira.issue(key,expand=expand)
    
class Persist(object):
    def __init__(self, config):
        # Create the database table
        conn = config.getDatabase()
        c = conn.cursor()

        # Create table
        #  key: Jira issue key
        #  updated: Jira updated field
        #  issuetype: Jira issue type field
        #  issuestructure: relation with children, e.g. children of an Epic, Epics of an Initiative
        #  issue: pickled data of the Jira issue
        c.execute('''CREATE TABLE IF NOT EXISTS issues
             (
             key TEXT PRIMARY KEY, 
             updated timestamp,
             issuetype TEXT,
             issuestructure TEXT,
             issue BLOB
             )''')
        conn.commit()
        self.config = config
        c.close()
        conn.close()
        
    def store(self, objectData):
        conn = self.config.getDatabase()
        c = conn.cursor()
        print("store %s; type=%s; estimate=%s; structure=%s" % (objectData.key,objectData.getType(),objectData.timeestimate, objectData.getStructure()))
        #print('updated type=%s' % (type(objectData.updated),))
        c.execute('''INSERT OR REPLACE INTO issues VALUES (?,?,?,?,?)''',
                  (
                      objectData.key,
                      objectData.updated,
                      objectData.getType(),                      
                      str(objectData),
                      pickle.dumps(objectData.raw)))
        print('inserted %s' % (objectData.key,))
        #c.execute('''select * from issues''')
        #res = c.fetchone()
        #raw_issue = pickle.loads(res[2])
        #x = dict2resource(raw_issue)
        #x = jira.resources.Issue(None, None, raw_issue)
        #print("loading issue from db:")
        #pprint.pprint(x.__dict__)
        #print(res[2])
        conn.commit()
        c.close()
        conn.close()

    def load(self, key=None, updated=None):
        '''
        For now: only load from database
        '''
        if key is None:
            return None
        else:
            conn = self.config.getDatabase()
            c = conn.cursor()
            c.execute('''select * from issues where key=?''', (key,))
            res = c.fetchall()
            result = None
            for row in res:
                raw_issue = pickle.loads(row[4])
                issuetype = row[2]
                issuestructure = row[3]
                d = eval(issuestructure)
                level = d['level']
                x = jira.resources.Issue(None, None, raw_issue)
                if level == 'initiative':
                    print("Loading initiative %s: %s" % (key, issuestructure))
                    children = []
                    if 'children' in d.keys():
                        for k in d['children']:
                            children.append(self.load(key=k))
                    else:
                        print("No 'children' in dictionary %s" % d)
                    result = InitiativeData(jiraIssue=x,epics=children)                   
                elif level == 'epic':
                    print("Loading epic %s: %s" %(key, issuestructure))
                    children = []
                    if 'children' in d.keys():
                        for k in d['children']:
                            children.append(self.load(key=k))
                    else:
                        print("No 'children' in dictionary %s" %d)
                    result = EpicData(jiraIssue=x,issues=children)
                else:
                    result = IssueData(jiraIssue=x)
            c.close()
            conn.close()
            return result
    def loadInitiatives(self):
            conn = self.config.getDatabase()
            c = conn.cursor()
            c.execute("select * from issues where key LIKE 'PORT%'")
            res = c.fetchall()
            initiatives = []
            for row in res:
                key = row[0]
                raw_issue = pickle.loads(row[4])
                issuetype = row[2]
                issuestructure = row[3]
                x = jira.resources.Issue(None, None, raw_issue)
                print("Loading initiative: "+issuestructure)
                d = eval(issuestructure)
                children = []
                if 'children' in d.keys():
                    for k in d['children']:
                        children.append(self.load(key=k))
                else:
                    print("No 'children' in dictionary %s for initiative %s" % (d, key))
                initiatives.append(InitiativeData(jiraIssue=x,epics=children))
            return initiatives              

if __name__ == 'main':
    pass
            
        
        
        