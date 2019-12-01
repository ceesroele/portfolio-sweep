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
import pprint

# *** Configuration: default settings ***********************************

STATIC_URL = '/static/'

# Settings for Sweep
DEFAULT_CONFIG_FILE = '../../sweep.yaml'
DEFAULT_VERBOSITY = 0
# ************************************************************************

# We set the variable 'config' as a global inside this module, so it can be read from the entire application
config = None
app = None

class Config(object):
    '''
    classdocs
    '''

    def __init__(self, filename):
        '''
        Read configuration file at relative position
        '''
        script_dir = os.path.dirname(__file__) # <-- absolute dir the script is in
        abs_file_path = os.path.join(script_dir, filename)
        with open(abs_file_path, 'r') as stream:
            config = yaml.load(stream, 
                            Loader=yaml.SafeLoader)
        self.configfile = abs_file_path
        self.config = config
        self.persist = PersistConfig(self)
        self.loadFields()
        self.loadStatus()
        self.printConfiguration()

    def printConfiguration(self):
        '''
        Write configuration to console.
        '''
        global app
        inputmode = self.loadingMode()
        if inputmode == 'jira':
            inputmode += " (" + self.config['jira']['server']+")"
        elif inputmode == 'database':
            inputmode += " (SQLite3 file: "+self.getDatabasePath()+")"

        app.console("Configuration:", 0)
        app.console("* Reading configuration from: %s (%s)" % (self.configfile,os.path.normpath(os.path.abspath(self.configfile))), 0)
        app.console("* Portfolio: %s" % (self.getPortfolio(),), 0)
        app.console("* Input mode: %s" % (inputmode,), 0)
        app.console("* Loaded fields: %s" % (", ".join(self.fields.keys()),), 2)
        app.console("* Loaded statuses: %s" % (", ".join(self.statuses),), 0)
        app.console("* Loaded plugins: %s" % ", ".join(self.config['plugins']['sections'].keys()), 0)
        app.console("* Report directory: %s" % (self.getReportDirectory(),), 0)

    def getPlugins(self):
        d = self.config['plugins']['sections']
        lst = []
        for k in d.keys():
            lst.append(dict(cname=k, title=d[k]['title']))
        return lst

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

    def getDatabasePath(self):
        filename = self.config['database']['filename']
        path = self.config['database']['path']
        return os.path.join(path, filename)

    def getDatabase(self):
        '''
        Get a database connection
        '''
        return sqlite3.connect(self.getDatabasePath())

    def loadFields(self):
        if self.loadingMode() == 'database':
            self.fields = self.persist.loadConfig("fields")
        else:
            self.fields = {}
            all_fields = self.getAtlassianJira().get_all_fields()
            for f in all_fields:
                self.fields[f['id']] = f
            self.persist.saveConfig(key="fields", updated=None, configdata=self.fields)

    def loadStatus(self, project_id="PLAN", issuetype="Story"):
        '''Hardcoded for now to get statuses for project PLAN and issuetype Story'''
        if hasattr(self, 'statuses'):
            return self.statuses
        else:
            res = []
            lst = self.getAtlassianJira().get_status_for_project(project_id)
            for a in lst:
                if a['name'] == issuetype:
                    res = list(map(lambda x: x['name'], a['statuses']))
                    self.statuses = res
                    break
            return res

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

class App(object):
    '''
    Application singleton.
    '''
    def __init__(self, verbosity=0):
        self.verbosity = verbosity

    def console(self,message,level=0):
        '''
        Log to console, depending on verbosity
        '''
        if level <= self.verbosity:
            print(message)
    

if __name__ == '__main__':
    c = Config(None)
