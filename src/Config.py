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
import importlib
import re
import inspect

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
        self.check_configuration()

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
        app.console("* Loaded plugins: %s" % ", ".join(app.plugin_modules.keys()), 0)
        app.console("* Configured plugins: %s" % ", ".join(self.config['plugins']['sections'].keys()), 0)
        app.console("* Report directory: %s" % (self.getReportDirectory(),), 0)

    def check_configuration(self):
        # check if all configured plugins are actually available
        configured_plugins = list(map(lambda x: x['cname'], self.getPlugins()))
        for cp in configured_plugins:
            if cp not in app.plugin_modules.keys():
                app.error("Configured plugin '%s' is not available. Check configured and available plugins" % cp)

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

    Provides simple colored console messages that may not work on all platforms.
    Alternatively: https://github.com/tartley/colorama
    '''
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    def __init__(self, verbosity=0):
        '''Load all plugin classes'''
        self.verbosity = verbosity
        self.plugin_modules = self.load_plugins()

    def load_plugins(self):
        '''Load all available plugins and return them as a dictionary {'<classname>': <class>}'''
        pdict = {}
        # Define, call, and add results for each plugin
        script_dir = os.path.dirname(__file__) # <-- absolute dir the script is in

        # Get plugins from the plugin/custom directory (each plugin in its own module with the same name)
        abs_file_path = os.path.join(script_dir, "plugin/custom")
        for p in filter(lambda x: re.match(".*Plugin.py", x),  os.listdir(abs_file_path)):
            cname = p[0:-3]
            module_name = "plugin.custom.%s" % cname
            module = importlib.import_module(module_name)
            if hasattr(module, cname):
                pdict[cname] = getattr(module, cname)
            else:
                raise AttributeError("Failed to find class '%s' in module '%s'" % (cname, module_name))

        # Now checking standard plugins
        module_name = "plugin.Plugin"
        module = importlib.import_module(module_name)
        for cname, class_ in inspect.getmembers(module, inspect.isclass):
            if re.match(".*Plugin", cname):
                pdict[cname] = class_

        return pdict

    def get_plugin(self, cname):
        if cname in self.plugin_modules.keys():
            return self.plugin_modules[cname]
        else:
            raise ModuleNotFoundError("Failed to find configured plugin '%s'. Check your configuration!" % cname)

    def console(self, message, level=0):
        '''
        Log to console, depending on verbosity
        '''
        if level <= self.verbosity:
            print(message)

    def warning(self, message):
        '''
        Log warning to console.
        '''
        print("%sWarning: %s%s" % (self.WARNING, message, self.ENDC))

    def error(self, message):
        '''
        Log error to console.
        '''
        print("%sError: %s%s" % (self.FAIL, message, self.ENDC))


if __name__ == '__main__':
    c = Config(None)
