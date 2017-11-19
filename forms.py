from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.core.exceptions import ImproperlyConfigured
from functools import update_wrapper
from django.utils.decorators import classonlymethod

from django.utils.safestring import mark_safe
from django.utils import html
# required
# get object
# how  delete

# optional
# return mesage
# redirect
# confirm form
def tmpl_instance_message(msg, title):
  '''Template for a message or title about an model instance'''
  return mark_safe('{0} <i>{1}</i>.'.format(msg, html.escape(title)))
  

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
    return mark_safe('<a href="{0}" {1}/>{2}</a>'.format(
        html.escape(href),
        ' '.join(b),
        html.escape(text)


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
    for k,v in attrs.items():
        b.append('{0}={1}'.format(k, v))
    return mark_safe('<input name="{0}" value={1} type="submit" {2}>'.format(
        html.escape(name),
        html.escape(value),
        ' '.join(b)
        ))        
        
        
        
class View:

    def view(request, *args, **kwargs):
        raise ImproperlyConfigured('View must be configured by inherriance with a View method')

    @classonlymethod
    def as_view(cls, **initkwargs):
        """Main entry point for a request-response process."""
        for key in initkwargs:
            if not hasattr(cls, key):
                raise TypeError("%s() received an invalid keyword %r. as_view "
                                "only accepts arguments that are already "
                                "attributes of the class." % (cls.__name__, key))
                                
                                
        self.view(request, *args, **kwargs)

        view.view_class = cls
        view.view_initkwargs = initkwargs

        # take name and docstring from class
        update_wrapper(view, cls, updated=())

        # and possible attributes set by decorators
        # like csrf_exempt from dispatch
        #update_wrapper(view, cls.dispatch, assigned=())
        return view
        
        
          
#? FormView
class ModelViewDelete(View):
    ???
    # required
    model = None
    object_title_field = None 
    # can be none
    success_redirect = #self admin_reverse('term', 'changelist', args=[bpk])
    object_get_fail_redirect = # self admin_reverse('base', 'changelist')
    
    # defaulted
    success_redirect = #self admin_reverse('term', 'changelist', args=[bpk])
    confirm_template = 'genericviewsimple/delete_confirm_form.html'

    # optional
    confirm_message_directions = '<p>Deleting a term will delete all its term children if there are any. This action cannot be undone.</p><p>(deleting a term will not delete elements attached to the term. However, attached elements will be removed from the taxonomies)</p>'
    
    #def __new__()
    #test the field is in the model
    # and title field not empty
    
    def __init__(self, **kwargs):
        setattr(self, )
        if (not self.model):
            raise ImproperlyConfigured('ModelViewDelete must be configured with a Model')
        if (not self.model):
            raise ImproperlyConfigured('ModelViewDelete must be configured with an object_title_field attribute')
        self.model_name = self.model._meta.object_name
        

    def get_objects(pk):
        raise ImproperlyConfigured('ModelViewDelete must be configured with a get_objects() method')

    def delete_object(objs):
        raise ImproperlyConfigured('ModelViewDelete must be configured with a delete_object() method')
        
    def cancel_url(self, objs):
        raise ImproperlyConfigured('ModelViewDelete must be configured with a cancel_url() method')
        
    def view(request, *args, **kwargs):
        pk = '19'
        #like this, or can we deduce it?
        self_url = request.get_full_path()
        
        try:
            objs = self.get_objects(pk)
        except Exception:
            msg = "<b>{0}</b> with ID '{1}' doesn't exist. Perhaps it was deleted?".format(
                self.model_name,
                pk
            )
            messages.add_message(request, messages.WARNING, msg) 
            
            rd = self.object_get_fail_redirect if self.object_get_fail_redirect else self_url
            return HttpResponseRedirect(rd)
              
        object_title = html.escape(obj[object_title_field])

        
        if (request.method == 'POST'):
            self.delete_object(objs)
            msg = 'Deleted "{0}"',format(self.model_name)
            messages.add_message(request, messages.SUCCESS, msg)
            rd = self.success_redirect if self.success_redirect else self_url
            return HttpResponseRedirect(rd)
        else:
            msg = '<p>Are you sure you want to delete the {0} "{1}"?</p>{2}'.format(
                self.model_name,    
                object_title,
                self.confirm_message_directions
            ) 
            context={
              'title': mark_safe('Delete {0}'.format(object_title)),
              'message': mark_safe(msg),
              #'submit': {},
              'actions': [
              submit('message':"Yes, I'm sure", 'url': self_url),
              link('No, take me back', cancel_url(objs), attrs={'class':'"button"'})
              ],
            } 
            return render(request, confirm_template, context)


        
        
        
# This is confirm?
#def _term_delete(request, term_pk):
    #tapi = api.TermAPI(term_pk)
    #try:
        #tm = tapi.term()
    #except Term.DoesNotExist:
        #msg = "Term with ID '{0}' doesn't exist. Perhaps it was deleted?".format(
            #term_pk
        #)
        #messages.add_message(request, messages.WARNING, msg) 
        #return HttpResponseRedirect(admin_reverse('base', 'changelist'))
    #bpk = tapi.base_pk()
      
    #if (request.method == 'POST'):
        #tapi.delete()
        #msg = tmpl_instance_message("Deleted Term", tm.title)
        #messages.add_message(request, messages.SUCCESS, msg)
        #return HttpResponseRedirect(admin_reverse('term', 'changelist', args=[bpk]))
    #else:
        #message = '<p>Are you sure you want to delete the Term "{0}"?</p><p>Deleting a term will delete all its term children if there are any. This action cannot be undone.</p><p>(deleting a term will not delete elements attached to the term. However, attached elements will be removed from the taxonomies)</p>'.format(
          #html.escape(tm.title)
          #)
        #context={
          #'title': tmpl_instance_message("Delete term", tm.title),
          #'message': mark_safe(message),
          #'submit': {'message':"Yes, I'm sure", 'url': admin_reverse('term', 'delete', args=[tm.pk])},
          #'actions': [link('No, take me back', admin_reverse('term', 'change', args=[tm.pk]), attrs={'class':'"button"'})],
        #} 
        #return render(request, 'taxonomy/delete_confirm_form.html', context)


        
#def term_delete(request, term_pk):
    #with transaction.atomic(using=router.db_for_write(Term)):
      #return _term_delete(request, term_pk)
  
