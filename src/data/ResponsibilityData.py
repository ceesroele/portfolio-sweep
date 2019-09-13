'''
Created on Sep 8, 2019

@author: cjr
'''

class ResponsibilityData(object):
    '''
    Data object for a "Responsibility".
    A "Responsibility" is a growing
    '''


    def __init__(self, key, summary, description):
        '''
        Constructor
        '''
        self.key = key
        self.summary = summary
        self.description = description
        self.issueList = [];
    
    def addIssue(self, issueData):
        self.issueList.append(issueData)
    def addIssues(self, issueDataList):
        self.issueList.extend(issueDataList)
    def getIssues(self):
        return self.issueList
