'''
Created on Aug 12, 2019

@author: cjr
'''
import plotly.graph_objects as go

class BurnupChart:
    def __init__(self, title, xaxis_title, yaxis_title):
        self.title = title
        self.xaxis_title = xaxis_title
        self.yaxis_title = yaxis_title
        self.fig = go.Figure()
        
    def add_trace(self,month,vals,name,line):
        self.fig.add_trace(go.Scatter(x=month,y=vals,name=name,line=line))
        
    def __str__(self):
        return self.name
    
    def to_html(self,filename):
            self.fig.update_layout(title=self.title,
                   xaxis_title=self.xaxis_title,
                   yaxis_title=self.yaxis_title)
            html_string = self.fig.to_html()
            f = open(filename,'w')
            f.write(html_string)
            f.close()


if __name__ == '__main__':
    # Add data
    ##month = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
    ##     'August', 'September', 'October', 'November', 'December']
    month = ['2018-01-01','2018-01-10','2018-01-20','2018-02-01','2018-02-10','2018-02-20',
             '2018-06-01','2018-06-30','2018-10-01','2018-11-01','2018-12-01','2019-02-5']
    high_2000 = [32.5, 37.6, 49.9, 53.0, 69.1, 75.4, 76.5, 76.6, 70.7, 60.6, 45.1, 29.3]
    low_2000 = [13.8, 22.3, 32.5, 37.2, 49.9, 56.1, 57.7, 58.3, 51.2, 42.8, 31.6, 15.9]
    high_2007 = [36.5, 26.6, 43.6, 52.3, 71.5, 81.4, 80.5, 82.2, 76.0, 67.3, 46.1, 35.0]
    low_2007 = [23.6, 14.0, 27.0, 36.8, 47.6, 57.7, 58.9, 61.2, 53.3, 48.5, 31.0, 23.6]
    high_2014 = [28.8, 28.5, 37.0, 56.8, 69.7, 79.7, 78.5, 77.8, 74.1, 62.6, 45.3, 39.9]
    low_2014 = [12.7, 14.3, 18.6, 35.5, 49.9, 58.0, 60.0, 58.6, 51.7, 45.2, 32.2, 29.1]
    
    chart = BurnupChart(title='Average High and Low Temperatures in New York',
                   xaxis_title='Month',
                   yaxis_title='Temperature (degrees F)')
    chart.add_trace(month,high_2014,'High 2014',
                    dict(color='firebrick', width=2))
    chart.add_trace(month,low_2014,'Low 2014',
                    dict(color='royalblue', width=2))
    chart.add_trace(month,high_2007,'High 2007',
                    dict(color='firebrick',width=2,dash='dash'))
    chart.add_trace(month,low_2007,'Low 2007',
                    dict(color='royalblue',width=2, dash='dash'))
    chart.add_trace(month,high_2000,'High 2000',
                    dict(color='firebrick',width=2,dash='dot'))
    chart.add_trace(month,low_2000,'Low 2000',
                    dict(color='royalblue',width=2,dash='dot'))
    
    chart.to_html('/Users/cjr/report.html')
    print("done")
#     html_string = fig.to_html()
#     f = open('/Users/cjr/report.html','w')
#     f.write(html_string)
#     f.close()
    