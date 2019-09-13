'''
Created on Sep 11, 2019

@author: cjr
'''
from Config import Config
from jinja2 import Environment, PackageLoader, select_autoescape

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
            autoescape=select_autoescape(['html', 'xml'])
        )

    def reportDetails(self, initiative):
        '''
        Create a report for one initiative
        '''
        template = self.env.get_template('details.html')
        f = open('report-%s.html' % initiative.key,'w')
        f.write(template.render(issue=initiative))
        f.close()

    def reportOverview(self, lst):
        '''
        Create a report showing an overview of initiatives
        '''
        template = self.env.get_template('overview.html')
        f = open('report-overview.html','w')
        f.write(template.render(issues=lst))
        f.close()
        
if __name__ == '__main__':
    config = Config('sweep.yaml')
    reportService = ReportService(config)
