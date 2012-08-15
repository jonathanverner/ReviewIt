"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.client import RequestFactory,Client
from django.contrib.auth.models import User

from models import Snippet, Comment
import auth


class AuthTest(TestCase):
  def setUp(self):
    self.john = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
    self.sam = User.objects.create_user('sam', 'sam@thebeatles.com', 'sampassword')
    self.public_snippet = Snippet.objects.create(public_comments = True, visible_to_public = True, owner_only_comments = False, access_token='asda',code='')
    self.john_snippet = Snippet.objects.create(public_comments = True, visible_to_public = True, owner_only_comments = False, access_token='asda',code='',user=self.john)
    self.sam_snippet = Snippet.objects.create(public_comments = False, visible_to_public = False, owner_only_comments = True, access_token='asda',code='',user=self.sam)
    self.factory = RequestFactory()

    
  def test_auth_public(self):
    request = self.factory.get('/'+str(self.public_snippet.id))
    request.session = self.client.session
    self.assertTrue( auth.allow( request, self.public_snippet, "view" ) )
    self.assertTrue( auth.allow( request, self.public_snippet, "add_comment" ) )
    self.assertFalse( auth.allow( request, self.public_snippet, "view_access_token" ) )
    self.assertFalse( auth.allow( request, self.public_snippet, "delete" ) )
    request = self.factory.get('/'+str(self.public_snippet.id)+'/?access_token=asda')
    request.session = self.client.session
    self.assertTrue( auth.allow( request, self.public_snippet, "view_access_token" ) )
    self.assertTrue( auth.allow( request, self.public_snippet, "delete" ) )
    request = self.factory.get('/'+str(self.public_snippet.id)+'/?snippet_access_token=asda')
    request.session = self.client.session
    self.assertTrue( auth.allow( request, self.public_snippet, "view_access_token" ) )
    self.assertTrue( auth.allow( request, self.public_snippet, "delete" ) )
    
  def test_owner_anything(self):
    self.client.login(username='john',password='johnpassword')
    request = self.factory.get('/'+str(self.john_snippet.id))
    request.session = self.client.session
    self.assertTrue( auth.allow( request, self.john_snippet, "view" ) )
    self.assertTrue( auth.allow( request, self.john_snippet, "add_comment" ) )
    self.assertTrue( auth.allow( request, self.john_snippet, "view_access_token" ) )
    self.assertTrue( auth.allow( request, self.john_snippet, "delete" ) )
    
    self.client.login(username='sam',password='sampassword')
    request = self.factory.get('/'+str(self.sam_snippet.id))
    request.session = self.client.session
    self.assertTrue( auth.allow( request, self.sam_snippet, "view" ) )
    self.assertTrue( auth.allow( request, self.sam_snippet, "add_comment" ) )
    self.assertTrue( auth.allow( request, self.sam_snippet, "view_access_token" ) )
    self.assertTrue( auth.allow( request, self.sam_snippet, "delete" ) )
    
    
  def test_nonowner_withpass_snippet(self):
    self.client.login(username='john',password='johnpassword')
    
    # Test that non-owner can only view with password
    request = self.factory.get('/'+str(self.sam_snippet.id)+'/?access_token=asda')
    request.session = self.client.session
    self.assertTrue( auth.allow( request, self.sam_snippet, "view_access_token" ) )
    self.assertTrue( auth.allow( request, self.sam_snippet, "view" ) )
    self.assertFalse( auth.allow( request, self.sam_snippet, "add_comment" ) )
    self.assertFalse( auth.allow( request, self.sam_snippet, "delete" ) )
    
  def test_nonowner_nopass_snippet(self):
    self.client.login(username='john',password='johnpassword')
        
    # Test that without password we can't do anything
    request = self.factory.get('/'+str(self.sam_snippet.id)+'/')
    request.session = self.client.session
    self.assertFalse( auth.allow( request, self.sam_snippet, "view_access_token" ) )
    self.assertFalse( auth.allow( request, self.sam_snippet, "view" ) )
    self.assertFalse( auth.allow( request, self.sam_snippet, "add_comment" ) )
    self.assertFalse( auth.allow( request, self.sam_snippet, "delete" ) )
