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

from Config import Config

if __name__ == '__main__':
    start = datetime.datetime.now()
    config = Config('../../sweep.yaml')
    print("Portfolio: "+config.getPortfolio())
    print("Loading mode: "+config.loadingMode())
    config.loadFields()
    portfolio = PortfolioService(config)
    report = ReportService(config)
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
        