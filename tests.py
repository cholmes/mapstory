from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from geonode.maps.models import Layer
from geonode.maps.models import Map
from geonode.maps.models import MapLayer
from geonode.simplesearch import models as simplesearch
import mapstory.social_signals # this just needs activating but is not used
from mapstory.models import UserActivity

from actstream.models import Action
from dialogos.models import Comment
from mailer import engine as email_engine

# these two can just get whacked
simplesearch.map_updated = lambda **kw: None
simplesearch.object_created = lambda **kw: None

class SocialTest(TestCase):
    
    fixtures = ['test_data.json','map_data.json']
    @classmethod
    def setUpClass(cls):
        cls._old_verify = Layer.verify
        cls._old_save_to_geoserver = Layer.save_to_geoserver
        Layer.verify = lambda s: None
        Layer.save_to_geoserver = lambda s: None

    @classmethod
    def tearDownClass(cls):
        Layer.verify = cls._old_verify
        Layer.save_to_geoserver = cls._old_save_to_geoserver
        
    def setUp(self):
        self.bobby = User.objects.get(username='bobby')
        self.admin = User.objects.get(username='admin')

    def test_social_map_layer_actions(self):
        Layer.objects.create(owner=self.bobby, name='layer1',typename='layer1')
        bobby_layer = Layer.objects.create(owner=self.bobby, name='layer2', typename='layer2')
        # no activity yet, still Private
        self.assertFalse(self.bobby.actor_actions.all())
        
        # lets publish it
        bobby_layer.publish.status = 'Public'
        bobby_layer.publish.save()
        actions = self.bobby.actor_actions.all()
        # there should be a single action
        self.assertEqual(1, len(actions))
        self.assertEqual('bobby published layer2 Layer 0 minutes ago', str(actions[0]))
        
        # now create a map
        admin_map = Map.objects.create(owner=self.admin, zoom=1, center_x=0, center_y=0, title='map1')
        # have to use a 'dummy' map to create the appropriate JSON
        dummy = Map.objects.get(id=admin_map.id)
        dummy.id += 1
        dummy.save()
        MapLayer.objects.create(name = 'layer1', ows_url='layer1', map=dummy, stack_order=1)
        # and 'add' the layer
        admin_map.update_from_viewer(dummy.viewer_json())
        # no activity yet, still Private
        self.assertFalse(self.admin.actor_actions.all())
        
        # lets publish it and ensure things work
        self.bobby.useractivity.other_actor_actions.clear()
        admin_map.publish.status = 'Public'
        admin_map.publish.save()
        # there should be a single 'public' action (the other exists so it can hang on bobby)
        actions = self.admin.actor_actions.public()
        self.assertEqual(1, len(actions))
        self.assertEqual('admin published map1 by admin 0 minutes ago', str(actions[0]))
        # and a single action for bobby
        actions = self.bobby.useractivity.other_actor_actions.all()
        self.assertEqual(1, len(actions))
        self.assertEqual('admin published layer1 Layer on map1 by admin 0 minutes ago', str(actions[0]))
        
        # already published, add another layer and make sure it shows up in bobby
        self.bobby.useractivity.other_actor_actions.clear()
        MapLayer.objects.create(name = 'layer2', ows_url='layer2', map=dummy, stack_order=2)
        admin_map.update_from_viewer(dummy.viewer_json())
        actions = self.bobby.useractivity.other_actor_actions.all()
        self.assertEqual(1, len(actions))
        self.assertEqual('admin added layer2 Layer on map1 by admin 0 minutes ago', str(actions[0]))
        
    def drain_mail_queue(self):
        # mailer doesn't play well with default mail testing
        mails = []
        for m in email_engine.prioritize():
            mails.append(m)
            m.delete()
        return mails
        
    def test_no_notifications(self):
        prefs = UserActivity.objects.get(user=self.bobby)
        prefs.notification_preference = 'S'
        
        layer = Layer.objects.create(owner=self.bobby, name='layer1',typename='layer1')
        comment_on(layer, self.admin, "This is great")
        
        prefs.notification_preference = 'E'
        prefs.save()
        comment_on(layer, self.admin, "This is great")
        
        mail = self.drain_mail_queue()
        self.assertEqual(1, len(mail))
        print vars(mail[0].email)
        

def comment_on(obj, user, comment, reply_to=None):
    ct = ContentType.objects.get_for_model(obj)
    return Comment.objects.create(author=user, content_type=ct, object_id=obj.id,
        comment=comment, parent=reply_to)