'''
Created on Oct 16, 2019

@author: cjr
'''

import datetime
import Config

class JiraObjectData(object):
    '''
    Superclass for all Jira Data objects
    '''
    def __init__(self, jiraIssue=None):
        self._jiraIssue = jiraIssue

    def getType(self):
        return self.issuetype

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
                res[k] = str(self._jiraIssue.fields.__dict__[k])
            except KeyError:
                print("Key doesn't exist: "+k)
                print(self._jiraIssue.fields.__dict__)
        return res

    def links(self):
        '''
        Return dictionary with lists of 'inwards' and 'outwards' issues. List elements are tuples with key and link name.
        '''
        inwards = []
        outwards = []
        for link in self.issuelinks:
            if hasattr(link, "outwardIssue"):
                k = link.outwardIssue.key
                n = link.type.name
                outwards.append((k,n))
            elif hasattr(link, "inwardIssue"):
                k = link.inwardIssue.key
                n = link.type.name
                inwards.append((k,n))
            else:
                print("Neither outward nor inward issue for %s" % link.__dict__)
        return {'inwards': inwards, 'outwards': outwards}

    def statusChangedTo(self, status):
        '''
        Return date at which the issue's status changed to 'status' or None if it never reached it.
        FIXME: deal with original status (now it is missed!)
        '''
        changelog = self.changelog

        for history in changelog.histories:
            for item in history.items:
                if item.field == 'status':
                    if item.toString == status:
                        #print('Date:' + history.created + ' From:' + item.fromString + ' To:' + item.toString)
                        return jiraDate2Datetime(history.created)
        return None
 
    def statusAtDate(self, d):
        '''
        Return the status of an issue at a given date
        '''
        if d < self.created:
            return None
        else:
            changelog = self.changelog
            curstatus = None
            for history in changelog.histories:
                for item in history.items:
                    if item.field == 'status':
                        if d <= jiraDate2Datetime(history.created):
                            curstatus = item.toString
            # If the status is not mentioned in the changelog,
            # it has been in the current status at any date after creation
            if curstatus is None:
                curstatus = self.status
            return curstatus
            
    def jiraLink(self, title=None):
        '''
        Create an HTML link to the issue in Jira.
        '''
        return jiraLink(self.key, title=title)

    def __getattr__(self, name):
        '''
        If no attribute is present, read it first from the encapsulated _jiraIssue, then from _jiraIssue.fields.
        Additionally, normalize the return value for complex types and datetime (which contains timezone in Jira,
        but none in standard python)
        '''
        res = None
        isField = False
        try:
            try:
                res = self._jiraIssue.__dict__[name]
            except KeyError:
                isField = True
                res = self._jiraIssue.fields.__dict__[name]
        except KeyError:
            raise AttributeError("Failed to find %s for %s" % (name,self._jiraIssue.key))
        if isField:
            #print("Field type (%s) = %s" % (name, Config.config.getFieldType(name),))
            iType = Config.config.getFieldType(name)
            if iType in ['string', 'array', 'number']:
                # nothing to be done for these types
                pass
            elif iType in ['issuetype', 'status']:
                res = str(res)
            elif iType == 'datetime':
                res = jiraDate2Datetime(str(res))
            else:
                raise KeyError("Unhandled type %s for field %s" % (iType,name))
        return res

    def __str__(self):
        '''
        The string representation of the object gives a representation of the data object's structure.
        It represents:
        * level
        * key
        * (optionally) children
        '''
        return "{'level': 'issue', 'key': '"+self.key+"'}"
    

class PortfolioData(JiraObjectData):
    '''
    Data object for a "Portfolio".
    An Portfolio is a set of initiatives describing work that can be planned, in progress, or done.
    '''
    '''
    Representing epic.
    '''

    def __init__(self, name, initiatives=None, sagas=None):
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
        s += ",".join(map(lambda x: "'"+x.key+"'", self.initiatives + self.sagas))
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
        print("Creating new initiative(%s) %s" % (jiraIssue.key, jiraIssue.fields.issuetype))
        self.epics = epics
        super().__init__(jiraIssue=jiraIssue)
    def traverse(self):
        return self.epics

    def traverse_recursive(self, exclude=None, withepics=False):
        '''
        Traverse over underlying issues recursively. Excludes epics.
        :param exclude: exclusionfunction(issue) - returns true if an issue should be *excluded* from the result
             e.g. to exclude tasks: exclusionfunction=lambda x: str(x.issuetype) == "Task"
        :param withepics: if True, include epics in the result
        :return: all issues found when traversing the tree of issues
        '''
        all_issues = []
        for epic in self.traverse():
            if withepics:
                all_issues.append(epic)
            for iss in epic.traverse():
                if not exclude or not(exclude(iss)):
                    all_issues.append(iss)
        return all_issues

    def __str__(self):
        if self.issuetype == 'Epic':
            # saga
            s = "{'level': 'saga', 'key': '"+self.key+"', 'children': ["
            s += ",".join(map(lambda x: "'"+x.key+"'", self.epics))
            s += "]}"
        else:
            # initiative
            s = "{'level': 'initiative', 'key': '"+self.key+"', 'children': ["
            s += ",".join(map(lambda x: "'"+x.key+"'", self.epics))
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
        s = "{'level': 'epic', 'key': '"+self.key+"', 'children': ["
        s += ",".join(map(lambda x: "'"+x.key+"'", self.issues))
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
    '''
    Strip the timezone from a datetime string to get a datetime without timezone, as in standard python.
    '''
    return datetime.datetime.strptime(d[:-6], '%Y-%m-%dT%H:%M:%S.%f')

def jiraLink(key,title=None):
    '''
    Create a HTML link to Jira based on the key of an issue
    FIXME: title isn't placed in HTML link
    '''
    href = Config.config.config['jira']['server'] + "/browse/"+key
    return "<a href='%s'>%s</a>" % (href, key)

        