import sys
import re 

#-------------------------------------------------------------------------------
def toHtml(mark,colors,max,slices,val,reduce) :
  str=f'<{mark} style="width:10px;background-color:'
  str += f'{colors[int((val/max)*slices)]};">'
  str +=f'{val/reduce:3.1f}'
  str += f'</{mark}>'
  return(str)

#-------------------------------------------------------------------------------
def calibrate(slices) :
  colors={}
  step=255/slices
  r=0
  g=255
  b=0
  for i in range(0,slices+1) :
    colors[i]=f'rgb({int(r)},{int(g)},{int(b)})'
    g -= step
    r += step
  return(colors)

#-------------------------------------------------------------------------------
class EdfData() :
  #-------------------------------------------------------------------------------
  def __init__(self,fileId) :
    self.fileId=fileId
    self.max=0
    self.h={}

  def getHSortedKeys(self) :
    return(sorted(self.h.keys()))

  def getH(self,key) :
    return(self.h[key])

  def setMax(self,val) :
    if val > self.max :
      self.max=val

  def getMax(self) :
    return(self.max)

#-------------------------------------------------------------------------------
class Puissance(EdfData) :
  #-------------------------------------------------------------------------------
  def __init__(self,fileId) :
    super().__init__(fileId)
    self.file="mes-puissances-atteintes-30min-"+fileId+".csv"
    self.fileProcessor=PuissanceFileProcessor(self)

  def getHSortedKeys1(self,val) :
    if val in self.h :
      return(sorted(self.h[val].keys()))
    else :
      return([])

  def addDay(self,day) :
    if day not in self.h :
      self.h[day]={}

  def addData(self,day,t) :
    self.h[day][t[0]]=int(t[1])

  def getH1(self,key,h) :
    return(self.h[key][h])

#-------------------------------------------------------------------------------
class Conso(EdfData) :
  #-------------------------------------------------------------------------------
  def __init__(self,fileId) :
    super().__init__(fileId)
    self.file="ma-conso-quotidienne-"+fileId+".csv"
    self.fileProcessor=ConsoFileProcessor(self)

  def addDay(self,day) :
    if day not in self.h :
      self.h[day]=None

  def addData(self,day,val) :
    self.h[day]=int(val)

#-------------------------------------------------------------------------------
class FileProcessor() :
  #-------------------------------------------------------------------------------
  def __init__(self,edf) :
    self.edf=edf
    
  #-------------------------------------------------------------------------------
  def process(self) :
    with open(self.edf.file,encoding='latin-1') as p :
      for l in p.readlines() :
        t=l.split(";")
        if len(t) < 2 :
          continue
        self.processLine(l)

  #-------------------------------------------------------------------------------
  def formatDay(self,pdate):
    if '/' not in pdate :
      return(None)
    t1=pdate.split("/")
    day=f'{t1[2]}/{t1[1]}/{t1[0]}'
    return(day)

#-------------------------------------------------------------------------------
class ConsoFileProcessor(FileProcessor) :
  #-------------------------------------------------------------------------------
  def __init__(self,edf) :
    super().__init__(edf)
    
  #-------------------------------------------------------------------------------
  def processLine(self,l) :
    t=l.split(";")
    if '/' not in t[0] :
      return()
    day=self.formatDay(t[0])
    self.edf.addDay(day)
    self.edf.setMax(int(t[1]))
    self.edf.addData(day,t[1])

#-------------------------------------------------------------------------------
class PuissanceFileProcessor(FileProcessor) :
  #-------------------------------------------------------------------------------
  def __init__(self,edf) :
    super().__init__(edf)
    self.day='----/--/--'
    
  #-------------------------------------------------------------------------------
  def processLine(self,l) :
    t=l.split(";")
    if ':' in t[0] :
      self.edf.setMax(int(t[1]))
      self.edf.addData(self.day,t)
    else :
      self.day=self.formatDay(t[0])
      self.edf.addDay(self.day)

#-------------------------------------------------------------------------------
def outHtml(p,c,filter) :
  slicesP=3
  slicesC=5
  PCOLOR=calibrate(slicesP)
  CCOLOR=calibrate(slicesC)
  print(f'<html>')
  print(f'<body>')
  print(f'<table>\n')
  for d in c.getHSortedKeys() :
    if re.search(filter,d) is None :
      continue
    str=f'<tr><td>{d}</td>'
    #print(f'{d=} {c.getH(d)=}')
    str += f'{toHtml('th',CCOLOR,c.getMax(),slicesC,c.getH(d),1)}'
    for h in p.getHSortedKeys1(d) :
      str += toHtml('td',PCOLOR,p.getMax(),slicesP,p.getH1(d,h),1000)
    str += '</tr>\n'
    print(f'{str}')
  print(f'</table>')
  print(f'</body>')
  print(f'</html>')


#-----------------------------------------------------------
H={}
filter='.*'
if len(sys.argv) > 2 :
  filter=sys.argv[2]
p=Puissance(sys.argv[1])
p.fileProcessor.process()
c=Conso(sys.argv[1])
c.fileProcessor.process()

outHtml(p,c,filter)
