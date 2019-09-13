'''
Created on Aug 15, 2019

check out: https://towardsdatascience.com/communication-story-from-an-issue-tracking-software-efbbf29736ff
https://qxf2.com/blog/python-jira-analyze-engineering-metrics/
https://pypi.org/project/jira-metrics-extract/
@author: cjr
'''
from service.PortfolioService import PortfolioService
from service.ReportService import ReportService

from Config import Config

if __name__ == '__main__':
    config = Config('../../sweep.yaml')
    portfolio = PortfolioService(config)
    report = ReportService(config)
    issues = portfolio.load()
    
    # Report overview
    report.reportOverview(issues)
    
    # Report details on each Initiative
    for v in issues:
        report.reportDetails(v)
        