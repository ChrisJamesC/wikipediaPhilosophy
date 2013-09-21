import urllib2
from bs4 import BeautifulSoup
from bottle import route, run, template, static_file,request
import time
from HTMLParser import HTMLParseError

template = "http://en.wikipedia.org"
philosophy_link = "/wiki/Philosophy"
philosophy_title = "Philosophy"
cache = {}
deprecated=24*60*60 #One day in seconds

def isValid(ref,paragraph):
   if not ref or "#" in ref or "//" in ref: 
      return False
   if "/wiki/" not in ref: 
      return False
   if ref not in paragraph:
      return False
   prefix = paragraph.split(ref,1)[0]
   if prefix.count("(")!=prefix.count(")"): 
      return False
   return True

def validateTag(tag):
   name = tag.name 
   isParagraph = name == "p"
   isList = name == "ul"
   return isParagraph or isList

def getFirstLink(wikipage):
   if wikipage in cache:
      cached = cache[wikipage]
      if time.time()-cached["time"]<deprecated:
         return cached["value"]
   req = urllib2.Request(template+wikipage, headers={'User-Agent' : "Magic Browser"}) 
   page = urllib2.urlopen(req)
   data = page.read()
   soup = BeautifulSoup(data)
   soup = soup.find(id="mw-content-text")
   for paragraph in soup.find_all(validateTag, recursive=False):
      for link in paragraph.find_all("a"):
         ref = link.get("href")
         if isValid(str(ref),str(paragraph)):
            cache[wikipage]={"value":link,"time":time.time()}
            return link
   return False

def iterateThroughPages(firstLink): 
   steps = []
   out = []
   link = firstLink
   title = ""
   result = ""
   while link is not philosophy_link:
      if not link:
         result = "No first link found in: "+steps[-1]
         break
      if link == philosophy_link: 
         result = philosophy_title+" found after "+str(len(steps))+" clics!"
         break
      current = getFirstLink(link)
      if not current: 
         result = "No first link in page"
         break
      link = current.get("href")
      title = current.get("title")
      print title
      if link not in steps:
         steps.append(link)
         out.append({
            'link':template+link, 
            'title':title
         })
      else:
         result = "We loop on "+title
         break
   return {'result':result, 'steps':out}


@route('/')
def index(): 
   return static_file("index.html", root="static")

@route('/static/<filename>')
def server_static(filename):
    return static_file(filename, root='static')

@route('/crowl')
def crowl():
   name = request.GET.get('title')
   link = "/wiki/"+urllib2.quote(name,safe=":/")
   print("LINK:"+link)
   try:
      res = iterateThroughPages(link)
      return res
   except:
      res = {"result": "Internal error"}

run(host='localhost', port=80)

ex1 = "/wiki/Hurricane_Ingrid_(2013)"
ex2 = "/wiki/Logic"
ex3 = "/wiki/Savoie"
ex4 = "/wiki/Julie_(given_name)"
ex5 = "/wiki/USA"
ex6 = "/wiki/United_States"
iterateThroughPages(ex6)

   

