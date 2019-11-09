'''
Created on Sep 9, 2019

@author: cjr
'''
import os
import yaml
import sqlite3
import jira
import atlassian
import datetime
import pickle

# We set the variable 'config' as a global inside this module, so it can be read from the entire application
config = None

class Config(object):
    '''
    classdocs
    '''


    def __init__(self, filename):
        '''
        Read configuration file at relative position
        '''
        global config
        script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
        abs_file_path = os.path.join(script_dir, filename)
        with open(abs_file_path, 'r') as stream:
            config = yaml.load(stream, 
                            Loader=yaml.SafeLoader)
        self.configfile = abs_file_path
        self.config = config
        self.persist = PersistConfig(self)
        print(config['plugins']['sections'])
    def getPlugins(self):
        d = self.config['plugins']['sections']
        list = []
        for k in d.keys():
            list.append(dict(cname=k, title=d[k]['title']))
        return list
    def getJira(self):
        '''
        jira client: https://pypi.org/project/jira/
        '''
        options = {
            'server': self.config['jira']['server']
        }

        return jira.JIRA(options, basic_auth=(self.config['jira']['username'], self.config['jira']['token']))
    def getAtlassianJira(self):
        '''
        atlassian client: https://pypi.org/project/atlassian-python-api/
        '''
        return atlassian.jira.Jira(
            url=self.config['jira']['server'],
            username=self.config['jira']['username'],
            password=self.config['jira']['token']
            )   
    def getDatabase(self):
        '''
        Get a database connection
        '''
        filename = self.config['database']['filename']
        path = self.config['database']['path']
        db = os.path.join(path, filename)
        return sqlite3.connect(db)
    def loadFields(self):
        start = datetime.datetime.now()
        if self.loadingMode() == 'database':
            self.fields = self.persist.loadConfig("fields")
        else:
            self.fields = {}
            all_fields = self.getAtlassianJira().get_all_fields()
            for f in all_fields:
                self.fields[f['id']] = f
            self.persist.saveConfig(key="fields", updated=None, configdata=self.fields)
        print("Loading field definitions in: %s" % (datetime.datetime.now()-start,))
    def loadingMode(self):
        loadingMode = self.config['loading']['mode']
        return loadingMode
    def getPortfolio(self):
        return self.config['portfolio']['name']
    def getFieldType(self, key):
        return self.fields[key]['schema']['type']
    def getReportDirectory(self):
        return self.config['reports']['directory']
    def __str__(self):
        return str(self.config)
    
    
class PersistConfig(object):
    '''
    Persist configuration objects
    '''
    def __init__(self,config):
                # Create the database table
        conn = config.getDatabase()
        c = conn.cursor()

        # Create table
        #  key: arbitrary key
        #  updated: timestamp of last update
        #  configdata: pickled data
        c.execute('''CREATE TABLE IF NOT EXISTS configdata
             (
             key TEXT PRIMARY KEY, 
             updated timestamp,
             configdata BLOB
             )''')
        conn.commit()
        self.config = config
        c.close()
        conn.close()

    def loadConfig(self,key=None):
        conn = self.config.getDatabase()
        c = conn.cursor()
        c.execute("select * from configdata where key = '%s'" % (key,))
        res = c.fetchall()
        if res:
            row = res[0]
            '''
            columns:
            - key
            - updated
            - blob with data
            '''
            key = row[0]
            updated = row[1]
            configdata = pickle.loads(row[2])
            return configdata  
        else:
            return None
    def saveConfig(self,key=None,updated=None, configdata=None):
        if updated is None:
            updated = datetime.datetime.now()
        conn = self.config.getDatabase()
        c = conn.cursor()
        #print("store "+objectData.key+"; type="+objectData.getType()+"; estimate="+str(objectData.timeestimate)+"; struct="+str(objectData.getStructure()))
        #print('updated type=%s' % (type(objectData.updated),))
        c.execute('''INSERT OR REPLACE INTO configdata VALUES (?,?,?)''', (
            key,
            updated,
            pickle.dumps(configdata)
        ))
        print('Inserted %s' % (configdata,))
        conn.commit()
        c.close()
        conn.close()


if __name__ == '__main__':
    c = Config(None)
