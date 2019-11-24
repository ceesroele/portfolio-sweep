from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
import datetime
import sys


def index(request):
    '''Portfolio: overview of all initiatives'''
    print(sys.path)
    from service.ReportService import ReportService
    import Config
    report = ReportService(Config.config)
    startReporting = datetime.datetime.now()
    # Portfolio overview
    text = report.portfolioOverview(Config.app.portfolioData)

    return HttpResponse(text)

def initiative(request, initiative_key):
    print("resulting page for initiative %s" % initiative_key)
    from service.ReportService import ReportService
    from service.PortfolioService import PortfolioService
    import Config
    portfolio = PortfolioService(Config.config)
    initiative_data = portfolio.get(initiative_key)
    report = ReportService(Config.config)
    print(initiative_data.__dict__)
    text = report.reportDetails(initiative_data)
    return HttpResponse(text)

def static(request, filename):
    '''Serve static file.
    Note: not using Django facilities as static file must also be available from jinja2 template
    when the application is run from command line
    '''
    print("Got a request for %s" % filename)
    from service.ReportService import ReportService
    import Config
    report = ReportService(Config.config)
    template = report.env.get_template('static/%s' % filename)
    print(template.render())
    return HttpResponse(template.render(), "text/css")
