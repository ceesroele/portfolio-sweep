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
import sys
import os

import Config

def main(**kwargs):
    with_reporting = True
    if sys.argv and sys.argv[0] == "manage.py":
        # Started from Django: $ python3 manage.py runserver
        args = {'config': Config.DEFAULT_CONFIG_FILE, 'verbose': Config.DEFAULT_VERBOSITY}
        with_reporting = False
    else:
        # Started from command line: $ python3 Start.py
        default_args = getParser().parse_args()
        args = default_args.__dict__
        args.update(kwargs)

    start = datetime.datetime.now()
    # Read configuration and set 'config' to a global in the Config module so it is available to all of the application
    Config.app = Config.App(verbosity=args['verbose'])
    Config.config = Config.Config(args['config'])
    
    portfolio = PortfolioService(Config.config)
    Config.app.portfolioData = portfolio.loadPortfolio()

    print("--- portfolio ---")
    for initiative in Config.app.portfolioData.traverse():
        print("* Initiative: "+str(initiative))
        print("- No epics" if not initiative.traverse() else "- Epics:")
        for epic in initiative.traverse():
            print("-- " + str(epic))
    print("-----------------")

    if with_reporting:
        report = ReportService(Config.config)
        startReporting = datetime.datetime.now()
        # Portfolio overview
        report.portfolioOverview(Config.app.portfolioData)

        # Report details on each Initiative
        for v in Config.app.portfolioData.traverse():
            report.reportDetails(v)

        report.copy_static_files()

        print("Reporting time: %s" % (datetime.datetime.now()-startReporting))
    
    end = datetime.datetime.now()
    print("\nRuntime %s" % (end-start))

def getParser():
    '''
    Create a parser for command line configuration parameters
    '''
    parser = argparse.ArgumentParser(description='Sweep Portfolio data from Jira')
    parser.add_argument('--config', '-c',
                        default=Config.DEFAULT_CONFIG_FILE,
                        help='Location of configuration file'
                        )
    parser.add_argument("--verbose", "-v", help="Increase output verbosity",
                    choices=[0, 1, 2], type=int, default=Config.DEFAULT_VERBOSITY)
    return parser

if __name__ == '__main__':
    main()
