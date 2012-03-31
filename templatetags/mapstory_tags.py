from django import template
from django.template import loader

register = template.Library()

@register.tag
def map_info_tile(parser, token):
    try:
        tag_name, obj_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires a single argument" % token.contents.split()[0]
    return MapInfoTileNode(obj_name)

class MapInfoTileNode(template.Node):
    def __init__(self, obj_name):
        self.obj_name = obj_name
    def render(self, context):
        obj = context[self.obj_name]
        return loader.render_to_string("mapstory/_tag_story_tiles.html",{'map':obj})