from django.views import generic
from django.contrib import messages
from django.http import HttpResponseRedirect

from .inline_templates import *



# + steps
# before_action
# fail_action
# unbound_action
# success_redirect_url
# + want
# customisable before, save
# + also
# template
# page_title
# confirm_message
# succeed_message
# fail_message
# model
# object_title_field

from django.views import generic
from django.forms import models as model_forms
from django.core.exceptions import ImproperlyConfigured

from .detail import (
    SingleObjectMixin,
    SingleObjectContextMixin, 
    SingleModelObjectMixin, 
    SingleModelObjectContextMixin
    )
    

#! the context here is layered. How can we drop admin context, but keep
# the rest? add_default_context?
# + modified with 
# querysets replaced with simple get_object()
# success_action/fail_action hooks
# messages
# title handling
# return_url() absolute_url() 
# default templates
# stock contexts

class GetView(generic.base.TemplateView):
    '''
    A View that only accepts GET method requests.
    In Django, this can be done with a few lines of code. But this view
    uses a form from the Django Form(builder). It also uses the 
    default templates, and has an API consistent with the other views. 
    
    The handling has no auto-validation. If you want to create a 
    multi-field search-> results scheme, as used by academic engines,
    use a 'create' type view from this app or elsewhere. Then you will 
    get validation too.
    
    The view is also not helpful if you wish to create an end-user 
    experience like a general search engine. This view requires too
    much overriding.
     
    You would use it if you wished to stay (mostly) within the 
    generic styling and construction system. And are looking for a
    quick redirect, or a repeat-submission visual display.

    To aid repeat-submission usage, the default template has an extra 
    'div' in the content. This can be populated e.g. ::
    
            context['data_display'] = 'something like search results'     

    Notes:
    - If the form is used for cycling (e.g. a search form), the render 
    will need a form with a GET submission method, not POST (the default
    template has a GET method).
    - For a form with repeat GET, it can upset user workflow if the 
    form is restrictive. You should probably set 'required=False' on form 
    fields, unless you have good reason not to.
    - The class has a method, before_render_action(). This runs after 
    the context is built, but before rendering. This hook method is 
    intended for logic such as display retrieval, and to separate such
    code from context building.
    - To recover data fromm the form use e.g. self.request.GET.get(<fieldname>, None)
    - has_changed
    
    '''
    template_name = 'simple_views/generic_get_form.html'
    initial = {}
    form_class = None
    prefix = None
    '''When True (default), will add user values back to the form. When
    False, the form is repopulated with 'initial' attribute values.
    '''
    repopulate_on_submit = True
    display_title = 'Input {0}'
    '''
    Add context definitions used by the default template. 
    Default is True.
    '''
    add_default_context = True
    
    def get_initial(self):
        """Return the initial data to use for forms on this view."""
        return self.initial.copy()

    def get_prefix(self):
        """Return the prefix to use for forms."""
        return self.prefix

    def get_form_class(self):
        """Return the form class to use."""
        return self.form_class

    def get_form(self, form_class=None):
        """Return an instance of the form to be used in this view."""
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(**self.get_form_kwargs())

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = {
            'initial': self.get_initial(),
            'prefix': self.get_prefix(),
        }
        return kwargs

    def get_return_url(self):
        return self.request.get_full_path()
        
    def get_success_url(self):
        """Return the URL to redirect to after processing a valid form."""
        if self.success_url:
            # success_url may be lazy
            url = str(self.success_url)
        else:
            url = get_return_url()
        return url 

    def before_render_action(self, context):
        ''' 
        Hook action run after context construction.
        Intended to gather and separate logic (e.g. information 
        gathering) from context work.
        ''' 
        pass
        
    def get(self, request, *args, **kwargs):
        if (self.repopulate_on_submit):
            self.initial = self.request.GET
        ctx = self.get_context_data(**kwargs)
        self.before_render_action(ctx)
        return self.render_to_response(ctx)

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        kwargs['form'] = self.get_form()
        if (self.add_default_context):
            kwargs.update({
            'navigators': [],
            'actions': [
              submit_action("Save", attrs={'class':'"button primary"'}),
            ],
            })                  
        return super().get_context_data(**kwargs)
        


class SuccessFailMixin:
    success_url = None
    display_title = 'Modify {0}'
    success_message = 'Modified {0}'
        
    def success_action(self, form):
        '''
        Hook for success.
        @return (usually modified) data
        '''
        raise ImproperlyConfigured('FormView must be configured with a success_action() method')

    def fail_action(self, form):
        '''
        Hook for failure.
        '''
        raise ImproperlyConfigured('FormView must be configured with a fail_action() method')

    def get_success_url(self):
        """Return the URL to redirect to after processing a valid form."""
            #? need to adapt.... 
            #! also admin_base if a model
            #? else self, but came from request?
            #!             rd = request.get_full_path()
        if not self.success_url:
            raise ImproperlyConfigured("No URL to redirect to. Provide a success_url.")
        # success_url may be lazy
        return str(self.success_url)



