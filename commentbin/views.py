# Create your views here.
from django.shortcuts import render_to_response
from django.http import Http404, HttpResponseRedirect,HttpResponse
from django import forms
from django.template import RequestContext,Context,Template
from django.core import serializers
from django.core.urlresolvers import reverse as reverseurl
import simplejson as json

from common.http import HttpNotImplemented,HttpPermissionDenied,HttpJSONResponse
import common.utils as utils
from commentbin.models import Snippet,Comment
import commentbin.auth as auth



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
      return HttpResponseRedirect(reverseurl('commentbin.views.snippet',args=[snip.id]))
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
  
  if snip.formatted_html is None:
    snip.format_code()
  
  if request.method == 'GET':
    params = {'snippet':snip}
    utils.add_timestamp(params)
    
    try:
      comments = Comment.objects.filter(snippet = snip)
      params['comments'] = serializers.serialize("json",comments,ensure_ascii=False,fields=exportCommentFields);
    except Comment.DoesNotExist:
      pass
    
    return render_to_response('snippet.html',params,context_instance=RequestContext(request))
  elif request.method == 'DELETE':
    if not auth.allow(request,snip,'delete'):
      raise HttpPermissionDenied
    else:
      snip.delete()
      return HttpResponseRedirect(reverseurl('commentbin.views.index'))
  else:
    raise HttpNotImplemented
    

def comments(request,snippet_id):
  try:
    snip = Snippet.objects.get(pk = snippet_id)
  except Snippet.DoesNotExist:
    raise Http404
  
  if request.method == 'GET':
    try:
      from datetime import datetime
      created_after = datetime.fromtimestamp(int(float(request.GET["created_after"])))
    except:
      created_after = datetime.fromtimestamp(0)
    
    try:
      comments = Comment.objects.filter(snippet = snip, creation_date__gte = created_after)
      result = { "comments":serializers.serialize("json",comments,ensure_ascii=False,fields=exportCommentFields),
                 "status":"Ok" }
    except:
      result = { "status":"Fail" }
      
    return HttpJSONResponse( result )

  
  elif request.method == 'POST':
    if not auth.allow(request,snip,'add_comment'):
      raise HttpPermissionDenied

    comment = Comment.objects.create( text = unicode(request.POST["text"]),
                                      start = int(request.POST["start"]),
                                      end = int(request.POST["end"]),
                                      nick = utils.getNick( request ),
                                      user = request.user,
                                      snippet = snip );
    comment.save()
    result = { "comment":serializers.serialize("json",[comment],ensure_ascii=False,fields=exportCommentFields),
               "clientid":int(request.POST["id"]),
               "status":"Ok" }
    return HttpJSONResponse( result )
  
  else:
    raise HttpNotImplemented

def comment(request,snippet_id,comment_id):
  try:
    snip = Snippet.objects.get(pk = snippet_id)
    comment = Comment.objects.get(pk = comment_id, snippet = snip)
  except:
    raise Http404

  if request.method == 'GET':
    result = { "comment":serializers.serialize("json",[comment],ensure_ascii=False,fields=exportCommentFields),
               "status":"Ok" }
    return HttpJSONResponse( result )
  
  elif request.method == 'PUT':
    utils.coerce_post(request)
    if not auth.allow(request, comment, 'change'):
      raise HttpPermissionDenied

    comment.text = request.PUT["text"]
    comment.start = int(request.PUT["start"])
    comment.end = int(request.PUT["end"])
    comment.save()
    
    result = { "comment":serializers.serialize("json",[comment],ensure_ascii=False,fields=exportCommentFields),
               "status":"Ok" }
    return HttpJSONResponse( result )
  
  elif request.method == 'DELETE':
    if not auth.allow(request,comment,'delete'):
      raise HttpPermissionDenied
    comment.delete()
    return HttpJSONResponse( {'status':'Ok', 'deletedID':comment_id} )

  else:
    raise HttpNotImplemented
