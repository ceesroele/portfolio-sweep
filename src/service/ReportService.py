'''
Created on Sep 11, 2019

@author: cjr
'''
from Config import Config
from jinja2 import Environment, PackageLoader
import plotly.graph_objects as go
import plotly.offline
from service.BucketService import TimeBucket, Period
from data.JiraObjectData import jiraDate2Datetime, jiraLink
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

        # Create a table with Initiative key/value details
        ks = []
        vs = []
        for (k,v) in initiative.dict().items():
            ks.append(self.config.fields[k]['name'])
            vs.append(v)
        values = [ks,vs]
        details_table = self.createTable(headers=['Attribute','Value'],values=values)
        posts.append(dict(title="Project details",post=details_table))


        # Create a treemap with the structure of the initiative
        ls = [initiative.key]
        ps = [""]
        vs = [30]
        all_issues = []
        closing_dates = []
        issuetypes = {}
        for epic in initiative.traverse():
            if ("Epic" in issuetypes.keys()):
                issuetypes["Epic"] = issuetypes["Epic"] + 1
            else:
                issuetypes["Epic"] = 1
            ls.append(epic.key)
            ps.append(initiative.key)
            vs.append(10)
            for iss in epic.traverse():
                itype = iss.issuetype
                if itype in issuetypes.keys():
                    issuetypes[itype] = issuetypes[itype] + 1
                else:
                    issuetypes[itype] = 1

                ls.append(iss.key)
                ps.append(epic.key)
                all_issues.append(iss)
                defaultHours = 1
                if iss.timeoriginalestimate is not None:
                    # we want hours
                    hours = iss.timeoriginalestimate / 3600
                    if hours >= 1:
                        vs.append(int(hours))
                    else:
                        vs.append(defaultHours)
                vs.append(defaultHours)
                changelog = iss.changelog

                for history in changelog.histories:
                    for item in history.items:
                        if item.field == 'status':
                            #print('Date:' + history.created + ' From:' + item.fromString + ' To:' + item.toString)
                            pass
                #print("Status %s" % (iss.status))
                if iss.status == 'Done':
                    #print("%s was closed on %s" % (iss.key, iss.statusChangedTo('Done')))
                    closingDate = iss.statusChangedTo('Done')
                    if closingDate:
                        closing_dates.append(jiraDate2Datetime(closingDate))
        tree_map = self.createTreeMap(labels=ls,parents=ps,values=vs)
        posts.append(dict(title="Treemap with estimations",post=tree_map))
        
        period = Period()
        results = period.analyse(all_issues)
        
        # cumulative flow diagram
        if all_issues:
            lst = period.datelist(all_issues)
            cflowdata = {}
            for d in lst:
                cflowdata[d] = {}
                for iss in all_issues:
                    #print("%s  %s  -> %s" % (iss.key, d, iss.statusAtDate(d)))
                    st = iss.statusAtDate(d)
                    if st is not None:
                        if st not in list(cflowdata[d].keys()):
                            cflowdata[d][st] = 1
                        else:
                            cflowdata[d][st] = cflowdata[d][st] + 1
            #pprint.pprint(cflowdata)
            
            ys = []
            timelinedates = list(cflowdata.keys())
            timelinedates.sort()
            backlog = []
            selectedfordevelopment = []
            inprogress = []
            done = []
            labels = ['Backlog', 'Selected for Development', 'In Progress', 'Done']
            xs = [timelinedates, timelinedates, timelinedates, timelinedates]
            for d in timelinedates:
                # hardcoded statuses
                backlog.append(0 if not 'Backlog' in cflowdata[d] else cflowdata[d]['Backlog'])
                selectedfordevelopment.append(0 if not 'Selected for Development' in cflowdata[d] else cflowdata[d]['Selected for Development'])
                inprogress.append(0 if not 'In Progress' in cflowdata[d] else cflowdata[d]['In Progress'])
                done.append(0 if not 'Done' in cflowdata[d] else cflowdata[d]['Done'])
            cumulativeflowchart = self.createAreaLineChart(xs=xs, ys=[backlog,selectedfordevelopment,inprogress,done], labels=labels, title="Cumulative Flow")
            posts.append(dict(title="Cumulative Flow Chart", post=cumulativeflowchart))

        
        bucket = TimeBucket(self.config, all_issues)
        bucket.allocate(None)
        linedict = bucket.cumulative(results)
        
        xs = []
        ys = []
        labels = []
        x1 = list(linedict.keys())
        x1.sort()
        y1 = []
        for k in x1:
            y1.append(linedict[k])
        if x1 and y1:
            xs.append(x1)
            ys.append(y1)
            labels.append("created")
            
        
        # Create a second line map for closed issues
        if closing_dates:
            closing_dates.sort()
            res = period.analyse_dates(closing_dates)
            nextlinedict = bucket.cumulative(res)
            x2 = list(nextlinedict.keys())
            y2 = []
            for k in x2:
                y2.append(nextlinedict[k])
            xs.append(x2)
            ys.append(y2)
            labels.append("closed")
        
        if xs and ys:
            line_map = self.createMultiLineMap(xs=xs, ys=ys, labels=labels, title="Created and closed")
            posts.append(dict(title="Created and closed issues", post=line_map))
        
        if issuetypes:
            piechart = self.createPieChart(labels=list(issuetypes.keys()),values=list(issuetypes.values()), title="Issue types")
            posts.append(dict(title="Issue types", post=piechart))

        # Create a table with Initiative key/value details
        ks = []
        vs = []
        tps = []
        sts = []
        ils = []
        for iss in initiative.issues():
            ks.append(iss.jiraLink())
            vs.append(iss.summary)
            tps.append(iss.issuetype)
            sts.append(iss.status)
            
            if iss.issuelinks:
                s = ""
                d = iss.links()
                inwards = d['inwards']
                outwards = d['outwards']
                if inwards:
                    s += "inward: "
                    s += ", ".join(map(lambda x: jiraLink(x[0],title=x[1]),inwards))
                if outwards:
                    s += "outward: "
                    s += ", ".join(map(lambda x: jiraLink(x[0],title=x[1]),outwards))
                ils.append(s)
            else:
                ils.append("")
            
        values = [ks,vs,tps,sts,ils]
        issues_table = self.createTable(headers=['Key','Summary','Type','Status','Links'],values=values)
        posts.append(dict(title="All issues",post=issues_table))

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
                align=['left', 'left'],
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
        fig.update_layout(margin=dict(l=10, r=10, t=10, b=10),autosize=True)
        fig.update_yaxes(automargin=True)
        presult = plotly.offline.plot(fig, config={"displayModeBar": False}, 
                                          show_link=False,
                                          include_plotlyjs=False,
                                          output_type='div')
        return presult

    def createMultiLineMap(self,xs=[],ys=[],labels=[], title=None):
        '''
        Create line chart with multiple lines
        xs, ys, and labels are lists of lists, each representing one line
        '''
        if not ys or not xs or not labels:
            return ""
        else:
            fig = go.Figure()
            if title:
                fig.update_layout(title_text=title)
            
            maxvalue = 0
            for (x,y,label) in zip(xs,ys,labels):
                maxvalue = max(maxvalue, max(y)+1) 
                fig.add_trace(go.Scatter(
                    x=x,
                    y=y,
                    name=label
                    ))
                
            fig.update_layout(yaxis_range=[0, maxvalue], showlegend=True)
            presult = plotly.offline.plot(fig, config={"displayModeBar": False},
                                          show_link=False,
                                          include_plotlyjs=False,
                                          output_type='div')
            return presult

    def createAreaLineChart(self,xs=[],ys=[],labels=[], title=None):
        '''
        Create line chart with multiple lines
        xs, ys, and labels are lists of lists, each representing one line
        '''
        if not ys or not xs or not labels:
            return ""
        else:
            fig = go.Figure()
            if title:
                fig.update_layout(title_text=title)
            
            cumulativeys = makecumulative(ys)
            maxvalue = 0
            isFirst = True
            for (x,y,label) in zip(xs,cumulativeys,labels):
                maxvalue = max(maxvalue, max(y)+1)
                if isFirst:
                    fill = 'tozeroy'
                    isFirst = False
                else:
                    fill = 'tonexty'
                fig.add_trace(go.Scatter(
                    x=x,
                    y=y,
                    name=label,
                    fill=fill
                    ))
                
            fig.update_layout(yaxis_range=[0, maxvalue], showlegend=True)
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
        
    def createPieChart(self,labels=[], values=[], title=None):

        fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
        fig.update_layout(showlegend=True)
        presult = plotly.offline.plot(fig, config={"displayModeBar": False},
                                          show_link=False,
                                          include_plotlyjs=False,
                                          output_type='div')
        return presult
        
def makecumulative(lst):
    '''
    Make values of lists that are part of the list of lists cumulative.
    '''
    res = []
    for num, l in enumerate(lst):
        if num == 0:
            res.append(l)
        else:
            res.append(list(map(lambda x, y: x+y, res[num-1], lst[num])))
    return res
        
        
if __name__ == '__main__':
    config = Config('sweep.yaml')
    reportService = ReportService(config)
