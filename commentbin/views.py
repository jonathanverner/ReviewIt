# Create your views here.
from django.shortcuts import render_to_response
from django.http import Http404, HttpResponseRedirect,HttpResponse
from django import forms
from django.template import RequestContext,Context,Template
from django.core import serializers
from django.core.urlresolvers import reverse as reverseurl
import django.contrib.auth as djangoauth

import simplejson as json

from common.http import HttpNotImplemented,HttpPermissionDenied,HttpJSONResponse
import common.utils as utils
from commentbin.models import Snippet,Comment
import commentbin.auth as auth


class NewSnippetForm(forms.ModelForm):
  class Meta:
    model = Snippet
    
  initial = { 'nick':'anonymous', 'title':'Enter a title...', 'code':"\n"*25 }
  nick = forms.CharField(widget = forms.TextInput(attrs={'size':10, 'class':'nick_related', 'onClick':'javascript:textInputClick(this);', 'onBlur':'javascript:textInputLeave(this);'}))
  title = forms.CharField(widget = forms.TextInput(attrs={'onClick':'this.value=""'}))
  code = forms.CharField(widget = forms.Textarea(attrs={'rows':25}))
  
    
  #def __init__(self,*args,**kwargs):
  #  super(NewSnippetForm,self).__init__(args,kwargs)
  #  self.fields['code'].widget.attrs['rows']=25
  #  self.fields['code'].widget.attrs['cols']=80
  #  self.fields['nick'].widget.attrs['size']=10

    
  
def logout(request):
  djangoauth.logout(request)
  return HttpResponseRedirect(reverseurl('commentbin.views.index'))

def login(request):
  return HttpResponseRedirect(reverseurl('commentbin.views.index'))
  
def index(request):
  initial_values = NewSnippetForm.initial
  initial_values['nick'] = request.session.get('nick','anonymous') or 'anonymous'
  form = NewSnippetForm(request.POST or None, initial=initial_values)
  if request.method == 'POST':
    if form.is_valid():
      snip = form.save()
      append_token='';
      if request.user.is_authenticated():
	forms.user = request.user
      else:
	snip.user=None
	request.session['nick'] = snip.nick
	if not snip.visible_to_public or not snip.public_comments:
	  append_token='?access_token='+snip.access_token;
	  request.session['snippet_access_token'] = snip.access_token;
      if snip.title == 'Enter a title...':
	snip.title = None
      snip.save()
      
      return HttpResponseRedirect(reverseurl('commentbin.views.snippet',args=[snip.id])+append_token)
  elif request.method != 'GET':
    raise HttpNotImplemented

  snippets = Snippet.objects.filter(visible_to_public=True).order_by('-creation_date')[:10]
  result = {'latest_snippets_list':snippets,
            'form':form,
            'nick':request.session.get('nick','anonymous')
            }
  utils.add_timestamp(result)
  return render_to_response('index.html',result,context_instance=RequestContext(request))


exportCommentFields = ("text","start","end", "user", "nick")
                              
def snippet(request,snippet_id):
  try:
    snip = Snippet.objects.get(pk = snippet_id)
  except Snippet.DoesNotExist:
    raise Http404
  
  if snip.formatted_html is None:
    snip.format_code()
  
  if request.method == 'GET':
    if not auth.allow(request,snip,'view'):
      raise HttpPermissionDenied
    params = {'snippet':snip}
    utils.add_timestamp(params)
    
    try:
      comments = Comment.objects.filter(snippet = snip)
      params['comments'] = serializers.serialize("json",comments,ensure_ascii=False,fields=exportCommentFields);
    except Comment.DoesNotExist:
      pass

    params['show_comment_interface'] = auth.allow(request,snip,'add_comment')
    params['nick'] = request.session.get('nick','anonymous');
    
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

    if request.user.is_authenticated():
      u = request.user
    else:
      u = None
    auth.generateAccessTokenIfNotPresent(request)
    comment = Comment.objects.create( text = unicode(request.POST["text"]),
                                      start = int(request.POST["start"]),
                                      end = int(request.POST["end"]),
                                      nick = utils.getNick( request ),
                                      user = u,
                                      snippet = snip,
                                      access_token = request.session['comment_access_token']);
    comment.save()
    request.session['nick'] = utils.getNick( request )
    result = { "comment":serializers.serialize("json",[comment],ensure_ascii=False,fields=exportCommentFields),
               "clientid":int(request.POST["id"]),
               'access_token':request.session['comment_access_token'],
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
    if not auth.allow(request,comment,'view'):
      raise HttpPermissionDenied
    result = { "comment":serializers.serialize("json",[comment],ensure_ascii=False,fields=exportCommentFields),
               "status":"Ok" }
    if auth.allow(request,comment,'view_access_token'):
      result['access_token']=comment.access_token
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
