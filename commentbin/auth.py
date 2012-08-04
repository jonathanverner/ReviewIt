from models import Snippet,Comment
def allow(request,instance,action):
  try:
    # The superuser can do anything
    if request.user.is_superuser:
      return True
    
    # The owner of the object can do anything to it
    # as does anyone knowing the access token
    if request.user == instance.user or instance.access_token == str(request.GET['access_token']):
      return True
  
    if isinstance(instance,Snippet):
    
      # Snippets may be viewed if they are public or if the
      # access_token was provided
      if action == 'view':
	return instance.visible_to_public
      
      elif action == 'add_comment':
	return instance.public_comment
      
      elif action == 'delete':
	return False
	
  except:
    pass
  return False