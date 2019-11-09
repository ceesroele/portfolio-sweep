'''
Created on Nov 6, 2019

@author: cjr
'''
import Config
import plotly.graph_objects as go
import plotly.offline
from data.JiraObjectData import jiraLink, jiraDate2Datetime
from service.BucketService import TimeBucket, Period
import datetime

class AbstractPlugin(object):
    '''
    classdocs
    '''
    def __init__(self,title="", initiative=None,issues=[]):
        self.title = title
        self.initiative = initiative
        self.issues = issues
    
    def go(self):
        start = datetime.datetime.now()
        res = self.goDoit()
        end = datetime.datetime.now()
        print("\nRuntime for '%s': %s" % (self.title, end-start))
        return res
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

    def createPieChart(self,labels=[], values=[], title=None):
        fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
        fig.update_layout(showlegend=True)
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
    def __str__(self):
        return "This is a %s plugin for %s" % (type(self).__name__, self.initiative.key)

        

class DetailsPlugin(AbstractPlugin):
    def goDoit(self):
        '''
        For now, only 'initiative' argument is NotImplemented
        '''
                # Create a table with Initiative key/value details
        ks = []
        vs = []
        for (k,v) in self.initiative.dict().items():
            ks.append(Config.config.fields[k]['name'])
            vs.append(v)
        values = [ks,vs]
        details_table = self.createTable(headers=['Attribute','Value'],values=values)
        res = dict(
            title=self.title,
            post=details_table
            )
        return res        


class IssuesPlugin(AbstractPlugin):
    
    def goDoit(self):
         # Create a table with Initiative key/value details
        ks = []
        vs = []
        tps = []
        sts = []
        ils = []
        for iss in self.initiative.issues():
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
        res = dict(
            title=self.title,
            post=issues_table
            )
        return res

class IssueTypesPlugin(AbstractPlugin):
    def goDoit(self):
        issuetypes = {}
        for epic in self.initiative.traverse():
            if ("Epic" in issuetypes.keys()):
                issuetypes["Epic"] = issuetypes["Epic"] + 1
            else:
                issuetypes["Epic"] = 1
            for iss in epic.traverse():
                itype = iss.issuetype
                if itype in issuetypes.keys():
                    issuetypes[itype] = issuetypes[itype] + 1
                else:
                    issuetypes[itype] = 1

        piechart = self.createPieChart(labels=list(issuetypes.keys()),values=list(issuetypes.values()), title="Issue types")
        res = dict(title=self.title, post=piechart)
        return res
    

class TreeMapPlugin(AbstractPlugin):
    def goDoit(self):
                # Create a treemap with the structure of the initiative
        ls = [self.initiative.key]
        ps = [""]
        vs = [30]
        all_issues = []
        for epic in self.initiative.traverse():
            ls.append(epic.key)
            ps.append(self.initiative.key)
            vs.append(10)
            for iss in epic.traverse():
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
        tree_map = self.createTreeMap(labels=ls,parents=ps,values=vs)
        res = dict(
            title=self.title,
            post=tree_map
            )
        return res
    
    
class BurnupPlugin(AbstractPlugin):
    def goDoit(self):
        all_issues = []
        closing_dates = []
        for epic in self.initiative.traverse():
            for iss in epic.traverse():
                all_issues.append(iss)
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

        period = Period()
        results = period.analyse(all_issues)
                
        bucket = TimeBucket(Config.config, all_issues)
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
        
        line_map = self.createMultiLineMap(xs=xs, ys=ys, labels=labels, title=self.title)
        return dict(title=self.title, post=line_map)

class CumulativeFlowPlugin(AbstractPlugin):
    def goDoit(self):
                # basic traversal
        all_issues = []
        for epic in self.initiative.traverse():
            for iss in epic.traverse():
                all_issues.append(iss)

        period = Period()
        
        # cumulative flow diagram
        lst = period.datelist(all_issues)
        cflowdata = {}
        for d in lst:
            cflowdata[d] = {}
            for iss in all_issues:
                st = iss.statusAtDate(d)
                if st is not None:
                    if st not in list(cflowdata[d].keys()):
                        cflowdata[d][st] = 1
                    else:
                        cflowdata[d][st] = cflowdata[d][st] + 1
            
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
        res = dict(title=self.title, post=cumulativeflowchart)
        return res


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
