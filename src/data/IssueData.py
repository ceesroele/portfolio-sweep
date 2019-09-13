'''
Created on Aug 14, 2019

@author: cjr
'''

class IssueData(object):
    '''
    Data object for Jira issues
    '''


    def __init__(self, jiraIssue):
        '''
        Constructor
        '''
        self.key = jiraIssue.key
#        self.summary = jiraIssue.fields.summary
#        self.description = jiraIssue.fields.description
        #self.fields = jiraIssue.fields