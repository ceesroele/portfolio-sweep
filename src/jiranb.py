
import Config
from service.PortfolioService import jira2DataObject
import pandas as pd
from data.QueryFrame import QueryFrame
from service.PortfolioService import Persist

class jiranb(object):
    def __init__(self):
        # Read configuration and set 'config' to a global in the Config module so it is available to all of the application
        Config.app = Config.App(verbosity=Config.DEFAULT_VERBOSITY)
        Config.config = Config.Config(Config.DEFAULT_CONFIG_FILE)
        Config.persist = Persist(Config.config)
        self.statuses = Config.config.statuses

    def jql(self, s, persist=False, errors=False):
        """
        :param s: jql query to be passed to JIRA
        :param persist: if True, cache the result
        :param errors: if True, show python exception in case of errors. if False, show error in jql only
        :return: QueryFrame with result of jql query
        """
        return QueryFrame(s)

    def fields(self, shortlist=True, columns=None):
        """
        Return a dataframe with JIRA configuration on fields.
        :param shortlist: If True return most relevant subset of columns. If False, return all. Default True.
        :param columns: List of columns to restrict result to. Default None.
        :return:
        """
        shortlist_keys = ['key', 'name', 'schema']
        regular_keys = ['id', 'key', 'name', 'custom', 'orderable', 'navigable', 'searchable']
        d = {}
        for rk in regular_keys:
            d[rk] = []
        d['clauseNames'] = []
        d['schema'] = []
        for f in Config.config.fields.values():
            for rk in regular_keys:
                d[rk].append(f[rk])
            schema = None
            if 'schema' in f:
                schema = str(f['schema'])
            d['schema'].append(schema)
            clauseNames = None
            if 'clauseNames' in f:
                clauseNames = str(f['clauseNames'])
            d['clauseNames'].append(clauseNames)
        df = pd.DataFrame(d)
        if shortlist and not columns:
            df = df[shortlist_keys]
        elif columns:
            df = df[columns]
        return df

