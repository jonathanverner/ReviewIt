from fabric.api import *

import urllib2
import cookielib

def push():
  local("git push origin")
  local("git push gitorious")
  local("git push github")
  
def deploy_static():
  local("./manage.py collectstatic --noinput")
  local("scp -r collected_static/* ffweb:~/public_html/commentbin_static/")
  
def reload_pythonanywhere():
  try:
    f = open('/home/jonathan/.kde/share/apps/kcookiejar/cookies','r')
    sessionid=None
    for l in f:
      if 'pythonanywhere' in l and 'sessionid' in l:
	sessionid = l.split()[-1]
    if sessionid is None:
      abort("Please log-in to pythonanywhere in Rekonq")
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    urllib2.install_opener(opener)
    req = urllib2.Request('https://www.pythonanywhere.com/reload_web_app')
    req.add_header("Cookie","sessionid="+sessionid )
    response = urllib2.urlopen(req)
  except urllib2.URLError, e:
    print "Network error:", e
    return None
  ret=response.read()
  if ret == "OK":
    return True
  return False
  
  
