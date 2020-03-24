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
source1='https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv'
source2='https://commons.wikimedia.org/wiki/Data:COVID-19_Cases_in_Santa_Clara_County,_California.tab'
#
# parse the JHU master data base
#
def getJHUData():
  os.system('rm *csv*;wget %s'%source1)
  data=open('time_series_19-covid-Confirmed.csv','r').readlines()
  #data=open('time_series_19-covid-Deaths.csv','r').readlines()  
  datatab=[[a for a in d.split(',')] for d in data]
  return datatab
#
# get santa clara data from wikipedia commons
# because its not updated anymore by JHU
#
def getSantaClaraData(datatab):
  import xml.etree.ElementTree as ET
  os.system('rm *.tab')
  os.system('wget %s'%source2)
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
  m=0
  for i in datatab:
     if 'Santa Clara County' in i[0]:
        datatab[m][-len(sc):]=sc
        break
     m=m+1   
  print datatab[m] 
  return sc
#
# main
# read JHU data
#
datatab=getJHUData()
# 
# fix santa clara county data
#
scdata=getSantaClaraData(datatab)
#
# regions that the plot needs to be created
# for. These strings need to be exact based on the
# JHU data base
#
regions=['Italy','California','Colorado','Switzerland','France','Quebec','India','New York','"Santa Clara County']
#regions=['Italy','California','Qatar','United Arab Emirates','Malaysia','Australia','India','New York','Illinois','Arizona','Maryland']
colors=['k','r','m','c','y','g','b','r--','c--','k--','m--','g--','y--']
#
# number of days back from today to plot
# default is 2 months
#
days=60
if (len(sys.argv) > 1):
    days=int(sys.argv[1])
#
# strip out only data per region
#
dtab={}
for r in regions:
  dtab[r]=[]
#
# check if a primary region
#
m=0
for d in datatab:
  for r in regions:
   if len(dtab[r])==0:
    if r == d[0]:
      dtab[r]=datatab[m]
  m=m+1
#
# if not found check if its a secondary
# region
#
m=0
for d in datatab:
  for r in regions:
   if len(dtab[r])==0:
    if r == d[1]:
      dtab[r]=datatab[m]
  m=m+1
#
# do the actual plotting
#
m=0
leg=[]
fig=plt.figure()
ax=plt.subplot(111)
plt.subplot(1,1,1)
for k in dtab:
  x=np.arange(0,days)
  y=np.array([float(a.strip('\r\n')) for a in dtab[k][-days:]])
  plt.semilogy(x,y,colors[m])
  plt.hold(True)
  p=np.polyfit(x[-5:],np.log(y[-5:]+1e-8),1)
  doubling_time=np.log(2)/p[0]
  if m > 0:
    leg.append(k+'(%0.2f days)'%doubling_time)
  else:
    leg.append(k+'(%0.2f days*)'%doubling_time)
  m=m+1
plt.xlim([0,days])
box=ax.get_position()
ax.set_position([box.x0,box.y0,box.width,box.height*1.2])
plt.legend(leg,fontsize=10,loc='upper center', bbox_to_anchor=(0.44, 1.26),ncol=3, fancybox=True, shadow=True)
plt.ylabel('Number of Confirmed COVID-19 cases')
plt.xticks(np.arange(0,days,2),datatab[0][-days::2],rotation='vertical')
plt.grid(True)
plt.text(0,1.5e5,'* number of days to double based on last 5-day average',fontsize=10,bbox=dict(facecolor='red', alpha=0.5))
plt.text(0,2e6,'sources: %s\n%s%s'%(source1,'              ',source2),fontsize=6)
fig.set_tight_layout(True)
plt.savefig('test')
