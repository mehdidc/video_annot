from django import template

register = template.Library()

@register.filter
def process_url(url):
    if url.startswith('http') or url.startswith('ftp'):
        return url
    elif url.startswith('/'):
        return url
    else:
        return '/static/annotator/{}'.format(url)

@register.filter
def label_to_question(label):
    label = ' '.join(label.split('_'))
    return 'Is there a {} ?'.format(label)
