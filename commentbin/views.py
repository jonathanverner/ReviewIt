# Create your views here.
from django.shortcuts import render_to_response
from django.http import Http404, HttpResponseRedirect,HttpResponse
from django import forms
from django.template import RequestContext,Context,Template
from django.core import serializers
from django.core.urlresolvers import reverse as reverseurl
import django.contrib.auth as djangoauth

import json

from common.http import HttpNotImplemented,HttpPermissionDenied,HttpJSONResponse
import common.utils as utils
from commentbin.models import Snippet,Comment
import commentbin.auth as auth


class NewSnippetForm(forms.ModelForm):
  class Meta:
    model = Snippet
    
  initial = { 'nick':'anonymous', 'title':'Enter a title...', 'language':'py' }
  nick = forms.CharField(widget = forms.TextInput(attrs={'size':10, 'class':'nick_related', 'onClick':'javascript:textInputClick(this);', 'onBlur':'javascript:textInputLeave(this);'}))
  title = forms.CharField(widget = forms.TextInput(attrs={'onClick':'this.value=""'}))
      
def logout(request):
  djangoauth.logout(request)
  return HttpResponseRedirect(reverseurl('commentbin.views.index'))

def login(request):
  return HttpResponseRedirect(reverseurl('commentbin.views.index'))

def about(request):
  result = {'nick':request.session.get('nick','anonymous')}
  return render_to_response('about.html',result,context_instance=RequestContext(request))

def sitehelp(request):
  result = {'nick':request.session.get('nick','anonymous')}
  return render_to_response('sitehelp.html',result,context_instance=RequestContext(request))

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
	if snip.access_token == '':
	  snip.access_token = auth.randomToken()
        request.session['snippet_access_token'] = snip.access_token
      if snip.title == 'Enter a title...':
	snip.title = ""
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


exportCommentFields = ("text","start","end", "user", "nick", "inlinecomment","creation_date")


def threadComments( c, comments ):
  replies = []
  for com in comments:
    if com.replyto == c:
      replies.append( threadComments( com, comments ) )
  return { 'comment':c,'replies':replies }

def thread( comments ):
  ret = []
  for c in comments:
    if c.replyto is None:
      ret.append(threadComments(c,comments))
  return ret

def flatten_thread( thread ):
  ret = []
  for element in thread:
    ret.append('indent')
    ret.append(element['comment'])
    if len(element['replies']) > 0:
      ret += flatten_thread( element['replies'])
    ret.append('deindent')
  return ret
  
                              
def snippet(request,snippet_id):
  try:
    snip = Snippet.objects.get(pk = snippet_id)
  except Snippet.DoesNotExist:
    raise Http404
  
  if snip.formatted_html is None:
    snip.format_code()
  
  if request.method == 'GET':
    params = {'snippet':snip,
              'nick':request.session.get('nick','anonymous') }
    utils.add_timestamp(params)
    
    if not auth.allow(request,snip,'view'):
      if 'access_token' in request.GET:
	params['wrong_password']=True
      return render_to_response('snippet-password.html',params,context_instance=RequestContext(request))

    
    try:
      inlinecomments = Comment.objects.filter(snippet = snip,inlinecomment=True)
      othercomments = Comment.objects.filter(snippet = snip,inlinecomment=False)
      params['comments'] = serializers.serialize("json",inlinecomments,ensure_ascii=False,fields=exportCommentFields);
      params['json-othercomments'] = serializers.serialize("json",othercomments,ensure_ascii=False,fields=exportCommentFields);
      params['threadedcomments'] = flatten_thread(thread((othercomments)))
    except Comment.DoesNotExist:
      pass

    params['show_delete_link'] = auth.allow(request,snip,'delete')
    params['show_comment_interface'] = auth.allow(request,snip,'add_comment')
    params['show_access_token'] = auth.allow(request,snip,'view_access_token')
    params['nick'] = request.session.get('nick','anonymous');
    
    return render_to_response('snippet.html',params,context_instance=RequestContext(request))
  elif request.method == 'DELETE':
    if not auth.allow(request,snip,'delete'):
      raise HttpPermissionDenied
    else:
      snip.delete()
      result = { "status":"Ok",
                 "redirect":reverseurl('commentbin.views.index') }
      return HttpJSONResponse(result)
  else:
    raise HttpNotImplemented

def commentFromRequest( request, snip ):
    if request.user.is_authenticated():
      u = request.user
    else:
      u = None
    auth.generateAccessTokenIfNotPresent(request)
    comment = Comment.objects.create( text = unicode(request.POST["text"]),
                                      start = int(request.POST["start"]),
                                      end = int(request.POST["end"]),
                                      nick = utils.getNick( request ) or "",
                                      user = u,
                                      snippet = snip,
                                      access_token = request.session['comment_access_token']);
    if comment.end == 0:
      comment.inlinecomment = False
    return comment

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
      inlinecomments = Comment.objects.filter(snippet = snip, creation_date__gte = created_after, inlinecomment = True)
      othercomments = Comment.objects.filter(snippet = snip, creation_date__gte = created_after, inlinecomment = False)
  
      result = { "comments":serializers.serialize("json",inlinecomments,ensure_ascii=False,fields=exportCommentFields),
		 "othercomments":serializers.serialize("json",othercomments,ensure_ascii=False,fields=exportCommentFields),
                 "status":"Ok" }
    except:
      result = { "status":"Fail" }
      
    return HttpJSONResponse( result )

  
  elif request.method == 'POST':
    if not auth.allow(request,snip,'add_comment'):
      raise HttpPermissionDenied
    
    comment = commentFromRequest(request, snip)
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

  elif request.method == 'POST':
    if not auth.allow(request,snip,'add_comment'):
      raise HttpPermissionDenied
    
    reply_comment = commentFromRequest(request,snip)
    reply_comment.replyto = comment
    reply_comment.save()
    request.session['nick'] = utils.getNick( request )
    result = { "comment":serializers.serialize("json",[reply_comment],ensure_ascii=False,fields=exportCommentFields),
               "clientid":int(request.POST["id"]),
               'access_token':request.session['comment_access_token'],
               "status":"Ok" }
    return HttpJSONResponse( result )    
  else:
    raise HttpNotImplemented
