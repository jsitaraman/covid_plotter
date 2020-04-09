# script to plot covid 19 cases available data
#
# J. Sitaraman
# 3/23/2019
#
import sys
import os
import matplotlib
matplotlib.use('pdf')
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
import numpy as np
import StringIO
#
source1='https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
source2='https://commons.wikimedia.org/wiki/Data:COVID-19_Cases_in_Santa_Clara_County,_California.tab'
source3='https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv'
#
# parse the JHU master data base
#
def getJHUData():
  os.system('rm *csv*;wget %s >& source1.log'%source1)
  os.system('wget %s >& source2.log'%source3)
  data=open('time_series_covid19_confirmed_global.csv','r').readlines()
  dataUSA=open('time_series_covid19_confirmed_US.csv','r').readlines()
  #data=open('time_series_19-covid-Deaths.csv','r').readlines()  
  datatab=[[a for a in d.split(',')] for d in data+dataUSA]
  return len(data),datatab
#
# get santa clara data from wikipedia commons
# because its not updated anymore by JHU 
# deprecated (JHU started updating in a new file)
#
def getSantaClaraData(datatab):
  import xml.etree.ElementTree as ET
  os.system('rm *.tab* > /dev/null 2>&1')
  os.system('wget %s > /dev/null 2>&1'%source2)
  def getxml(data,node):
    if (len(node.getchildren())==0):
         data[0]+=node.text
	 data[0]+=','
         #print node.text,
    else:
         data[0]+='\n'
         #print '\n',
    for j in node.getchildren():
        getxml(data,j)
  rootXML = ET.parse('Data:COVID-19_Cases_in_Santa_Clara_County,_California.tab')
  data=['']
  for neighbor in rootXML.iter('table'):
    getxml(data,neighbor)
  m=0
  buf=StringIO.StringIO(data[0])
  bufl=buf.readlines()
  for i in bufl:
      if '31-Jan' in i:
        break
      m=m+1
  sc=[]
  for i in bufl[m:]:
     print i.split(',')
     sc.append(i.split(',')[2])
  nn=len(datatab[-1])
  datatab.append(['','Santa Clara County'])
  for i in range(nn-2):
    datatab[-1].append('0')
  datatab[-1][-len(sc):]=sc
  print datatab[m] 
  return sc

