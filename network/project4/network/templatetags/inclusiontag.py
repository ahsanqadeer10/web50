from django import template

register = template.Library()

@register.inclusion_tag('network/posts.html', takes_context=True)
def display_posts(context):
    return {"posts_page": context['posts_page'],
            "user": context['user']
            }