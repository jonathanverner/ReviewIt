from models import Snippet,Comment

import string,random

def generateNewAccessToken(request):
  request.session['comment_access_token'] = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(15))

def generateAccessTokenIfNotPresent(request):
  if not 'comment_access_token' in request.session:
    generateNewAccessToken(request)
    
    

def allow(request,instance,action):
  try:
    # The superuser can do anything
    if request.user.is_superuser:
      return True
    
    # The owner of the object can do anything to it
    # as does anyone knowing the access token
    if request.user == instance.user or ('access_token' in request.GET and instance.access_token == str(request.GET['access_token'])):
      return True
    
    if isinstance(instance,Snippet):
      # Since we do not own the object and it has 'owner_only_comments' set to True
      # we cannot add comments
      if action =='add_comment' and instance.owner_only_comments:
	return False
      print request.GET
      print request.POST
      if ('snippet_access_token' in request.session and instance.access_token == request.session['snippet_access_token']) or (
          'snippet_access_token' in request.GET and instance.access_token == request.GET['snippet_access_token']) or (
          'snippet_access_token' in request.POST and instance.access_token == request.POST['snippet_access_token']):
	return True
    
      # Snippets may be viewed if they are public or if the
      # access_token was provided
      if action == 'view':
	return instance.visible_to_public
      
      elif action == 'add_comment':
	return instance.public_comments
      
      elif action == 'delete':
	return False
      
      elif action == 'view_access_token':
	return False
    
    elif isinstance(instance,Comment):
        if ('comment_access_token' in request.session and instance.access_token == request.session['comment_access_token']):
	  return True
	
	if action == 'view':
	  return allow(request, instance.snippet, action)
	
	elif action == 'view_access_token':
	  # Since only logged in owners may view the token,
	  # and they were handled above (request.user == instance.user ...)
	  # we know that we return False
	  return False
	
	elif action == 'delete':
	  # Only logged in owners or people with access_tokens may delete
	  return False
  except:
    pass
  return False