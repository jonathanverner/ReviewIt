from django.http import HttpResponseServerError
from django.shortcuts import render_to_response

class HttpNotImplemented(Exception):    
  pass
  
class HttpPermissionDenied(Exception):
  pass


class HttpExceptionsMiddleware(object):     
  def process_exception(self,request,exception):
    if isinstance(exception,HttpNotImplemented):
      response = render_to_response('NotImplemented.html')
      response.status_code=501
      return response
    elif isinstance(exception,HttpPermissionDenied):
      response = render_to_response('PermissionDenied.html')
      response.status_code=403
      return response
      
#      else:
#	return HttpResponseServerError()
	    