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
import traceback
from flask_table import Table, Col
from collections import OrderedDict

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
        res = None
        try:
            res = self.goDoit()
        except Exception as err:
            print("%s" % (err,))
            traceback.print_tb(err.__traceback__)
            print("Ignoring this exception and continuing")
        end = datetime.datetime.now()
        print("\nRuntime for '%s': %s" % (self.title, end-start))
        return res
    def createTable(self,headers=None,values=None):
        # headers = list(map(lambda x: '<b>'+x+"</b>", headers))
        # fig = go.Figure(data=[go.Table(
        #         header = dict(
        #         values = headers,
        #         line_color='darkslategray',
        #         fill_color='royalblue',
        #         align=['left','center'],
        #         font=dict(color='white', size=12),
        #         height=40
        #         ),
        #         cells=dict(
        #         values=values,
        #         line_color='darkslategray',
        #         fill=dict(color=['paleturquoise', 'white']),
        #         align=['left', 'left'],
        #         font_size=12,
        #         height=30)
        #         )
        #     ])
        # presult = plotly.offline.plot(fig, config={"displayModeBar": False},
        #                                   show_link=False,
        #                                   include_plotlyjs=False,
        #                                   output_type='div')
        # return presult
        if headers and values:
            lst = []
            for v in values:
                item = {}
                for key, value in zip(headers, v):
                    item[key] = value
                lst.append(item)
            table = DynamicTable(lst)
            table.set_headers(headers)
            return table.__html__()

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
    
    def createAreaLineChart(self, xs=[], ys=[], labels=[], title=None):
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
            cumulative_ys = make_cumulative(ys)
            maxvalue = 0
            is_first = True
            for (x, y, label) in zip(xs, cumulative_ys, labels):
                if x and y:
                    maxvalue = max(maxvalue, max(y)+1)
                    if is_first:
                        fill = 'tozeroy'
                        is_first = False
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
            for (x, y, label) in zip(xs, ys, labels):
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
    '''Create a table with Initiative key/value details'''
    def goDoit(self):
        '''
        For now, only 'initiative' argument is NotImplemented
        '''
        values = list(map(lambda x, y: (Config.config.fields[x]['name'], y),
                          self.initiative.dict().keys(), self.initiative.dict().values()))
        details_table = self.createTable(headers=['Attribute', 'Value'], values=values)
        res = dict(
            title=self.title,
            post=details_table
            )
        return res        


class IssuesPlugin(AbstractPlugin):
    '''Create a table with an overview of the issues of the Initiatve'''
    def goDoit(self):
        values = []
        for iss in self.initiative.traverse_recursive():
            l = ""
            if iss.issuelinks:
                d = iss.links()
                inwards = d['inwards']
                outwards = d['outwards']
                if inwards:
                    l += "inward: "
                    l += ", ".join(map(lambda x: jiraLink(x[0],title=x[1]),inwards))
                if outwards:
                    l += "outward: "
                    l += ", ".join(map(lambda x: jiraLink(x[0],title=x[1]),outwards))
            values.append((iss.key, iss.summary, iss.issuetype, iss.status, l))

        issues_table = self.createTable(headers=['Key', 'Summary', 'Type', 'Status', 'Links'], values=values)
        res = dict(
            title=self.title,
            post=issues_table
            )
        return res

class IssueTypesPlugin(AbstractPlugin):
    def goDoit(self):
        issuetypes = {}
        all_issues = self.initiative.traverse_recursive(withepics=True)
        for iss in all_issues:
                itype = iss.issuetype
                if itype in issuetypes.keys():
                    issuetypes[itype] = issuetypes[itype] + 1
                else:
                    issuetypes[itype] = 1

        piechart = self.createPieChart(labels=list(issuetypes.keys()),values=list(issuetypes.values()), title="Issue types")
        res = dict(title=self.title, post=piechart)
        return res
    

class TreeMapPlugin(AbstractPlugin):
    '''
    Create a treemap with the structure of the initiative
    '''
    def goDoit(self):
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
        all_issues = self.initiative.traverse_recursive(lambda x: str(x.issuetype) == "Task")
        closing_dates = []

        if all_issues:
            # FIXME: "bucket" currently does nothing other than make 'cumulative' function available
            bucket = TimeBucket(Config.config, all_issues)
            xs = []
            ys = []

            period = Period()
            created_match = lambda x: x.created
            created_results = period.analyse_monotonic(all_issues, created_match)
            linedict = bucket.cumulative(created_results)
            x1 = list(linedict.keys())
            y1 = list(linedict.values())
            xs.append(x1)
            ys.append(y1)
            label1 = "created"

            # function to determine the date at which the issue is closed
            def closingmatch(issue):
                closingDate = issue.statusChangedTo('Done')
                if closingDate:
                    return jiraDate2Datetime(closingDate)

            closing_results = period.analyse_monotonic(all_issues, closingmatch)
            # Create a second line map for closed issues
            label2 = "closed"
            if closing_results:
                nextlinedict = bucket.cumulative(closing_results)
                # in python, keys() and values() for a dictionary come in the same order
                x2 = list(nextlinedict.keys())
                y2 = list(nextlinedict.values())
                xs.append(x2)
                ys.append(y2)

            line_map = self.createMultiLineMap(xs=xs, ys=ys, labels=[label1, label2], title=self.title)
            return dict(title=self.title, post=line_map)


class CumulativeFlowPlugin(AbstractPlugin):
    def goDoit(self):
        # basic traversal
        all_issues = self.initiative.traverse_recursive()

        bucket = TimeBucket(Config.config, all_issues)
        period = Period()

        # cumulative flow diagram
        date_list = period.datelist(all_issues)

        cflowdata = {}
        for d in date_list:
            cflowdata[d] = {}
            for iss in all_issues:
                st = iss.statusAtDate(d)
                if st is not None:
                    if st not in list(cflowdata[d].keys()):
                        cflowdata[d][st] = 1
                    else:
                        cflowdata[d][st] = cflowdata[d][st] + 1

        def group_function(issue, d):
            return issue.statusAtDate(d)

        (allgroups, cflowdata) = period.analyse_group(all_issues, date_list, group_function)
        newlabels = []
        xs = []
        ys = []
        for g in allgroups:
            newlabels.append(g)
            xs.append(date_list)
            res_for_group = []
            for d in date_list:
                res_for_group.append(cflowdata[d][g])
            ys.append(res_for_group)
        cumulative_flow_chart = self.createAreaLineChart(xs=xs, ys=ys,
                                                       labels=newlabels, title="Cumulative Flow")
        res = dict(title=self.title, post=cumulative_flow_chart)
        return res

class DynamicTable(Table):
    def set_headers(self, headers):
        self.headers = headers
        lst = []
        for h in headers:
            setattr(self, h, Col(h))
            lst.append((h, getattr(self, h)))
        self._cols = OrderedDict()
        # Then add the columns from this class.
        this_cls_cols = sorted(lst, key=lambda x: x[1]._counter_val)
        self._cols.update(OrderedDict(this_cls_cols))


def make_cumulative(lst):
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
