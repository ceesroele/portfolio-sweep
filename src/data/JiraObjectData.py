'''
Created on Oct 16, 2019

@author: cjr
'''

import datetime

class JiraObjectData(object):
    '''
    Superclass for all Jira Data objects
    '''
    def __init__(self, jiraIssue=None):
        self.jiraIssue = jiraIssue
    def getType(self):
        return str(self.jiraIssue.fields.issuetype)
    def getStructure(self):
        '''
        The structure of a data object is an evaluation of its string representation
        '''
        return eval(self.__str__())
    def traverse(self):
        return None
    def dict(self):
        '''
        Relevant fields as dictionary with values all as strings
        '''
        res = {}
        key_selection = ['summary','description','issuetype','created','updated','assignee','creator','timeoriginalestimate']
        for k in key_selection:
            try:
                res[k] = str(self.jiraIssue.fields.__dict__[k])
            except KeyError:
                print("Key doesn't exist: "+k)
                print(self.jiraIssue.fields.__dict__)
        return res
    def statusChangedTo(self,status):
        changelog = self.jiraIssue.changelog

        for history in changelog.histories:
            for item in history.items:
                if item.field == 'status':
                    if item.toString == status:
                        print('Date:' + history.created + ' From:' + item.fromString + ' To:' + item.toString)
                        return history.created
        return None
 
    def __str__(self):
        '''
        The string representation of the object gives a representation of the data object's structure.
        It represents:
        * level
        * key
        * (optionally) children
        '''
        return "{'level': 'issue', 'key': '"+self.jiraIssue.key+"'}"
    

class PortfolioData(JiraObjectData):
    '''
    Data object for a "Portfolio".
    An Portfolio is a set of initiatives describing work that can be planned, in progress, or done.
    '''
    '''
    Representing epic.
    '''

    def __init__(self, name, initiatives=None,sagas=None):
        '''
        Create epic data from Jira epic issue and issues referring to it
        '''
        self.name = name
        self.initiatives = initiatives
        self.sagas = sagas
        super().__init__(jiraIssue=None)
    def getType(self):
        return "portfolio"
    def traverse(self):
        return self.initiatives
    def __str__(self):
        s = "{'level': 'portfolio', 'key': '"+self.name+"', 'children': ["
        s += ",".join(map(lambda x: "'"+x.jiraIssue.key+"'", self.initiatives + self.sagas))
        s += "]}"
        return s

        

class InitiativeData(JiraObjectData):
    '''
    Data object for an "Initiative".
    An Initiative is a set of issues describing work that can be planned, in progress, or done.
    An Initiative extends a Responsibility with a start and end date.
    '''
    '''
    Representing epic.
    '''

    def __init__(self, jiraIssue=None, epics=None):
        '''
        Create epic data from Jira epic issue and issues referring to it
        '''
        print("Creating new initiative("+jiraIssue.key+") "+str(jiraIssue.fields.issuetype))
        self.epics = epics
        super().__init__(jiraIssue=jiraIssue)
    def traverse(self):
        return self.epics
    def __str__(self):
        if str(self.jiraIssue.fields.issuetype) == 'Epic':
            # saga
            s = "{'level': 'saga', 'key': '"+self.jiraIssue.key+"', 'children': ["
            s += ",".join(map(lambda x: "'"+x.jiraIssue.key+"'", self.epics))
            s += "]}"
        else:
            # initiative
            s = "{'level': 'initiative', 'key': '"+self.jiraIssue.key+"', 'children': ["
            s += ",".join(map(lambda x: "'"+x.jiraIssue.key+"'", self.epics))
            s += "]}"
        return s
    

class EpicData(JiraObjectData):
    '''
    Representing epic.
    '''


    def __init__(self, jiraIssue=None, issues=None):
        '''
        Create epic data from Jira epic issue and issues referring to it
        '''
        self.issues = issues
        super().__init__(jiraIssue=jiraIssue)
    def traverse(self):
        return self.issues
    def __str__(self):
        s = "{'level': 'epic', 'key': '"+self.jiraIssue.key+"', 'children': ["
        s += ",".join(map(lambda x: "'"+x.jiraIssue.key+"'", self.issues))
        s += "]}"
        return s
    

class IssueData(JiraObjectData):
    '''
    Data object for Jira issues
    '''


    def __init__(self, jiraIssue=None):
        '''
        Constructor
        '''
        self.key = jiraIssue.key
#        self.summary = jiraIssue.fields.summary
#        self.description = jiraIssue.fields.description
        #self.fields = jiraIssue.fields
        super().__init__(jiraIssue=jiraIssue)
        
def jira2DataObject(jiraIssue, level=None):
    result = None
    jiraType = str(jiraIssue.fields.issuetype)
    if jiraType == 'Epic':
        result = EpicData(jiraIssue=jiraIssue)
    else:
        result = IssueData(jiraIssue=jiraIssue)
    return result

def jiraDate2Datetime(d):
    return datetime.datetime.strptime(d[:-6], '%Y-%m-%dT%H:%M:%S.%f')
        