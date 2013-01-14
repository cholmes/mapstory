from mapstory.models import get_view_cnts
from mapstory.models import get_ratings
from mapstory.models import Topic
from mapstory.models import Section
from mapstory.models import ContactDetail
from mapstory.models import ProfileIncomplete

from geonode.maps.models import Layer
from geonode.maps.models import Map

display_names = {
    'map' : 'MapStory',
    'layer' : 'StoryLayer',
    'user' : 'StoryTeller'
}

def extra_context(context):
    context['sections'] = Section.objects.all()
    
def process_search_results(normalizers):
    '''Generic content types are _much_ faster to deal with in bulk'''
    if not normalizers: return normalizers
    model = type(normalizers[0].o)
    cnts = get_view_cnts(model)
    ratings = get_ratings(model)
    for n in normalizers:
        n.views = cnts.get(n.o.id, 0)
        n.rating = float(ratings.get(n.o.id, 0))
    return normalizers

owner_query_fields = ['blurb','organization','biography']
    
def owner_query(query, kw):
    if kw['bysection']: return None
    q = ContactDetail.objects.select_related().filter(user__isnull=False)
    q = q.exclude(user__id__in=ProfileIncomplete.objects.all().values('user'))
    q = q.defer('blurb', 'biography')
    return q

def owner_rank_rules():
    return (ContactDetail,
           ['blurb', 5, 2],
           ['biography', 5, 2])

def _initial_query(model, kw):
    user = kw['user']
    if user and user.is_superuser:
        q = model.objects.all()
    else:
        q = model.objects.filter(publish__status='Public')
        if user:
            q = q | model.objects.filter(owner=user)
    return q
    

def layer_query(query, kw):
    q = _initial_query(Layer, kw)
    q = q.only('title','date')
    bysection = kw.get('bysection')
    if bysection:
        q = q.filter(topic__in=Topic.objects.filter(section__id=bysection))
    # @todo once supported via UI - this should be an OR with the section filter
    bytopic = kw.get('bytopic')
    if bytopic:
        q = q.filter(topic_category = bytopic)
    return q


def map_query(query, kw):
    q = _initial_query(Map, kw)
    q = q.only('title','last_modified')

    bysection = kw.get('bysection')
    if bysection:
        q = q.filter(topic__in=Topic.objects.filter(section__id=bysection))

    return q