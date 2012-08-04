from django.db import models
from django.contrib.auth.models import User

class Snippet(models.Model):
  title = models.CharField(max_length=100,null=True,blank=True)
  code = models.TextField()
  commented_html = models.TextField(null=True,blank=True,editable=False)
  creation_date = models.DateTimeField(auto_now_add=True)
  user_email = models.EmailField(null=True,blank=True)
  user = models.ForeignKey(User,related_name='+',blank=True,null=True,on_delete=models.SET_NULL)

class Comment(models.Model):
  ordering = ['start','end']
  text = models.TextField()
  creation_date = models.DateTimeField(auto_now_add=True)
  user_email = models.EmailField()
  user = models.ForeignKey(User,related_name='+',blank=True,null=True,on_delete=models.SET_NULL)
  snippet = models.ForeignKey(Snippet)
  start = models.IntegerField()
  end = models.IntegerField()
  
  
# Create your models here.