class FormMixin(generic.base.ContextMixin, SuccessFailMixin):
    """
    Show and handle a form in a request.
    (only useful for create/update)
    """
    initial = {}
    form_class = None
    prefix = None
    display_title = 'Create/Update {0}'
    success_message = 'Created/Updated {0}'

    def get_initial(self):
        """Return the initial data to use for forms on this view."""
        return self.initial.copy()

    def get_prefix(self):
        """Return the prefix to use for forms."""
        return self.prefix

    def get_form_class(self):
        """Return the form class to use."""
        return self.form_class

    def get_form(self, form_class=None):
        """Return an instance of the form to be used in this view."""
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(**self.get_form_kwargs())

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = {
            'initial': self.get_initial(),
            'prefix': self.get_prefix(),
        }

        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return kwargs

    def get_return_url(self):
        return self.request.get_full_path()
        
    def get_success_url(self):
        """Return the URL to redirect to after processing a valid form."""
        if not self.success_url:
            raise ImproperlyConfigured("No URL to redirect to. Provide a success_url.")
        return str(self.success_url)  # success_url may be lazy

    def form_valid(self, form):
        """If the form is valid, hook then redirect to the supplied URL."""
        self.object = self.success_action(form)
        # messages
        msg = self.success_message.format(self.get_display_name(self.object))
        messages.add_message(self.request, messages.SUCCESS, msg)
        return HttpResponseRedirect(self.get_success_url())
        
    def form_invalid(self, form):
        """If the form is invalid, hook then render the invalid form."""
        self.fail_action(form)
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super().get_context_data(**kwargs)



class DataFormMixin(FormMixin, SingleObjectContextMixin):
    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = super().get_form_kwargs()
        if hasattr(self, 'object'):
            kwargs.update({'instance': self.object})
        return kwargs
        
        
        
class ModelFormMixin(DataFormMixin, SingleModelObjectContextMixin):
    """
    Show and handle a ModelForm in a request.
    (only useful for create/update)
    """
    fields = None
    
    def get_form_class(self):
        """Return the form class to use in this view."""
        if ((self.fields is not None) and self.form_class):
            raise ImproperlyConfigured(
                "Specifying both 'fields' and 'form_class' is not permitted."
            )
            
        if self.form_class:
            return self.form_class
        else:
            if self.model is not None:
                # If a model has been explicitly provided, use it
                model = self.model
            else:
                self.verify_object_is_from_model()
                # If this view is operating on a single object, use
                # the class of that object
                model = self.object.__class__
                
            if self.fields is None:
                raise ImproperlyConfigured(
                    "Using ModelFormMixin (base class of %s) without "
                    "the 'fields' attribute is prohibited." % self.__class__.__name__
                )
            return model_forms.modelform_factory(model, fields=self.fields)

    def get_admin_base_url(self): 
        return '/admin/' + self.model._meta.app_label + '/' + self.model._meta.model_name
        
    def get_success_url(self):
        """Return the URL to redirect to after processing a valid form."""
            #! also admin_base if a model
            #? else self, but came from request?
        if self.success_url:
            url = self.success_url.format(**self.object.__dict__)
        else:
            try:
                url = self.object.get_absolute_url()
            except AttributeError:
                raise ImproperlyConfigured(
                    "No URL to redirect to.  Either provide a url or define"
                    " a get_absolute_url method on the Model.")
        return url

    def success_action(self, form):
        obj = form.save()
        return obj
             


class ProcessFormView(generic.View):
    """Render a form on GET and processes it on POST."""
    def get(self, request, *args, **kwargs):
        """Handle GET requests: instantiate a blank version of the form."""
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    # PUT is a valid HTTP verb for creating (with a known URL) or editing an
    # object, note that browsers only support POST for now.
    def put(self, *args, **kwargs):
        return self.post(*args, **kwargs)


######################
## Creates

class BaseCreateView(ProcessFormView, generic.detail.SingleObjectTemplateResponseMixin):
    """
    Base view for creating an new object instance.
    """
    template_name_suffix = '_create_form'
    template_name = 'simple_views/generic_form.html'
   
    def get(self, request, *args, **kwargs):
        self.object = None
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = None
        return super().post(request, *args, **kwargs)
        
        

class CreateView(FormMixin, BaseCreateView):
    display_title = 'Create {0}'
    success_message = "Created {0}"
    
    def get_context_data(self, **kwargs):
        kwargs.update({
        'navigators': [],
        'actions': [
          submit_action("Save", attrs={'class':'"button primary"'}, right_align=True),
        ],
        })
        group_name = self.get_object_model_name()
        if (group_name):
            kwargs['title'] = self.display_title.format(group_name)
        return super().get_context_data(**kwargs)
        
        

