"""
Result of JIRA query stored in one object
"""

import Config
import pandas as pd
import re
from jira.exceptions import JIRAError
from service.PortfolioService import jira2DataObject


class QueryFrame(object):
    """Data object for JIRA query results."""
    def __init__(self, jql):
        self._jql = jql
        self._issuedict = {}
        # if we have a jql, but no issues, query JIRA
        try:
            # Always ask JIRA for the list of issues
            issues = Config.config.getJira().search_issues(jql)
            # JIRA will not pass the changelog with the result of a search query, so we must get all issues individually
            # we need to upgrade the issues to include the changelog
            nissues = []
            for iss in issues:
                obj = Config.persist.load(key=iss.key)
                if obj:
                    nissues.append(obj)
                else:
                    ch_issue = Config.config.getJira().issue(iss.key, expand='changelog')
                    o_issue = jira2DataObject(ch_issue)
                    nissues.append(o_issue)
                    Config.persist.store(o_issue)
            # Find out the minimum and maximum date in the period for the query: first created, last updated
            min_created = None
            max_updated = None
            for iss in nissues:
                self._issuedict[iss.key] = iss
                c = iss['created']
                if not min_created or c < min_created:
                    min_created = c
                u = iss['updated']
                if not max_updated or u > max_updated:
                    max_updated = u
            self.issuedata = QueryFrame._issues2dataframe(nissues)
            if min_created is not None and max_updated is not None:
                self.timedata = QueryFrame._issues2time(nissues, mindate=min_created, maxdate=max_updated)
        except JIRAError as inst:
            Config.app.error(inst.args[1])

    def _issues2dataframe(issues):
        using_fields = ['key', 'status', 'summary', 'description', 'created', 'updated', 'issuetype', 'timeoriginalestimate', 'timespent', 'creator', 'reporter', 'assignee']
        d = {}
        for k in using_fields:
            d[k] = []
        for iss in issues:
            for k in using_fields:
                d[k].append(iss[k])
        df = pd.DataFrame(d)
        df.columns = using_fields
        return df

    def _issues2time(issues, mindate, maxdate):
        delta = maxdate - mindate
        days = pd.date_range(mindate.replace(hour=0, minute=0, second=0, microsecond=0), freq='D', periods=delta.days)
        d = {'date': [], 'key': [], 'status': []}
        for day in days:
            for iss in issues:
                d['date'].append(day)
                d['key'].append(iss.key)
                d['status'].append(iss.statusAtDate(day))
        df = pd.DataFrame(d)
        df.columns = ['date', 'key', 'status']
        return df

    def __repr__(self):
        return 'QueryFrame[{}]'.format(self._jql)

    def __getitem__(self, item):
        """
        If item matches the format of a key of a JIRA issue, return that issue.
        Otherwise pass on the argument to the issuedata dataframe
        """
        # Allow for case independent entry of JIRA issue keys.
        if isinstance(item, str) and re.fullmatch('[A-Z]+-[0-9]+', item):
            if item in self._issuedict:
                return self._issuedict[item]
            else:
                Config.app.error('Failed to find JIRA issue key {} in query result'.format(item))
        else:
            try:
                return self.issuedata[item]
            except KeyError as k:
                if isinstance(item, str) and re.fullmatch('[a-zA-Z]+-[0-9]+', item):
                    Config.app.error('If you tried to enter a JIRA issue key, enter in UPPERCASE only!')
                raise k

    # For Jupyter default 'pretty' output of object
    # See: https://ipython.readthedocs.io/en/stable/api/generated/IPython.lib.pretty.html
    def IGNORE_repr_pretty_(self, p, cycle):
        p.pretty('hello, pretty world!')

    def __str__(self):
        return 'QueryFrame({})'.format(self._jql)

    # For Jupyter default HTML output of object
    # See: https://ipython.readthedocs.io/en/stable/api/generated/IPython.display.html
    # Now we return the primary dataframe with data on issues
    def _repr_html_(self):
        return self.issuedata.to_html()


