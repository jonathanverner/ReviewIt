# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'Comment.user_email'
        db.delete_column('commentbin_comment', 'user_email')

        # Adding field 'Comment.nick'
        db.add_column('commentbin_comment', 'nick', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True), keep_default=False)

        # Adding field 'Comment.access_token'
        db.add_column('commentbin_comment', 'access_token', self.gf('django.db.models.fields.CharField')(default=None, max_length=100, null=True, blank=True), keep_default=False)

        # Deleting field 'Snippet.user_email'
        db.delete_column('commentbin_snippet', 'user_email')

        # Adding field 'Snippet.formatted_html'
        db.add_column('commentbin_snippet', 'formatted_html', self.gf('django.db.models.fields.TextField')(default=None, null=True, blank=True), keep_default=False)

        # Adding field 'Snippet.nick'
        db.add_column('commentbin_snippet', 'nick', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True), keep_default=False)

        # Adding field 'Snippet.public_comments'
        db.add_column('commentbin_snippet', 'public_comments', self.gf('django.db.models.fields.BooleanField')(default=True), keep_default=False)

        # Adding field 'Snippet.visible_to_public'
        db.add_column('commentbin_snippet', 'visible_to_public', self.gf('django.db.models.fields.BooleanField')(default=True), keep_default=False)

        # Adding field 'Snippet.access_token'
        db.add_column('commentbin_snippet', 'access_token', self.gf('django.db.models.fields.CharField')(default=None, max_length=100, null=True, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Adding field 'Comment.user_email'
        db.add_column('commentbin_comment', 'user_email', self.gf('django.db.models.fields.EmailField')(default='anonymous@anonymous.org', max_length=75), keep_default=False)

        # Deleting field 'Comment.nick'
        db.delete_column('commentbin_comment', 'nick')

        # Deleting field 'Comment.access_token'
        db.delete_column('commentbin_comment', 'access_token')

        # Adding field 'Snippet.user_email'
        db.add_column('commentbin_snippet', 'user_email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True), keep_default=False)

        # Deleting field 'Snippet.formatted_html'
        db.delete_column('commentbin_snippet', 'formatted_html')

        # Deleting field 'Snippet.nick'
        db.delete_column('commentbin_snippet', 'nick')

        # Deleting field 'Snippet.public_comments'
        db.delete_column('commentbin_snippet', 'public_comments')

        # Deleting field 'Snippet.visible_to_public'
        db.delete_column('commentbin_snippet', 'visible_to_public')

        # Deleting field 'Snippet.access_token'
        db.delete_column('commentbin_snippet', 'access_token')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'commentbin.comment': {
            'Meta': {'ordering': "['start', 'end']", 'object_name': 'Comment'},
            'access_token': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'end': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nick': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'snippet': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['commentbin.Snippet']"}),
            'start': ('django.db.models.fields.IntegerField', [], {}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"})
        },
        'commentbin.snippet': {
            'Meta': {'ordering': "['creation_date']", 'object_name': 'Snippet'},
            'access_token': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'code': ('django.db.models.fields.TextField', [], {}),
            'commented_html': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'formatted_html': ('django.db.models.fields.TextField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nick': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'public_comments': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'visible_to_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['commentbin']
