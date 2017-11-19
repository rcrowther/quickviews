from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.core.exceptions import ImproperlyConfigured
from functools import update_wrapper, partial
from django.utils.decorators import classonlymethod
from django.contrib import messages
from django.utils.safestring import mark_safe
from django.utils import html
from django.db import router, transaction
from contextlib import contextmanager
from django.urls import reverse

#! move lists and utility funcs over
#! view duplication here and there is ropey
#! make an init

#! novalidate https://docs.djangoproject.com/en/1.11/topics/forms/
#! contexts https://docs.djangoproject.com/en/1.11/ref/forms/renderers/#built-in-template-form-renderers
#! ModelGETRead
#! ModelForm
#! stop using generic model names in exceptions, derive them
#! csrf
#! get rid of self object, use the method and local only?
#! left/right buttons not working due to need to put class on surrounding inline-blocks
#! use the file pk, not an auto-generated one.
#! need this, if all context going through ok,
#! <form {% if has_file_field %}enctype="multipart/form-data" {% endif %}action="{{ form_url }}" method="post" id="{{ opts.model_name }}_form" novalidate>{% csrf_token %}{% block form_top %}{% endblock %}

#??? taxonomy
#??? then sort out Files, finally.

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

def tmpl_instance_message(msg, title):
    '''Template for a message or title about an model instance'''
    return mark_safe('{0} {1}.'.format(msg, html.escape(title)))


def admin_reverse(model_name, url_pattern_name, args=None):
    return reverse('admin:taxonomy_{0}_{1}'.format(model_name, url_pattern_name), args=args)

def admin_reverse2(app_name, model_name, url_pattern_name, args=None):
    return reverse('admin:{0}_{1}_{2}'.format(app_name, model_name, url_pattern_name), args=args)
            
#############################

class ViewVerifyMeta(type):
    '''Base meta for verification on views'''
    def verify_attrs(mcs, module, name, attrs):
        #print('verify_attrs base')
        pass
       
    def __new__(mcs, name, bases, attrs):
        super_new = super().__new__
        parents = [b for b in bases if isinstance(b, ViewVerifyMeta)]
        if not parents:
            #print('ignoring:' +str(name))
            return super_new(mcs, name, bases, attrs)
        module = attrs['__module__']
        new_class = super_new(mcs, name, bases, attrs)
        #print('ViewVerifyMeta run:')
        #print(str(name))
        new_class.verify_attrs(module, name, attrs)
        return new_class

    #def __new__(mcs, name, bases, attrs):
    #    new_class = super().__new__(mcs, name, bases, attrs)
    #    return new_class
#from django.views.decorators.csrf import csrf_protect
#    @csrf_protect_m


class View:
    """
    A base View class.
    This can replace django.views.View. Removes the dispatch-by-method 
    functionality in the original and replaces with a breakout view() 
    method stub. Should otherwise function the same as the original, 
    with similar error messages etc.
    If you enable __init__(), e.g. to check code consistency,
    please call super().__init__(). This sets provided key values
    as attributes on the class 'self' given to the View. This is a
    Django idiom, and other code should follow it.  
    """
    extra_context = None

    def __init__(self, **attr_args):
        """
        Constructor. Called in the URLconf; can contain helpful extra
        keyword arguments, and other things.
        """
        # Go through keyword arguments, and either save their values to our
        # instance, or raise an error.
        for key, value in attr_args.items():
            setattr(self, key, value)


    def get_context_data(self, request, ctx):
        """
        Overridable method for providing template context.
        ...and boosts the context from a couple of sources
        """
        if 'view' not in ctx:
            ctx['view'] = self
        if self.extra_context is not None:
            ctx.update(self.extra_context)
        return ctx

    def view(self, request, *args, **kwargs):
        raise ImproperlyConfigured('View must be configured by inheritance with a "view" method')

    @classonlymethod
    def as_view(cls, **attr_args):
        """Main entry point for a request-response process."""
        for key in attr_args:
            if not hasattr(cls, key):
                raise TypeError("%s() received an invalid keyword %r. as_view "
                                "only accepts arguments that are already "
                                "attributes of the class." % (cls.__name__, key))
        
        # The original code to call the view and provide an instance of
        # the class is intricate, and involves an (yuck) embedded
        # function which cannot be broken out.
        # This mmethod, the partial() from functools, replaces all of 
        # that and allows an overridable method stud.
        # I don't know about performance and docstrings, but it is
        # for sure neater than the original, and the essential 
        # functionality is the same.
        view = partial(cls.view, cls(**attr_args))
        
        # take name and docstring from class
        update_wrapper(view, cls, updated=())

        # and possible attributes set by decorators
        # like csrf_exempt from dispatch
        #update_wrapper(view, cls.dispatch, assigned=())
        return view
        
    def template_response(self, request, ctx):
        """
        Render with a context supplied by get_context_data().
        Pass keyword arguments (usually from from the URLconf) to the context.
        """
        context = self.get_context_data(request, ctx)
        return render(request, self.template, context)



