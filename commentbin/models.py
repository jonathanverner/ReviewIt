from django.db import models
from django.contrib.auth.models import User

class Snippet(models.Model):
  PYTHON='py'
  LATEX='tex'
  CPP='cpp'
  C='c'
  HTML='html'
  JAVASCRIPT='js'
  PHP = 'php'
  CSS = 'css'
  
  LANGUAGE_CHOICES = (
    ( PYTHON, 'Python' ),
    ( LATEX,  'LaTeX' ),
    ( CPP,    'C++' ),
    ( C,      'C'),
    ( HTML,   'HTML'),
    ( JAVASCRIPT, 'JavaScript'),
    ( PHP,    'PHP'),
    ( CSS,    'CSS (Cascading Style Sheets)'),
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
  owner_only_comments = models.BooleanField("only the owner can comment/delete",default = False,help_text='If true only the owner can comment. Note that the user must be known, otherwise no comments will be allowed')
  access_token = models.CharField(max_length=100,blank=True,default=None,help_text='The "master key" to the snippet. Its knowledge allows commenting, deleting and viewing the snippet.')
  language = models.CharField(max_length=4,choices = LANGUAGE_CHOICES,default=PYTHON)
  
  def format_code(self):
    from pygments import highlight
    from pygments.lexers import PythonLexer, HtmlLexer, JavascriptLexer, PhpLexer, TexLexer, CppLexer, CLexer, CssLexer
    from pygments.formatters import HtmlFormatter
    
    if self.language == self.PYTHON:
      lexer = PythonLexer()
    elif self.language == self.LATEX:
      lexer = TexLexer()
    elif self.language == self.CPP:
      lexer = CppLexer()
    elif self.language == self.C:
      lexer = CLexer()
    elif self.language == self.HTML:
      lexer = HtmlLexer()
    elif self.language == self.JAVASCRIPT:
      lexer = JavascriptLexer()
    elif self.language == self.PHP:
      lexer = PhpLexer()      
    elif self.language == self.CSS:
      lexer = CssLexer()
    
    self.formatted_html = highlight( self.code, lexer, HtmlFormatter(linenos=True) )
  
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
    super(Snippet,self).save(kwargs)


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

