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
from flask_table import Table, Col, LinkCol
from collections import OrderedDict
import pandas as pd
import math

class AbstractPlugin(object):
    '''
    classdocs
    '''
    def __init__(self, title="", initiative=None, issues=[]):
        self.title = title
        self.initiative = initiative
        self.issues = issues
        self.initiative_df = self.load_initiative_dataframe(initiative)

    def load_initiative_dataframe(self, initiative):
        '''Load a dataframe with standard information on the iniative'''
        all_issues = self.initiative.traverse_recursive(withepics=True)
        rows = []
        for iss in all_issues:
            rows.append({
                'key': iss.key,
                'issuetype': str(iss.issuetype),
                'timeoriginalestimate': iss.timeoriginalestimate,
                'timespent': iss.timespent
            })
        df = pd.DataFrame(rows, columns=['key', 'issuetype', 'timeoriginalestimate', 'timespent'])
        return df

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

    def createTable(self, table_class, headers=None,values=None):
        if headers and values:
            lst = []
            for v in values:
                item = {}
                for key, value in zip(headers, v):
                    item[key] = value
                lst.append(item)
            table = table_class(lst)
            #table.set_headers(headers)
            return table.__html__()

    def createPieChart(self, dataframe, title=None):
        labels = dataframe['issuetype'].tolist()
        values = dataframe['count'].tolist() # FIXME: now 'key' is set automatically as column name, set it manually
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

    def createMultiLineMap(self, dataframe, title=None):
        '''
        Create line chart with multiple lines
        :param dataframe contains the data of all lines, with 'data' being the key
        '''
        if dataframe.empty:
            return ""
        else:
            maxvalue = 0
            # {<column_name>: {'dates': [ ... ], 'values': [ ... ]} }
            d = {}
            for index, row in dataframe.iterrows():
                for c in dataframe.columns[1:]:
                    if isinstance(row[c], float) and not math.isnan(row[c]):
                        # get the maximum value for setting the maximum of the y-axis of the diagram
                        if row[c] > maxvalue:
                            maxvalue = row[c]
                        if c not in d.keys():
                            d[c] = {'dates': [row['date'].date()], 'values': [row[c]]}
                        else:
                            d[c]['dates'].append(row['date'].date())
                            d[c]['values'].append(row[c])

            maxvalue += 1
            fig = go.Figure()
            if title:
                fig.update_layout(title_text=title)

            for label in d.keys():
                fig.add_trace(go.Scatter(
                    x=d[label]['dates'],
                    y=d[label]['values'],
                    name=label
                ))

            fig.update_layout(yaxis_range=[0, maxvalue+1], showlegend=True)
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
        class DetailsTable(Table):
            key = Col('Attribute')
            value = Col('Value')
        values = list(map(lambda x, y: (Config.config.fields[x]['name'], y),
                          self.initiative.dict().keys(), self.initiative.dict().values()))
        details_table = self.createTable(DetailsTable, headers=['key', 'value'], values=values)
        res = dict(
            title=self.title,
            post=details_table
            )
        return res        

class AggregateDataPlugin(AbstractPlugin):
    '''Create a table with Initiative key/value details'''
    def goDoit(self):
        '''
        For now, only 'initiative' argument is NotImplemented
        '''
        class DetailsTable(Table):
            key = Col('Attribute')
            value = Col('Value')

        timeoriginalestimate = None
        if self.initiative.timeoriginalestimate:
            timeoriginalestimate = self.initiative.timeoriginalestimate

        estimated = 0
        timespent = 0
        for iss in self.initiative.traverse_recursive():
            e = iss.timeoriginalestimate
            if e is None:
                e = 0
            estimated += e
            t = iss.timespent
            if t is None:
                t = 0
            timespent += t

        values = []
        if timeoriginalestimate:
            values.append(['Original estimate', timeoriginalestimate])
        values += [['Estimate', estimated], ['Time spent', timespent]]
        details_table = self.createTable(DetailsTable, headers=['key', 'value'], values=values)
        res = dict(
            title=self.title,
            post=details_table
            )
        return res


