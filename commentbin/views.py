# Create your views here.
from django.shortcuts import render_to_response
from django.http import Http404, HttpResponseRedirect,HttpResponse
from django import forms
from django.template import RequestContext,Context,Template

from common.http import HttpNotImplemented,HttpPermissionDenied
from commentbin.models import Snippet,Comment

class NewSnippetForm(forms.ModelForm):
  class Meta:
    model = Snippet
  
def index(request):
  if request.method == 'GET':
    form = NewSnippetForm()
  elif request.method == 'POST':
    form = NewSnippetForm(request.POST)
    if form.is_valid():
      if request.user.is_authenticated():
	forms.user = request.user
      snip = form.save()
      snip.user=request.user
      snip.save()
      from django.core.urlresolvers import reverse
      return HttpResponseRedirect(reverse('commentbin.views.snippet',args=[snip.id]))
  else:
    raise HttpNotImplemented

  snippets = Snippet.objects.all().order_by('-creation_date')[:10]
  return render_to_response('index.html',
                              {'latest_snippets_list':snippets,
                               'form':form},
                              context_instance=RequestContext(request))


exportCommentFields = ("text","start","end")
                              
def snippet(request,snippet_id):
  try:
    snip = Snippet.objects.get(pk = snippet_id)
  except Snippet.DoesNotExist:
    raise Http404
  
  if request.method == 'GET':
    params = {'snippet':snip}
    
    try:
      comments = Comment.objects.filter(snippet = snip)
      from django.core import serializers
      params['comments'] = serializers.serialize("json",comments,ensure_ascii=False,fields=exportCommentFields);
    except Comment.DoesNotExist:
      pass
      
    from pygments import highlight
    from pygments.lexers import PythonLexer
    from pygments.formatters import HtmlFormatter
    
    params['formated_code']=highlight( snip.code, PythonLexer(), HtmlFormatter(linenos=True) )
    import time
    params['timestamp'] = int(time.time())
    return render_to_response('snippet.html',params,context_instance=RequestContext(request))
  else:
    raise HttpNotImplemented
    

def comments(request,snippet_id):
  try:
    snip = Snippet.objects.get(pk = snippet_id)
  except Snippet.DoesNotExist:
    raise Http404  
 
  from datetime import datetime
  import time
  from django.core import serializers
  import simplejson as json
  
  if request.method == 'GET':

    try:
      created_after = datetime.fromtimestamp(int(float(request.GET["created_after"])))
    except:
      created_after = datetime.fromtimestamp(0)
    
    try:
      comments = Comment.objects.filter(snippet = snip, creation_date__gte = created_after)
      result = { "timestamp":int(time.time()),
                 "comments":serializers.serialize("json",comments,ensure_ascii=False,fields=exportCommentFields),
                 "status":"Ok" }
    except:
      result = { "status":"Fail",
		 "timestamp":int(time.time())}
    return HttpResponse(json.dumps(result),"application/json")
  elif request.method == 'POST':
    if not request.user.is_authenticated():
      raise HttpPermissionDenied
    
    comment = Comment.objects.create( text = str(request.POST["text"]),
                                      start = int(request.POST["start"]),
                                      end = int(request.POST["end"]),
                                      user = request.user,
                                      snippet = snip );
    comment.save()
    result = { "timestamp":int(time.time()),
               "comment":serializers.serialize("json",[comment],ensure_ascii=False,fields=exportCommentFields),
               "clientid":int(request.POST["id"]),
               "status":"Ok" }
    return HttpResponse(json.dumps(result),"application/json");
  else:
    raise HttpNotImplemented

def comment(request,snippet_id,comment_id):
  try:
    snip = Snippet.objects.get(pk = snippet_id)
    comment = Comment.objects.get(pk = comment_id, snippet = snip)
  except:
    raise Http404
  import time
  from django.core import serializers
  import simplejson as json
  from common.utils import coerce_post
  if request.method == 'GET':
    result = { "timestamp":int(time.time()),
               "comment":serializers.serialize("json",[comment],ensure_ascii=False,fields=exportCommentFields),
               "status":"Ok" }
    return HttpResponse( json.dumps(result),"application/json")
  elif request.method == 'PUT':
    coerce_post(request)
    if not request.user.is_authenticated() or request.user != comment.user:
      raise HttpPermissionDenied
    comment.text = request.PUT["text"]
    comment.start = int(request.PUT["start"])
    comment.end = int(request.PUT["end"])
    comment.save()
    result = { "timestamp":int(time.time()),
               "comment":serializers.serialize("json",[comment],ensure_ascii=False,fields=exportCommentFields),
               "status":"Ok" }
    return HttpResponse( json.dumps(result),"application/json")
  elif request.method == 'DELETE':
    coerce_post(request)
    if not request.user.is_authenticated():
      raise HttpPermissionDenied
    coerce_post(request)
  else:
    raise HttpNotImplemented