class ModelCreateView(ModelFormMixin, BaseCreateView):
    display_title = 'Create {0}'
    success_message = "Created {0}"
    
    def get_context_data(self, **kwargs):
        kwargs.update({
        'navigators': [],
        'actions': [
          submit_action("Save", attrs={'class':'"button primary"'}, right_align=True),
        ],
        })
        group_name = self.get_object_model_name()
        if (group_name):
            kwargs['title'] = self.display_title.format(group_name)
        return super().get_context_data(**kwargs)


#####################################
# Update
class BaseUpdateView(ProcessFormView, generic.detail.SingleObjectTemplateResponseMixin):
    """
    Base view for updating an existing object.
    """
    template_name_suffix = '_update_form'
    template_name = 'simple_views/generic_form.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)
        

class UpdateView(FormMixin, BaseUpdateView):
    """View for updating by any form, with a response rendered by a template."""
    display_title = 'Update {0}'
    success_message = "Updated {0}"

    def get_context_data(self, **kwargs):
        kwargs.update({
        'navigators': [],
        #'submit_url': request.get_full_path(),
        'actions': [
          submit_action("Update", attrs={'class':'"button primary"'}, right_align=True),
        ],
        })
        group_name = self.get_object_model_name()
        if (group_name):
            kwargs['title'] = self.display_title.format(group_name)
        return super().get_context_data(**kwargs)
      
      
      
class ModelUpdateView(ModelFormMixin, BaseUpdateView):
    """View for updating a model object, with a response rendered by a template."""
    display_title = 'Update {0}'
    success_message = "Updated {0}"

    def get_context_data(self, **kwargs):
        kwargs.update({
        'navigators': [],
        #'submit_url': request.get_full_path(),
        'actions': [
          submit_action("Update", attrs={'class':'"button primary"'}, right_align=True),
        ],
        })
        group_name = self.get_object_model_name()
        if (group_name):
            kwargs['title'] = self.display_title.format(group_name)
        return super().get_context_data(**kwargs)
        
        
      
###################################################
## confirm
class ProcessConfirmView(SuccessFailMixin, generic.View):
    """
    Handle a confirm form.
    Render on GET and process (a yes response) on POST.
    """
    display_title = 'Are you sure?'
    confirm_message = '<p>Are you sure you want to modify this data?</p>'
    
    def get(self, request, *args, **kwargs):
        """Handle GET requests: render the data."""
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: run a sucess action, message, then redirect.
        """
        self.object = self.success_action(None)
        # messages
        msg = self.success_message.format(self.get_object_name(self.object))
        messages.add_message(self.request, messages.SUCCESS, msg)
        return HttpResponseRedirect(self.get_success_url())

    # PUT is a valid HTTP verb for creating (with a known URL) or editing an
    # object, note that browsers only support POST for now.
    def put(self, *args, **kwargs):
        return self.post(*args, **kwargs)
        


class BaseConfirmView(ProcessConfirmView, generic.detail.SingleObjectTemplateResponseMixin):
    """
    Base view for updating an existing object.
    """
    template_name_suffix = '_confirm_form'
    template_name = 'simple_views/confirm_form.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

                
                
class ConfirmView(SingleObjectContextMixin, BaseConfirmView):
    display_title = 'Are you sure?'
    success_message = "Modified {0}"

    def get_context_data(self, **kwargs):
        kwargs.update({
          'message': mark_safe(self.confirm_message.format(self.get_object_model_name(),self.get_object_name(self.object))),
          #'submit_url': request.get_full_path(),
          'navigators': [],
          'actions': [
              submit_action(
                  "Yes, I'm sure",
                  attrs={'class':'"button alert"'}
              ),
          ]})
        group_name = self.get_object_model_name()
        if (group_name):
            kwargs['title'] = self.display_title.format(group_name)
        return super().get_context_data(**kwargs)
        
           

class ModelConfirmView(SingleModelObjectContextMixin, BaseConfirmView):
    display_title = 'Are you sure?'
    success_message = "Modified {0}"
    
    def get_context_data(self, **kwargs):
        kwargs.update({
          'message': mark_safe(self.confirm_message.format(self.get_object_model_name(),self.get_object_name(self.object))),
          #'submit_url': request.get_full_path(),
          'navigators': [],
          'actions': [
              submit_action(
                  "Yes, I'm sure",
                  attrs={'class':'"button alert"'}
              ),
          ]})
        group_name = self.get_object_model_name()
        if (group_name):
            kwargs['title'] = self.display_title.format(group_name)
        return super().get_context_data(**kwargs)
       

 
class ModelDeleteView(ModelConfirmView):
    """
    View for deleting an object retrieved with self.get_object(), with a
    response rendered by a template.
    """
    template_name_suffix = '_delete_form'
    display_title = 'Delete {0}'
    success_message = "Deleted {0}"
    confirm_message = "<p>Are you sure you want to delete the {0} '{1}'?</p>"

    def success_action(self, form):
        # form.delete() returns a tuple (total, object) ...avoid
        self.object.delete()
        return self.object
        
