'''
Created on Sep 8, 2019

@author: cjr
'''

class TeamData(object):
    '''
    Data object for a team
    '''


    def __init__(self, params):
        '''
        Constructor
        '''
        self.memberList = []
    
    def addMember(self, teamMember):
        self.memberList.append(teamMember)
    def getMembers(self):
        return self.memberList
    
        