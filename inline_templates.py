from django.utils.safestring import mark_safe
from django.utils import html
from django.urls import reverse


def link(text, href, attrs={}):
    '''
    Build HTML for a anchor/link.
    
    @param title escaped
    @param href escaped
    @param attrs dict of HTML attributes. Not escaped
    '''
    #NB 'attrs' can not use kwargs because may want to use reserved words
    # for keys, such as 'id' and 'class'
    b = []
    for k,v in attrs.items():
        b.append('{0}={1}'.format(k, v))
    return mark_safe('<div><a href="{0}" {1}/>{2}</a></div>'.format(
        html.escape(href),
        ' '.join(b),
        html.escape(text)
    ))

def submit(value, name, attrs={}):
    '''
    Build HTML for a anchor/link.
    
    @param title escaped
    @param name escaped
    @param attrs dict of HTML attributes. Not escaped
    '''
    #NB 'attrs' can not use kwargs because may want to use reserved words
    # for keys, such as 'id' and 'class'
    b = []
    #! name is optional?
    for k,v in attrs.items():
        b.append('{0}={1}'.format(k, v))
    return mark_safe('<input name="{0}" value="{1}" type="submit" {2}>'.format(
        name,
        value,
        ' '.join(b)
        ))        

def link_action(text, href, attrs={}, right_align=False):
    '''
    Build HTML for a anchor/link.
    
    @param title escaped
    @param href escaped
    @param attrs dict of HTML attributes. Not escaped
    '''
    #NB 'attrs' can not use kwargs because may want to use reserved words
    # for keys, such as 'id' and 'class'
    b = []
    list_class = ''
    if (right_align):
        list_class = 'class="right"'
    for k,v in attrs.items():
        b.append('{0}={1}'.format(k, v))
    return mark_safe('<li {0}><a href="{1}" {2}/>{3}</a></li>'.format(
        list_class,
        html.escape(href),
        ' '.join(b),
        html.escape(text)
    ))
    
def submit_action(value, attrs={}, right_align=False):
    '''
    Build HTML for a anchor/link.
    
    @param title escaped
    @param name escaped
    @param attrs dict of HTML attributes. Not escaped
    '''
    #NB 'attrs' can not use kwargs because may want to use reserved words
    # for keys, such as 'id' and 'class'
    b = []

    list_class = ''
    if (right_align):
        list_class = 'class="right"'
        
    for k,v in attrs.items():
        b.append('{0}={1}'.format(k, v))
    return mark_safe('<li {0}><input value="{1}" type="submit" {2}><li>'.format(
        list_class,
        value,
        ' '.join(b)
        )) 

        
def tmpl_instance_message(msg, title):
    '''Template for a message or title about an model instance'''
    return mark_safe('{0} {1}.'.format(msg, html.escape(title)))


def admin_reverse(model_name, url_pattern_name, args=None):
    return reverse('admin:taxonomy_{0}_{1}'.format(model_name, url_pattern_name), args=args)

def admin_reverse2(app_name, model_name, url_pattern_name, args=None):
    return reverse('admin:{0}_{1}_{2}'.format(app_name, model_name, url_pattern_name), args=args)
            
