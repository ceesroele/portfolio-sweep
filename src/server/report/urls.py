from django.urls import path, re_path
from django.views.generic.base import RedirectView

from . import views

urlpatterns = [
    # '' or 'portfolio.html'
    path('', views.index, name='index'),
    re_path(r'portfolio.html/?$', RedirectView.as_view(url='/report/', permanent=False), name='index'),
    # ex: /report/PORT-9/
    path('report-<str:initiative_key>.html/', views.initiative, name='initiative'),
    re_path(r'static/(?P<filename>[a-zA-Z.]+)/?$', views.static, name='static')
    ]
