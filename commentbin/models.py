from django.db import models
from django.contrib.auth.models import User

class Snippet(models.Model):
  PYTHON='py'
  LATEX='tex'
  CPP='cpp'
  C='c'
  HTML='html'
  
  LANGUAGE_CHOICES = (
    ( PYTHON, 'Python' ),
    ( LATEX,  'LaTeX' ),
    ( CPP,    'C++' ),
    ( C,      'C'),
    ( HTML,   'HTML'),
  )
  
  class Meta:
    ordering = ['creation_date']

  title = models.CharField(max_length=100,blank=True)
  code = models.TextField()
  formatted_html = models.TextField("cached pygment-formatted html version of the code",blank=True,editable=False,default=None)
  creation_date = models.DateTimeField(auto_now_add=True)
  nick = models.CharField(max_length=30,blank=True)
  user = models.ForeignKey(User,related_name='+',blank=True,null=True,on_delete=models.SET_NULL)
  public_comments = models.BooleanField("allow anyone to comment",default = True,help_text='If true, anyone can comment. Otherwise only the owner (if available), admin or the person with an access token can comment.' )
  visible_to_public = models.BooleanField("allow anyone to view",default = True,help_text='If false, the snippet will only be visible to the owner (if available) or anyone with the access token')
  owner_only_comments = models.BooleanField("only the owner can comment",default = False,help_text='If true only the owner can comment. Note that the user must be known, otherwise no comments will be allowed')
  access_token = models.CharField(max_length=100,blank=True,default=None,help_text='The "master key" to the snippet. Its knowledge allows commenting, deleting and viewing the snippet.')
  language = models.CharField(max_length=4,choices = LANGUAGE_CHOICES,default=PYTHON)
  
  def format_code(self):
    from pygments import highlight
    from pygments.lexers import PythonLexer
    from pygments.formatters import HtmlFormatter
    
    self.formatted_html = highlight( self.code, PythonLexer(), HtmlFormatter(linenos=True) )
  
  def display_author(self):
    if self.user is not None:
      return self.user.username
    elif self.nick is not None:
      return self.nick
    else:
      return "anonymous"
    
  def __unicode__(self):
    return "Snippet #"+str(self.id)+":"+self.title;
  
  @models.permalink
  def get_absolute_url(self):
    return ('commentbin.views.snippet',(str(self.id)),{})
  
  def save(self,*args, **kwargs):
    if self.formatted_html is None:
      self.format_code()
    super(Snippet,self).save(args,kwargs)


class Comment(models.Model):
  class Meta:
    ordering = ['start','end']
  text = models.TextField("the (html) text of the comment")
  creation_date = models.DateTimeField(auto_now_add=True)
  nick = models.CharField(max_length=30,blank=True)
  user = models.ForeignKey(User,related_name='+',blank=True,null=True,on_delete=models.SET_NULL)
  snippet = models.ForeignKey(Snippet)
  replyto = models.ForeignKey('self',blank=True,null=True,default=None)
  start = models.IntegerField()
  end = models.IntegerField()
  inlinecomment = models.BooleanField("Is this an inline comment",default=True)
  access_token = models.CharField(help_text='The "master key" to the comment. Its knowledge allows deleting and modifying the comment.',max_length=100,blank=True,default=None)
  
  def __unicode__(self):
    return self.text
  
  def display_author(self):
    if self.user:
      return self.user.username
    elif self.nick:
      return self.nick
    else:
      return "anonymous"
  
  @models.permalink
  def get_absolute_url(self):
    return ('commentbin.views.comment',(str(self.snippet.id),str(self.id)))
  
  
# Create your models here.