if __name__== "__main__":
  #
  # main
  #
  regions=['US','Italy','India','France','Switzerland','California','Santa Clara','Quebec','Washington','New York']
  #regions=['Italy','California','Qatar','United Arab Emirates','Malaysia','Australia','India','New York','Illinois','Arizona','Maryland']
  #
  # TODO have to automatically sequence these colors
  #
  colors=['k','r','m','c','y','g','b'] 
  ncol=len(colors)
  for c in colors[:ncol]:
     colors.append(c+'o-')
  for c in colors[:ncol]:
     colors.append(c+'-.')
  #
  # number of days back from today to plot
  # default is 2 months
  #
  days=60
  avg_range=5
  ratePlot=False
  #
  if len(sys.argv)==1:
    print("Usage : python plotcovid.py --days=days --avg_range=avg_range --ratePlot=[True,False] --regions=<region1>,<region2>,<region3>..\n\n\n")
    print("Output : test.pdf \n\n")
    print("Using defaults now")
    print("regions=",regions)
    print("days=",days)
    print("avg_range=\n\n",avg_range)
    print("sources=%s\n%s\n",source1,source3)
  else:  
   # simple arg parser now
   for arg in sys.argv:
     if '--days' in arg:
         days=int(arg.strip('--days='))
     if '--ratePlot=True' in arg:
         ratePlot=True
     if '--avg_range' in arg:
         avg_range=int(arg.strip('--avg_range='))
     if '--regions=' in arg:
         print arg
         regions=[]
         regions=arg[10:].split(',')
         print regions
  #
  # main
  # read JHU data
  #
  ncountries,datatab=getJHUData()
  nsamples=len(datatab[0])-4 
  # 
  # fix santa clara county data
  #
  #scdata=getSantaClaraData(datatab)
  #
  # regions that the plot needs to be created
  # for. These strings need to be exact based on the
  # JHU data base
  #
  #
  # strip out only data per region
  #
  dtab={}
  for r in regions:
    dtab[r]=[]
  #
  # check if a primary region (a country)
  #
  for d in datatab[:ncountries]:
    for r in regions:
     if len(dtab[r])==0:
      if r == d[1] and d[0]=='':
        dtab[r]=[float(a.strip('\r\n')) for a in d[4:]]
  #
  # check if province of a country other than
  # US 
  #
  for d in datatab[:ncountries]:
    for r in regions:
     if len(dtab[r])==0:
      if r == d[0]:
        dtab[r]=[float(a.strip('\r\n')) for a in d[4:]]
  #
  # if not found check if its a secondary
  # region, county in the united states
  #
  for d in datatab[ncountries:]:
    for r in regions:
     if len(dtab[r])==0:
      if r == d[5]:
        dtab[r]=[float(a.strip('\r\n')) for a in d[-nsamples:]]
      if r == d[6]:
        dtab[r]=[float(a.strip('\r\n')) for a in d[-nsamples:]]
     else:
      if r== d[6]:
         val=[float(a) for a in d[-nsamples:]]
         for k in range(len(val)):
           dtab[r][k]+=val[k]
          
  #
  # do the actual plotting
  #
  m=0
  leg=[]
  fig=plt.figure()
  ax=plt.subplot(111)
  plt.subplot(1,1,1)
  if ratePlot:
    for k in dtab.keys():
      if len(dtab[k])==0:
         print( "No data found for %s"%k)
         continue
      x=np.arange(-avg_range,days)
      y=np.array([float(a) for a in dtab[k][-days-avg_range:]])
      yy=[]
      for i in range(days):
       if (y[i] > 0):
          p=np.polyfit(x[i:i+avg_range],np.log(y[i:i+avg_range]),1)
          yy.append(np.exp(p[0])*100-100)
       else:
          yy.append(0)
      leg.append(k)
      plt.plot(x[avg_range:],yy,colors[m])
      plt.hold(True)
      m=m+1
  else:
    for k in dtab.keys():
      if len(dtab[k])==0:
         print ("No data found for %s"%k)
         continue
      x=np.arange(0,days)
      y=np.array(dtab[k][-days:])
      #y=np.array([float(a.strip('\r\n')) for a in dtab[k][-days:]])
      #except:
      #  y=dtab[k][-days:]
      plt.semilogy(x,y,colors[m])
      plt.hold(True)
      p=np.polyfit(x[-avg_range:],np.log(y[-avg_range:]+1e-8),1)
      doubling_time=np.log(2)/p[0]
      if m > 0:
        leg.append(k+'(%0.2f days)'%doubling_time)
      else:
        leg.append(k+'(%0.2f days*)'%doubling_time)
      m=m+1
  plt.xlim([0,days])
  box=ax.get_position()
  ax.set_position([box.x0,box.y0,box.width,box.height*1.2])
  plt.legend(leg,fontsize=8,loc='upper center', bbox_to_anchor=(0.44, 1.30),ncol=4, fancybox=True, shadow=True)
  if ratePlot:
    plt.ylabel('Growth Rate %')
    plt.ylim([0,100])
    plt.text(0,107,'Growth rate computed as percentage increase based on regression on last %d-days'%avg_range,fontsize=8,bbox=dict(facecolor='red', alpha=0.5))
    plt.text(0,101,'sources: %s\n%s%s'%(source1,'              ',source2),fontsize=6)
  else:
    plt.ylabel('Number of Confirmed COVID-19 cases')
    plt.text(0,1.2e6,'* number of days to double based on last %d-day average'%avg_range,fontsize=8,bbox=dict(facecolor='red', alpha=0.5))
    plt.text(0,2e6,'sources: %s\n%s%s'%(source1,'              ',source2),fontsize=6)

  plt.xticks(np.arange(0,days,2),datatab[0][-days::2],rotation='vertical')
  plt.grid(True)

  fig.set_tight_layout(True)
  plt.savefig('test')
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