class TemplateResponseMixin:
    """A mixin that can be used to render a template."""
    template = ''
    template_engine = None
    extra_context = None

    def get_context_data(self, request, ctx):
        '''
        Adds a few defaults to the context.
        Can be overridden to customise the template context. This base 
        code can be called as super() before or after customizing code. 
        '''
        if 'view' not in ctx:
            ctx['view'] = self
        if self.extra_context is not None:
            ctx.update(self.extra_context)
        return ctx
        
    def template_response(self, request, ctx):
        """
        Render with a context boosted by get_context_data().
        The incoming ctx should by convention be the url_args of the view. 
        Pass keyword arguments (usually from from the URLconf) to the context.
        """
        context = self.get_context_data(request, ctx)
        return render(
            request, 
            self.template, 
            context=context,
            using=self.template_engine,
        )


        
# Common so we provide
class TemplateView(View, TemplateResponseMixin):
    pass
    

class SuccessFailBase:
    success_redirect_as_admin_base = False

    def success_redirect_url(self, request, ctx):
        raise ImproperlyConfigured('FormView must be configured with a success_redirect_url() method')

    #? given documentation, should inherit into ModelBase
    def before_action(self, request, ctx):
        '''
        Perform actions before dispatch.
        The actions can attach data to the context, run tests, etc.
        In versions of the method attached to Models, this method
        should return a single object. The object is used to populate 
        forms and error messages (see object_title_field). The return can 
        be None for a 'create' form (as irrelevant if an object exists 
        or not)
        '''
        return None
        
    def success_action(self, request, form, ctx):
        raise ImproperlyConfigured('FormView must be configured with a success_action() method')

    def fail_action(self, request, form, ctx):
        raise ImproperlyConfigured('FormView must be configured with a fail_action() method')

    def unbound_action(self, request, ctx):
        raise ImproperlyConfigured('FormView must be configured with a unbound_action() method')



class Read(TemplateView, SuccessFailBase):
    '''
    GET-only template handling
    Relentlessly return to the same template. Data is the query string.
    '''
    template = 'simple_views/generic_form.html'
    query_id = ''

    def view(self, request, *args, **url_args):
        self.before_action(request, url_args)
        if (request.method == 'GET'):
            query = request.GET.get(self.query_id, None)
            if (query):
                try:
                    self.success_action(request, query.strip(), url_args)
                except Exception:
                    self.fail_action(request, query, url_args)
        else:
            self.unbound_action(request, before_data)
        return self.template_response(request, url_args)

    def success_action(self, request, query, ctx):
        '''
        @param clean_data the stripped query string.
        '''
        raise ImproperlyConfigured('FormView must be configured with a success_action() method')



class FormVerifyMeta(type):
    '''Verify a view has a form_class attribute'''
    def verify_attrs(self, module, name, attrs):
        fc = attrs.get('form_class')
        if (fc is None):
            raise ImproperlyConfigured(
                "View class {0}.{1} doesn't declare a form_class.".format(
                    module,
                    name
                )
            )
        super().verify_attrs(module, name, attrs)



class FormBase(SuccessFailBase):
    '''Show and handle forms in a request'''
    form_initial = {}
    form_class = None
    prefix = None

    def get_form(self, ctx, **form_args):
        # This allows form_args to have an initial key, so dynamic
        # initializing
        if ('initial' in form_args):
            form_args['initial'] = dict(form_args['initial'], **self.form_initial)
        else:
            form_args['initial'] = self.form_initial
        form_args['prefix'] = self.prefix
        return self.form_class(**form_args)

    def get_context_data(self, request, ctx):
        return super().get_context_data(request, ctx)



class FormRead(TemplateView, FormBase, metaclass=FormVerifyMeta):
    '''
    Get-only form handling
    Relentlessly return to the same form. Data is the query string.
    '''
    template = 'simple_views/generic_form.html'
    query_id = ''

    def view(self, request, *args, **url_args):
        before_data = self.before_action(request, url_args)
        if (request.method == 'GET'):
            query = request.GET.get(self.query_id, None)
            if (query):
                self.success_action(request, query.strip(), url_args)
            else:
                self.fail_action(request, query, url_args)
        else:
            self.unbound_action(request, before_data)
        return self.template_response(request, url_args)

    def success_action(self, request, query_string, ctx):
        '''
        @param clean_data the stripped query string.
        '''
        # add the query back to 'initial' on the form
        ctx['form'] = self.get_form(ctx, initial={self.query_id : query_string})
        
    def fail_action(self, request, form, ctx):
        # make a new query
        ctx['form'] = self.get_form(ctx)
                
    def unbound_action(self, request, ctx):
        ctx['form'] = self.get_form(ctx)



        
