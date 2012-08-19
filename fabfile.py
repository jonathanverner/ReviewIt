from fabric.api import local

def push():
  local("git push origin")
  local("git push gitorious")
  local("git push github")
  
def deploy_static():
  local("./manage.py collectstatic --noinput")
  local("scp -r collected_static/* ffweb:~/public_html/commentbin_static/")