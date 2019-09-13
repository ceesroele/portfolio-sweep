'''
Created on Sep 9, 2019

@author: cjr
'''
import os
import yaml
import sqlite3
from jira import JIRA

class Config(object):
    '''
    classdocs
    '''


    def __init__(self, filename):
        '''
        Read configuration file at relative position
        '''
        script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
        abs_file_path = os.path.join(script_dir, filename)
        with open(abs_file_path, 'r') as stream:
            config = yaml.load(stream, 
                            Loader=yaml.SafeLoader)
        self.config = config
    def getJira(self):
        options = {
            'server': self.config['jira']['server']
        }

        return JIRA(options, basic_auth=(self.config['jira']['username'], self.config['jira']['token']))
    def getDatabase(self):
        '''
        Get a database connection
        '''
        return sqlite3.connect(self.config['database']['filename'])


if __name__ == '__main__':
    c = Config(None)