####
class ModelVerifyMeta(type):
    '''Verify a view has consistent model attributes'''
    def verify_attrs(self, module, name, attrs):
        #print('verify_attrs model')
        model = attrs.get('model')
        if (model is None):
            raise ImproperlyConfigured(
                "View class {0}.{1} doesn't declare a model.".format(
                    module,
                    name
                )
            )        
        otf = attrs.get('object_title_field')
        if (otf is not None):
            fnames = [f.name for f in model._meta.fields]
            if otf not in fnames:
                raise ImproperlyConfigured(
                  "View class {0}.{1} declares an object_title_field '{2}' not in the model?".format(
                    module,
                    name,
                    otf
                ))
        super().verify_attrs(module, name, attrs)



class ModelBase:
    model = None
    object_title_field = None 

    def get_model_name(self):
        return self.model._meta.object_name

    def get_display_title(self, obj):
        '''
        Can not be called if an object has not been established,
        i.e. call  after before_action()
        '''
        if (self.object_title_field):
            return '"{0}"'.format(html.escape(getattr(obj, self.object_title_field)))
        else:
            return self.get_model_name()
  
    def get_admin_base_url(self): 
        return '/admin/' + self.model._meta.app_label + '/' + self.model._meta.model_name
        
    def get_absolute_url(self):
        '''
        Can not be called if an object has not been established, 
        i.e. call  after before_action()
        '''
        try:
            url = self.obj.get_absolute_url()
        except AttributeError:
            raise ImproperlyConfigured(
                "No absolute URL defined on {0}.".format(
                self.get_model_name()
                ))
        return url

    @contextmanager
    def quit_if_fails(self, request, ctx):
        try:
            yield
        except:
            msg = mark_safe("{0} class with URL args '{1}' can not be found?".format(
                self.get_model_name(),
                ctx
            ))
            messages.add_message(request, messages.WARNING, msg)
            raise Http404(msg) 

    @contextmanager
    def quit_if_succeeds(self, request, ctx):
        try:
            yield
        except:
            pass
        else:
            msg = mark_safe("{0} class with URL args '{1}' exists.".format(
                self.get_model_name(),
                ctx
            ))
            messages.add_message(request, messages.WARNING, msg)
            raise Http404(msg) 
            
                
                
class ModelFormVerify(ModelVerifyMeta, FormVerifyMeta, ViewVerifyMeta):
    pass
    
    

class ModelFormCommon(TemplateView, FormBase, ModelBase):
    template = 'simple_views/generic_form.html'
    success_redirect_as_admin_base = False

    def success_redirect_url(self, request, ctx):
        if (self.success_redirect_as_admin_base):
            rd = self.get_admin_base_url()
        else:
            rd = request.get_full_path()
        return rd
        
    def view(self, request, *args, **url_args):
        url_args['obj'] = self.before_action(request, url_args)
        if (request.method == 'POST'):
            f = self.get_form(
                url_args,
                data=request.POST,
                files=request.FILES,
                instance=url_args.get('obj')
            )
            if f.is_valid():
                try:
                    self.success_action(request, f, url_args)
                    rd = self.success_redirect_url(request, url_args)
                    return HttpResponseRedirect(rd)
                except Exception:
                    self.fail_action(request, f, url_args)
            else:
                self.fail_action(request, f, url_args)
        else:
            self.unbound_action(request, url_args)
        return self.template_response(request, url_args)
                
    def fail_action(self, request, form, ctx):
        ctx['form'] = form

    def unbound_action(self, request, ctx):
        # object will be null if create, but for update will populate
        ctx['form'] = self.get_form(ctx, instance=ctx.get('obj'))

        
                
#? These must be ModelForms, because of the instance in ...Update.
class ModelCreate(ModelFormCommon, metaclass=ModelFormVerify):
    #form_class = None    

    def create(self, form, ctx):
        raise ImproperlyConfigured('ModelCreate must be configured with a create() method')
         
    def get_context_data(self, request, ctx):
        ctx.update({
        'title': mark_safe('Add {0}'.format(self.get_model_name())),
        'navigators': [],
        'actions': [
          submit("Save", '', attrs={'class':'"button primary right"'}),
        ],
        })
        return super().get_context_data(request, ctx)

    def success_action(self, request, form, ctx):
        ctx['obj'] = self.create(form, ctx)
        msg = 'Created {0}'.format(
            self.get_display_title(ctx['obj'])
        )
        messages.add_message(request, messages.SUCCESS, msg)


             

