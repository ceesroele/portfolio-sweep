'''
Created on Aug 15, 2019

check out: https://towardsdatascience.com/communication-story-from-an-issue-tracking-software-efbbf29736ff
https://qxf2.com/blog/python-jira-analyze-engineering-metrics/
https://pypi.org/project/jira-metrics-extract/
@author: cjr
'''
from service.PortfolioService import PortfolioService
from service.ReportService import ReportService
 
import datetime
import argparse

import Config

DEFAULT_CONFIGURATION_FILE = "../../sweep.yaml"

def main(**kwargs):
    print("Using configuration file: %s" % (kwargs['config'],))
    print("config = %s" % (kwargs['config']))
    start = datetime.datetime.now()
    # Read configuration and set 'config' to a global in the Config module so it is available to all of the application
    Config.config = Config.Config(kwargs['config'])
    
    portfolio = PortfolioService(Config.config)
    report = ReportService(Config.config)
    portfolioData = portfolio.loadPortfolio()

    print("--- portfolio ---")
    for initiative in portfolioData.traverse():
        print("* Initiative: "+str(initiative))
        print("- No epics" if not initiative.traverse() else "- Epics:")
        for epic in initiative.traverse():
            print("-- " + str(epic))
    print("-----------------")
    
    startReporting = datetime.datetime.now()
    # Portfolio overview
    report.portfolioOverview(portfolioData)
    
    # Report overview
    #report.reportOverview(issues)
    
    # Report details on each Initiative
    for v in portfolioData.traverse():
        report.reportDetails(v)
    print("Reporting time: %s" % (datetime.datetime.now()-startReporting,))
    
    end = datetime.datetime.now()
    print("\nRuntime %s" % (end-start,))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Sweep Portfolio data from Jira')
    parser.add_argument('--config', '-c',
                        default=DEFAULT_CONFIGURATION_FILE,
                        help='Location of configuration file'
                        )

    args = parser.parse_args()
    main(**args.__dict__)