class IssuesPlugin(AbstractPlugin):
    '''Create a table with an overview of the issues of the Initiatve'''
    def goDoit(self):
        class IssuesTable(Table):
            key = RawCol('Key')
            summary = Col('Summary')
            itype = Col('Type')
            status = Col('Status')
            links = Col('Links')
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
            values.append((iss.jiraLink(), iss.summary, iss.issuetype, iss.status, l))

        issues_table = self.createTable(IssuesTable, headers=['key', 'summary', 'itype', 'status', 'links'], values=values)
        res = dict(
            title=self.title,
            post=issues_table
            )
        return res

class IssueTypesPlugin(AbstractPlugin):
    '''Create a piechart with issue types'''
    def goDoit(self):
        # the 'groupby' column somehow gets the column name 'key'. Rename it to 'count'.
        dataframe = self.initiative_df.groupby('issuetype').count().reset_index().rename(columns={'key': 'count'})
        piechart = self.createPieChart(dataframe, title="Issue types")
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
    '''Create a burnup chart'''
    def goDoit(self):
        all_issues = self.initiative.traverse_recursive(lambda x: str(x.issuetype) == "Task")

        if all_issues:
            period = Period()
            created_match = lambda x: x.created
            created_df = period.analyse_monotonic(all_issues, created_match, field_name="created")

            # function to determine the date at which the issue is closed
            def closingmatch(issue):
                closingDate = issue.statusChangedTo('Done')
                if closingDate:
                    return jiraDate2Datetime(closingDate)

            closing_df = period.analyse_monotonic(all_issues, closingmatch, field_name="closed")
            df_total = pd.merge(created_df, closing_df, how="outer", on="date").sort_values(by='date')
            line_map = self.createMultiLineMap(df_total, title=self.title)
            return dict(title=self.title, post=line_map)


class TimeSpentPlugin(AbstractPlugin):
    '''Create a chart displaying how much time was estimated and how much as spent at the time of closing an issue.'''
    def goDoit(self):
        all_issues = self.initiative.traverse_recursive(lambda x: str(x.issuetype) == "Task")
        closing_dates = []

        if all_issues:
            period = Period()
            created_match = lambda x: x.created
            def timeestimate(issue):
                value = issue.timeoriginalestimate
                if value is None:
                    value = 0
                else:
                    # convert seconds to hours
                    value = value / 3600
                return value

            created_results_df = period.analyse_monotonic(all_issues, created_match,
                                                          valuefunction=timeestimate, field_name='estimated')
            # function to determine the date at which the issue is closed
            def closingmatch(issue):
                closingDate = issue.statusChangedTo('Done')
                if closingDate:
                    return jiraDate2Datetime(closingDate)

            def timespent(issue):
                value = issue.timespent
                if value is None:
                    value = 0
                else:
                    # convert seconds to hours
                    value = value / 3600
                return value

            closing_results_df = period.analyse_monotonic(all_issues, closingmatch, valuefunction=timespent, field_name="timespent")

            timeoriginalestimate = self.initiative.timeoriginalestimate
            rows = []
            df_total = pd.merge(created_results_df, closing_results_df, how="outer").sort_values(by='date')
            if timeoriginalestimate is not None:
                # If a time is estimated at the initiative level - estimate for the whole project -
                # it is drawn from the first date to the last date.
                t = timeoriginalestimate / 3600
                rows.append({'date': df_total.date.min(), 'total estimate': t})
                rows.append({'date': df_total.date.max(), 'total estimate': t})
            estimate_df = pd.DataFrame(rows, columns=['date', 'total estimate'])
            df_total = pd.merge(df_total, estimate_df, how="outer").sort_values(by='date')
            line_map = self.createMultiLineMap(df_total, title=self.title)
            return dict(title=self.title, post=line_map)


class CumulativeFlowPlugin(AbstractPlugin):
    '''Create a cumulative flow diagram'''
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


class RawCol(Col):
    """Class that will just output whatever it is given and will not
    escape it.
    """
    def td_format(self, content):
        return content


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
