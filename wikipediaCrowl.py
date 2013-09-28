import urllib2
from bs4 import BeautifulSoup
from bottle import route, run, template, static_file,request, default_app
import time
import os

# Conventions: 
# A link is of form "/wiki/United_States"
# A title is of form "United States"

template = "https://en.wikipedia.org"
philosophy_link = "/wiki/Philosophy"
philosophy_title = "Philosophy"
cache = {}
deprecated=24*60*60 # One day in seconds

local = os.environ.get('LOCAL') 

def isValid(ref,paragraph):
   # Check whether the reference is valid in the paragraph
   if not ref or "#" in ref or "//" in ref or ":" in ref:
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
   # Check whether the tag is one in which we could find a valid link 
   name = tag.name
   isParagraph = name == "p"
   isList = name == "ul"
   return isParagraph or isList

def getSoup(address): 
   req = urllib2.Request(address, headers={'User-Agent' : "Magic Browser"})
   data = urllib2.urlopen(req).read()
   soup = BeautifulSoup(data)
   soup = soup.find(id="mw-content-text")
   return soup

def titleToLink(title): return "/wiki/"+title
def linkToTitle(link): return link[6:]

def getFirstLink(link):
   if link in cache:
      cached = cache[link]
      if time.time()-cached["time"]<deprecated:
         return cached["value"]
   
   title = linkToTitle(link)
   print title
   soup = getSoup("http://en.wikipedia.org/w/index.php?title="+title+"&printable=yes")
   if not soup: 
      return False

   for paragraph in soup.find_all(validateTag, recursive=False):
      for newLink in paragraph.find_all("a"):
         ref = newLink.get("href")
         if isValid(str(ref),str(paragraph)):
            cache[link]={"value":newLink,"time":time.time()}
            return newLink
   return False


def iterateThroughPages(title):
   steps = []
   out = []
   link = "/wiki/"+title
   result = ""
   first = True
   while link is not philosophy_link:
      if not link:
         result = "No first link found in: "+steps[-1]
         break
      if link == philosophy_link:
         result = philosophy_title+" found after "+str(len(steps))+" clicks!"
         break
      current = getFirstLink(link)

      if not current:
         result = "No first link in page"
         break
      link = current.get("href")
      title = current.get("title")
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
   if local: 
      return static_file("index.html", root="static")
   else: 
      return static_file("index.html", root="/home/ChrisJamesC/wikipediaPhilosophy/static")

@route('/static/<filename>')
def server_static(filename):
    return static_file(filename, root='static')

@route('/crowl')
def crowl():
   name = request.GET.get('title')
   title = urllib2.quote(name,safe=":/")
   if local: 
      return iterateThroughPages(title)
   else: 
      try:
         return iterateThroughPages(title)
      except:
         return {"result": "Internal error", "steps":[]}

if local: 
   run(host='localhost', port=8080)
else: 
   application = default_app()

