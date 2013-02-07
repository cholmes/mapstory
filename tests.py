from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from geonode.maps.models import Layer
from geonode.maps.models import Map
from geonode.maps.models import MapLayer
from geonode.simplesearch import models as simplesearch
import mapstory.social_signals # this just needs activating but is not used
from mapstory import forms
from mapstory.models import UserActivity
from mapstory.models import ProfileIncomplete
from mapstory.templatetags import mapstory_tags

from agon_ratings.models import Rating
from actstream.models import Action
from dialogos.models import Comment
from mailer import engine as email_engine

# these can just get whacked
simplesearch.map_updated = lambda **kw: None
simplesearch.object_created = lambda **kw: None
Layer.delete_from_geoserver = lambda self: None

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

    def test_activity_item_tag(self):
        lyr = Layer.objects.create(owner=self.bobby, name='layer1',typename='layer1', title='example')
        lyr.publish.status = 'Public'
        lyr.publish.save()

        comment_on(lyr, self.bobby, 'a comment')
        expected = ("http://localhost:8000/mapstory/storyteller/bobby (bobby)"
        " commented on http://localhost:8000/data/layer1 (the StoryLayer 'example')"
        " [ 0 minutes ago ]")
        actual = mapstory_tags.activity_item(self.bobby.actor_actions.all()[0], plain_text=True)
        self.assertEqual(expected, actual)

        rate(lyr, self.bobby, 4)
        expected = ("http://localhost:8000/mapstory/storyteller/bobby (bobby)"
        " gave http://localhost:8000/data/layer1 (the StoryLayer 'example')"
        " a rating of 4 [ 0 minutes ago ]")
        actual = mapstory_tags.activity_item(self.bobby.actor_actions.all()[0], plain_text=True)
        self.assertEqual(expected, actual)

        lyr.delete()
        # it seems like comment objects are not deleted when the commented-on object
        # is deleted - test that the tag doesn't blow up
        # @todo is this somehow related to mptt in threaded comments?
        self.assertEqual(1, len(self.bobby.actor_actions.all()))
        for a in self.bobby.actor_actions.all():
            self.assertEqual('', mapstory_tags.activity_item(a))

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


def comment_on(obj, user, comment, reply_to=None):
    ct = ContentType.objects.get_for_model(obj)
    return Comment.objects.create(author=user, content_type=ct, object_id=obj.id,
        comment=comment, parent=reply_to)


def rate(obj, user, rating):
    ct = ContentType.objects.get_for_model(obj)
    return Rating.objects.create(user=user, content_type=ct, object_id=obj.id,
        rating=rating)


class ContactDetailTests(TestCase):

    c = Client()

    def test_incomplete_profile(self):
        u = User.objects.create(username='billy')
        # this will fail if not incomplete, no need for assertions
        ProfileIncomplete.objects.get(user = u)

        # now fill stuff out
        p = u.get_profile()
        u.first_name = 'Billy'
        u.last_name = 'Bob'
        u.save()
        p.update_audit()
        # still incomplete
        ProfileIncomplete.objects.get(user = u)

        p.blurb = 'I Billy Bob'
        p.save()
        p.update_audit()
        # still incomplete
        ProfileIncomplete.objects.get(user = u)

        # add avatar
        a = u.avatar_set.model(user=u)
        a.save()
        u.avatar_set.add(a)
        p.update_audit()
        # finally
        self.assertEqual(0, ProfileIncomplete.objects.filter(user = u).count())


    def test_profile_form(self):
        u = User.objects.create(username='billy')
        form = forms.ProfileForm(data={}, instance = u.get_profile())
        self.assertTrue(not form.is_valid())

        # first, last, blurb work
        form = forms.ProfileForm(data={'first_name':'Billy','last_name':'Bob','blurb':'I Billy Bob'}, instance = u.get_profile())
        self.assertTrue(form.is_valid())
        form.save()
        # computed name field
        self.assertEqual('Billy Bob', u.get_profile().name)

