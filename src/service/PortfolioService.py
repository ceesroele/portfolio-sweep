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
import pprint
import jira.resources


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
        #self.jira = JIRA(options, basic_auth=('cees.roele@gmail.com', 'XMPl3UaNMItaNZewMlJKA9F5'))
        #self.jira = config.getJira()
        self.persist = Persist(config)
    def load(self,key=None):
        
        # Get all projects viewable by anonymous users.
        #projects = self.jira.projects()
        
        # Find all issues reported by the admin
        #issues = self.jira.search_issues('assignee=admin')
        #issues = self.jira.search_issues('project=PORT')
        #for issueData in issues:
        #    print(type(issueData))
        #    #pprint.pprint(issueData.raw)
        #    self.persist.store(issueData)
        return self.persist.load(key=key)
    def jira(self):
        return self.jira
    def issue(self,key,expand=None):
        return self.jira.issue(key,expand=expand)
    
class Persist(object):
    def __init__(self, config):
        # Create the database table
        conn = config.getDatabase()
        c = conn.cursor()

        # Create table
        c.execute('''CREATE TABLE IF NOT EXISTS issues
             (
             key TEXT PRIMARY KEY, 
             updated timestamp, 
             issue BLOB
             )''')
        conn.commit()
        self.config = config
        c.close()
        conn.close()
        
    def store(self, issueData):
        print(issueData)
        conn = self.config.getJira()
        c = conn.cursor()
        print('updated type=%',type(issueData.fields.updated))
        c.execute('''INSERT OR REPLACE INTO issues VALUES (?,?,?)''',
                  (
                      issueData.key, 
                      issueData.fields.updated,
                      pickle.dumps(issueData.raw)))
        print('inserted %', issueData.key)
        c.execute('''select * from issues''')
        res = c.fetchone()
        raw_issue = pickle.loads(res[2])
        #x = dict2resource(raw_issue)
        x = jira.resources.Issue(None, None, raw_issue)
        print("loading issue from db:")
        pprint.pprint(x.__dict__)
        #print(res[2])
        conn.commit()
        c.close()
        conn.close()
    def load(self, key=None):
        '''
        For now: only load from database
        '''
        issues = []
        conn = self.config.getDatabase()
        c = conn.cursor()
        if (key == None):
            c.execute('''select * from issues''')
        else:
            c.execute('''select * from issues where key=?''',(key,))
        res = c.fetchall()
        for row in res:
            raw_issue = pickle.loads(row[2])
            x = jira.resources.Issue(None, None, raw_issue)
            issues.append(x)
        c.close()
        conn.close()
        return issues

        
if __name__ == 'main':
    pass
            
        
        
        