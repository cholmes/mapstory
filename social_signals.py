from django.db.models.signals import post_save
from django.db.models.signals import m2m_changed
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.template import loader
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from geonode.maps.models import Layer
from geonode.maps.models import Map
from geonode.maps.models import map_changed_signal
from mapstory.models import PublishingStatus
from mapstory.models import ContactDetail
from mapstory.models import UserActivity
from mapstory.templatetags import mapstory_tags

from flag.signals import content_flagged
from dialogos.models import Comment
from agon_ratings.models import Rating
from mapstory.util import user
from mailer import send_html_mail
from social_auth.backends.facebook import FacebookBackend
from social_auth.backends.twitter import TwitterBackend
from social_auth.backends import google
import datetime
import urllib2
from urlparse import urlparse
import logging

_logger = logging.getLogger('mapstory.social_signals')

def activity_summary(actions, plain_text=False):
    sep = "\n" if plain_text else "<br/>"
    return sep.join([mapstory_tags.activity_item(a, plain_text) for a in actions])


def batch_notification(days=1):
    for u in User.objects.filter(useractivity__notification_preference='S'):
        day_ago = datetime.datetime.now() - datetime.timedelta(days=days)
        actions = u.useractivity.other_actor_actions.filter(timestamp_gte=day_ago)
        if not actions: continue
        send_html_mail("[MapStory] Daily Summary Notification",
                       message=activity_summary(actions, plain_text=True),
                       message_html=activity_summary(actions),
                       from_email="do-not-reply@mapstory.org", 
                       recipient_list=[user.email])


def notify_handler(sender, instance, action, model, pk_set, **kwargs):
    if action != 'post_add': return
    if instance.notification_preference != 'E':
        return
    assert len(pk_set) == 1
    real_action = getattr(model,'objects').get(id=iter(pk_set).next())
    send_html_mail("[MapStory] Notification", 
                   message=mapstory_tags.activity_item(real_action, plain_text=True),
                   message_html=mapstory_tags.activity_item(real_action),
                   from_email="do-not-reply@mapstory.org", 
                   recipient_list=[instance.user.email])
    

def action(actor, verb, action_object=None, target=None, public=True):
    '''using the signal api doesn't give us a ref to the new action...'''
    # this'll cause some circular dep problems...
    from actstream.models import Action
    newaction = Action(
        actor_content_type=ContentType.objects.get_for_model(actor),
        actor_object_id=actor.pk,
        verb=unicode(verb),
        public=public,
        timestamp=datetime.datetime.now())
    if action_object:
        newaction.action_object = action_object
        newaction.action_object_content_type = ContentType.objects.get_for_model(action_object)
    if target:
        newaction.target = target
        newaction.target_content_type = ContentType.objects.get_for_model(target)
    newaction.save()
    return newaction


def action_handler(create_verb='created', update_verb='updated', provide_user=True):
    def handler(sender, instance, created, **kwargs):
        if created and not create_verb:
            return
        try:
            publish = getattr(instance, 'publish', None)
        except PublishingStatus.DoesNotExist:
            publish = None
        if publish and publish.status != 'Public':
            return
        active_verb = create_verb if created else update_verb
        actor = instance
        action_object = None
        if provide_user:
            actor = user()
            if not actor:
                # a non request caused this
                return
            action_object = instance
        action(actor, verb=active_verb, action_object=action_object)
    return handler


def register_save_handler(model, **kwargs):
    handler = action_handler(**kwargs)
    post_save.connect(handler, sender=model, weak=False)


def rating_handler(sender, instance, created, **kwargs):
    # fall back on the rating user if no request user is found (for tests)
    actor = user() or instance.user
    target = instance.content_object
    act = action(actor, verb='rated', action_object=instance, target=target)
    if actor != target.owner:
        target.owner.useractivity.other_actor_actions.add(act)


def comment_handler(sender, instance, created, **kwargs):
    actor = instance.author
    if not actor: return
    target = instance.content_object # object being commented on (map/layer)
    parent = instance.parent # possible parent comment

    if created:
        verb = 'commented'
        if parent:
            verb = 'replied'
        act = action(actor, verb=verb, action_object=instance, target=parent)
    else:
        act = action(actor, verb='edited', action_object=instance, target=target)

    # track this activity - too expensive to query this out after the fact
    # only track if the comment is 
    # a) on someone elses layer/map or
    if actor != target.owner:
        target.owner.useractivity.other_actor_actions.add(act)
    # b) in reply to someone elses comment
    elif parent and actor != parent.author:
        parent.author.useractivity.other_actor_actions.add(act)


def publishing_handler(sender, instance, created, **kw):
    if instance.status == 'Public':
        what = instance.map or instance.layer
        action(what.owner, 'published', action_object=what)
        layers = getattr(what, 'local_layers', [])
        for l in layers:
            if l.owner != what.owner:
                # make this hidden so it doesn't show up
                act = action(what.owner, verb='published', action_object=l,
                       target=what, public=False)
                # except here
                l.owner.useractivity.other_actor_actions.add(act)


def map_handler(sender, what_changed, old, new, **kw):
    if what_changed == 'layers' and sender.publish.status == 'Public':
        added = old ^ new
        layers = Layer.objects.filter(typename__in=added)
        for l in layers:
            act = action(sender.owner, verb='added', action_object=l, 
                         target=sender)
            # if the layer owner is not the map owner, tell the layer owner
            if l.owner != sender.owner:
                l.owner.useractivity.other_actor_actions.add(act)


def flag_handler(flagged_instance, flagged_content, **kw):
    target = flagged_content.content_object
    get_absolute_url = getattr(target, 'get_absolute_url', None)
    recps = User.objects.filter(is_staff=True).exclude(email='').exclude(email__isnull=True)
    link = get_absolute_url() if get_absolute_url else ''
    message = loader.render_to_string("flag/email.txt", {
        'flag' : flagged_instance,
        'url' : link,
        'display' : '%s[%s]' % (target._meta.object_name, target.id)
    })
    for u in recps:
        u.email_user('mapstory flagged content', message)

def get_user_avatar(backend, details, response, social_user, uid,\
                    user, *args, **kwargs):
    url = None
    if backend.__class__ == FacebookBackend:
        url = "http://graph.facebook.com/%s/picture?type=large" % response['id']

    elif backend.__class__ == TwitterBackend:
        url = response.get('profile_image_url', '').replace('_normal', '')

    elif backend.__class__  == google.GoogleOAuth2Backend and "picture" in response:
        url = response["picture"]

    if url:
        name = urlparse(url).path.split('/')[-1]
        img_temp = NamedTemporaryFile(delete=True)
        img_temp.write(urllib2.urlopen(url).read())
        img_temp.flush()
        try:
                a = user.avatar_set.get()
        except:
                a = user.avatar_set.model(user=user)
        a.avatar.save(name, File(img_temp))
        user.avatar_set.add(a)

register_save_handler(ContactDetail, create_verb='joined MapStory', provide_user=False)
register_save_handler(Layer, create_verb='uploaded')
register_save_handler(Map)
map_changed_signal.connect(map_handler)
post_save.connect(publishing_handler, sender=PublishingStatus)
post_save.connect(rating_handler, sender=Rating)
post_save.connect(comment_handler, sender=Comment)

m2m_changed.connect(notify_handler, sender=UserActivity.other_actor_actions.through)

content_flagged.connect(flag_handler)
