# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):
    def forwards(self, orm):
        # Adding model 'FriendshipSuggestion'
        db.create_table('friends_suggestions_friendshipsuggestion', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('from_user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='suggestions_from',
                                                                                to=orm['auth.User'])),
            ('to_user',
             self.gf('django.db.models.fields.related.ForeignKey')(related_name='suggestions_to', to=orm['auth.User'])),
            ('added', self.gf('django.db.models.fields.DateTimeField')(
                default=datetime.datetime(2012, 4, 4, 23, 22, 21, 885434))),
        ))
        db.send_create_signal('suggestions', ['FriendshipSuggestion'])

        # Adding unique constraint on 'FriendshipSuggestion', fields ['to_user', 'from_user']
        db.create_unique('friends_suggestions_friendshipsuggestion', ['to_user_id', 'from_user_id'])

        # Adding model 'ImportedContact'
        db.create_table('friends_suggestions_importedcontact', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='imported_contacts',
                                                                            to=orm['auth.User'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('added', self.gf('django.db.models.fields.DateTimeField')(
                default=datetime.datetime(2012, 4, 4, 23, 22, 21, 883400))),
        ))
        db.send_create_signal('suggestions', ['ImportedContact'])

    def backwards(self, orm):
        # Removing unique constraint on 'FriendshipSuggestion', fields ['to_user', 'from_user']
        db.delete_unique('friends_suggestions_friendshipsuggestion', ['to_user_id', 'from_user_id'])

        # Deleting model 'FriendshipSuggestion'
        db.delete_table('friends_suggestions_friendshipsuggestion')

        # Deleting model 'ImportedContact'
        db.delete_table('friends_suggestions_importedcontact')

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [],
                            {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')",
                     'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': (
                'django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [],
                       {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [],
                                 {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)",
                     'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'suggestions.friendshipsuggestion': {
            'Meta': {'unique_together': "[('to_user', 'from_user')]", 'object_name': 'FriendshipSuggestion',
                     'db_table': "'friends_suggestions_friendshipsuggestion'"},
            'added': ('django.db.models.fields.DateTimeField', [],
                      {'default': 'datetime.datetime(2012, 4, 4, 23, 22, 21, 894183)'}),
            'from_user': ('django.db.models.fields.related.ForeignKey', [],
                          {'related_name': "'suggestions_from'", 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'to_user': ('django.db.models.fields.related.ForeignKey', [],
                        {'related_name': "'suggestions_to'", 'to': "orm['auth.User']"})
        },
        'suggestions.importedcontact': {
            'Meta': {'object_name': 'ImportedContact', 'db_table': "'friends_suggestions_importedcontact'"},
            'added': ('django.db.models.fields.DateTimeField', [],
                      {'default': 'datetime.datetime(2012, 4, 4, 23, 22, 21, 892352)'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [],
                      {'related_name': "'imported_contacts'", 'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['suggestions']