class ModelUpdate(ModelFormCommon, metaclass=ModelFormVerify):
    ''' require before_action(), form_class, update()'''
    #form_class = None
    #success_redirect_as_admin_base = False

    def update(self, form, ctx):
        raise ImproperlyConfigured('ModelViewUpdate must be configured with an update() method')

    def get_context_data(self, request, ctx):
        ctx.update({
        'title': mark_safe('Update {0}'.format(self.get_display_title(ctx['obj']))),
        'navigators': [],
        'submit_url': request.get_full_path(),
        'actions': [
          #link('Delete', delete, attrs={'class':'"button alert"'})],
          submit("Update", '', attrs={'class':'"button primary righty"'}),
        ],
        })
        return super().get_context_data(request, ctx)
      
    def success_action(self, request, form, ctx):
        obj = self.update(form, ctx)       
        msg = 'Updated {0}'.format(
            self.get_display_title(obj)
        )
        messages.add_message(request, messages.SUCCESS, msg)




class ModelVerify(ModelVerifyMeta, ViewVerifyMeta):
    pass


class ConfirmBase(TemplateView, ModelBase, SuccessFailBase):
    '''
    View for a confirm form built into a template.
    required:
        model
        object_title_field
        def modify(self, ctx)
        def before_action(self, url_args)
    frequent options:
        template
        object_title_field
        page_title
        confirm_message
        succeed_message
        fail_message
        success_redirect_as_admin_base
        def success_redirect_url(self, request, obj)
        def get_context_data(self, request, ctx)
    '''
    template = 'simple_views/confirm_form.html'
    #model = 
    page_title = "Modify {0}"
    #object_title_field = 'title'
    #SuccessFailBase
    #success_redirect_as_admin_base = True
    confirm_message = '<p>Are you sure?</p>'
    succeed_message = 'Modified {0}' 
    fail_message = "Modification of {0} failed? DB may be inconsistent."
    
    def modify(self, ctx):
        raise ImproperlyConfigured('Confirm must be configured with a modify() method')
    
    #SuccessFailBase
    def success_redirect_url(self, request, ctx):
        if (self.success_redirect_as_admin_base):
            rd = self.get_admin_base_url()
        else:
            # cannot be self URL, it's deleted
            raise ImproperlyConfigured('ModelDelete must be configured with a "success_redirect()" or the attribute "success_redirect_as_admin_base"')          
        return rd
        
    def get_context_data(self, request, ctx):
        ctx = super().get_context_data(request, ctx)
        ctx.update({
          'title': self.page_title.format(self.get_display_title(ctx['obj'])),
          'message': mark_safe(self.confirm_message),
          'submit_url': request.get_full_path(),
          'navigators': [],
          'actions': [
              submit(
                  "Yes, I'm sure", 
                  '',
                  attrs={'class':'"button alert"'}
              ),
          ]})
        return ctx     
    
    def view(self, request, *args, **url_args):
        url_args['obj'] = self.before_action(request, url_args)
        if (request.method == 'POST'):
            try:
                self.success_action(request, None, url_args)
            except Exception:
                self.fail_action(request, None, url_args)
                return self.template_response(request, url_args)
            rd = self.success_redirect_url(request, url_args)
            return HttpResponseRedirect(rd)
        else:
            self.unbound_action(request, url_args)
            return self.template_response(request, url_args)
                  
    def success_action(self, request, form, ctx):
        self.modify(ctx)
        msg = self.succeed_message.format(
            self.get_display_title(ctx['obj'])
        )
        messages.add_message(request, messages.SUCCESS, msg)

    def fail_action(self, request, form, ctx):
        msg = mark_safe(self.fail_message.format(
            self.get_display_title(ctx['obj'])
        ))
        messages.add_message(request, messages.WARNING, msg)
        # can fall through to rendering (no form to build)
        
    def unbound_action(self, request, ctx):
        # unlikely to be used...
        pass


class Confirm(ConfirmBase, metaclass=ModelVerify):
    pass


class ModelDeleteConfirm(ConfirmBase, metaclass=ModelVerify):
    confirm_message = ''
    page_title = 'Delete {0}'
    succeed_message = 'Deleted {0}' 
    fail_message = "Delete of {0} failed? DB may be inconsistent."    
