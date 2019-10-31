'''
Created on Sep 11, 2019

@author: cjr
'''
from Config import Config
from jinja2 import Environment, PackageLoader, select_autoescape
import plotly.graph_objects as go
import plotly.offline
import os
from service.BucketService import TimeBucket, Period
from data.JiraObjectData import jiraDate2Datetime
import datetime
from pathlib import Path

class ReportService(object):
    '''
    Create reports
    '''


    def __init__(self, config):
        '''
        Constructor
        '''
        self.config = config
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
            title=initiative.jiraIssue.fields.summary,
            timestamp=datetime.datetime.now()
            )
        
        # posts is a list of entries (dictionaries) where each entry can consist of:
        #   title (mandatory)
        #   link
        #   subtitle
        #   post (mandatory)
        #   morelink
        posts = []

        # Create a table with Initiative key/value details
        ks = []
        vs = []
        for (k,v) in initiative.dict().items():
            ks.append(self.config.fields[k]['name'])
            vs.append(v)
        values = [ks,vs]
        details_table = self.createTable(headers=['key','value'],values=values)
        posts.append(dict(title="title",post=details_table,link="link"))


        # Create a treemap with the structure of the initiative
        ls = [initiative.jiraIssue.key]
        ps = [""]
        vs = [30]
        all_issues = []
        closing_dates = []
        for epic in initiative.traverse():
            ls.append(epic.jiraIssue.key)
            ps.append(initiative.jiraIssue.key)
            vs.append(10)
            for iss in epic.traverse():
                ls.append(iss.jiraIssue.key)
                ps.append(epic.jiraIssue.key)
                all_issues.append(iss)
                defaultHours = 1
                if iss.jiraIssue.fields.timeoriginalestimate is not None:
                    # we want hours
                    hours = iss.jiraIssue.fields.timeoriginalestimate / 3600
                    if hours >= 1:
                        vs.append(int(hours))
                    else:
                        vs.append(defaultHours)
                vs.append(defaultHours)
                #pprint.pprint(iss.jiraIssue.__dict__)
                changelog = iss.jiraIssue.changelog

                for history in changelog.histories:
                    for item in history.items:
                        if item.field == 'status':
                            #print('Date:' + history.created + ' From:' + item.fromString + ' To:' + item.toString)
                            pass
                print("Status %s" % (iss.jiraIssue.fields.status))
                if str(iss.jiraIssue.fields.status) == 'Done':
                    print("%s was closed on %s" % (iss.jiraIssue.key, iss.statusChangedTo('Done')))
                    closingDate = iss.statusChangedTo('Done')
                    if closingDate:
                        closing_dates.append(jiraDate2Datetime(closingDate))
        tree_map = self.createTreeMap(labels=ls,parents=ps,values=vs)
        posts.append(dict(title="treemap",post=tree_map))
        
        period = Period()
        results = period.analyse(all_issues)
        
        bucket = TimeBucket(self.config, all_issues)
        bucket.allocate(None)
        linedict = bucket.cumulative(results)
        
        x = list(linedict.keys())
        x.sort()
        y = []
        for k in x:
            y.append(linedict[k])
        line_map = self.createLineMap(x=x, y=y, title=initiative.jiraIssue.fields.summary)
        posts.append(dict(title="Created issues", post=line_map))
        
        # Create a second line map for closed issues
        if closing_dates:
            closing_dates.sort()
            res = period.analyse_dates(closing_dates)
            nextlinedict = bucket.cumulative(res)
            x = list(nextlinedict.keys())
            y = []
            for k in x:
                y.append(nextlinedict[k])
            nextline_map = self.createLineMap(x=x, y=y, title="Closed issues")
        else:
            nextline_map = ""
        
        posts.append(dict(title="Closed issues", post=nextline_map))
        template = self.env.get_template('details.html')
        self.writeTemplate(
            'report-%s.html' % initiative.jiraIssue.key,
            template.render(
                issue=initiative,
                meta=meta,
                posts=posts
                )
            )
#            
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
        dirname = self.config.getReportDirectory()
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
        
    def createTable(self,headers=None,values=None):
        headers = list(map(lambda x: '<b>'+x+"</b>", headers))
        fig = go.Figure(data=[go.Table(
            columnorder = [1,2],
            columnwidth = [80,400],
            header = dict(
                values = headers,
                line_color='darkslategray',
                fill_color='royalblue',
                align=['left','center'],
                font=dict(color='white', size=12),
                height=40
                ),
            cells=dict(
                values=values,
                line_color='darkslategray',
                fill=dict(color=['paleturquoise', 'white']),
                align=['left', 'center'],
                font_size=12,
                height=30)
                )
            ])
        presult = plotly.offline.plot(fig, config={"displayModeBar": False}, 
                                          show_link=False,
                                          include_plotlyjs=False,
                                          output_type='div')
        return presult
    
    def createTreeMap(self,labels=[],parents=[],values=[]):       
        fig = go.Figure(go.Treemap(
            labels = labels,
            parents = parents,
            values = values
            ))
        presult = plotly.offline.plot(fig, config={"displayModeBar": False}, 
                                          show_link=False,
                                          include_plotlyjs=False,
                                          output_type='div')
        return presult

    def createLineMap(self,x=[],y=[],title=None):
        if not y:
            return ""
        else:
            maxvalue = max(y)+1  
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=x,
                y=y,
                name="foobar"
                ))
            if title:
                fig.update_layout(title_text=title)
            fig.update_layout(yaxis_range=[0, maxvalue], showlegend=True)
            presult = plotly.offline.plot(fig, config={"displayModeBar": False},
                                          show_link=False,
                                          include_plotlyjs=False,
                                          output_type='div')
            return presult
        
        
if __name__ == '__main__':
    config = Config('sweep.yaml')
    reportService = ReportService(config)
