'''
Created on Sep 11, 2019

@author: cjr
'''
import Config
from jinja2 import Environment, PackageLoader
import plotly.graph_objects as go
import plotly.offline
from service.BucketService import TimeBucket, Period
from data.JiraObjectData import jiraDate2Datetime
import datetime
from pathlib import Path
from plugin.Plugin import DetailsPlugin, IssuesPlugin, IssueTypesPlugin, TreeMapPlugin, CumulativeFlowPlugin, BurnupPlugin
import importlib

class ReportService(object):
    '''
    Create reports
    '''


    def __init__(self, config):
        '''
        Constructor
        '''
        self.env = Environment(
            loader=PackageLoader('service','web'),
            autoescape=False)
#            autoescape=select_autoescape(['html', 'xml'])
#        )

    def reportDetails(self, initiative):
        '''
        Create a report for one initiative
        '''
        meta = dict(
            title=initiative.summary,
            timestamp=datetime.datetime.now()
            )
        # posts is a list of entries (dictionaries) where each entry can consist of:
        #   title (mandatory)
        #   link
        #   subtitle
        #   post (mandatory)
        #   morelink
        posts = []
        
        # Define, call, and add results for each plugin
        module_name = "plugin.Plugin"
        plugin_classes = Config.config.getPlugins()
        module = importlib.import_module(module_name)
        for p in plugin_classes:
            cname = p['cname']
            title = p['title']
            class_ = getattr(module, cname)
            instance = class_(title=title, initiative=initiative)
            posts.append(instance.go())

        template = self.env.get_template('details.html')
        self.writeTemplate(
            'report-%s.html' % initiative.key,
            template.render(
                issue=initiative,
                meta=meta,
                posts=posts
                )
            )

    def portfolioOverview(self, portfolioData):
        '''
        Create a report for the portfolio
        '''
        template = self.env.get_template('overview.html')
        meta = dict(
            title='Portfolio',
            timestamp=datetime.datetime.now()
            )
        self.writeTemplate(
            "portfolio", 
            template.render(issues=portfolioData.traverse(),meta=meta)
            )
        

    def writeTemplate(self,filename,text):
        dirname = Config.config.getReportDirectory()
        suffix = ".html"
        path = Path(dirname, filename).with_suffix(suffix)
        f = open(path,'w')
        f.write(text)
        print(path.as_uri())
        f.close()

    def reportOverview(self, lst):
        '''
        Create a report showing an overview of initiatives
        '''
        template = self.env.get_template('overview.html')
        self.writeTemplate(
            "report-overview",
            template.render(issues=lst)
            )