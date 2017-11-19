from functools import update_wrapper
from django.urls import reverse

from django.contrib import admin
from django.conf.urls import url

from django.core.exceptions import FieldError, ImproperlyConfigured
from django.apps import apps
from django.utils.text import format_lazy, camel_case_to_spaces
from django.contrib.auth import get_permission_codename


class Options():
    def __init__(self, cls, app_label=None):
        self.apps = apps
        self.app_label = app_label
        self.object_name = cls.__name__
        self.model_name = self.object_name.lower()
        self.verbose_name = camel_case_to_spaces(self.object_name)
        # Do nothing with the plural name. It is referenced in the 
        # templates as plural, but we do not need plurality.
        self.verbose_name_plural = self.verbose_name
        self.abstract = False
        self.swapped = False
        
    @property
    def app_config(self):
        # Don't go through get_app_config to avoid triggering imports.
        return self.apps.app_configs.get(self.app_label)
        return new_class
        
        
        
#! get app_label without model?
#! can we get rid of actions? (with links, likely)
#! can we reroute the index? Where does URL come from?
class FakeModelMetaclass(type):
    """Collect Fields declared on the base classes."""
    def __new__(mcs, name, bases, attrs):
        super_new = super().__new__

        # This metaclass will run on a base model. We want to check for 
        # required attributes and build meta info, but not on bases
        # themselves.
        parents = [b for b in bases if isinstance(b, FakeModelMetaclass)]
        if not parents:
            return super_new(mcs, name, bases, attrs)        
        module = getattr(attrs, '__module__', 'paper')
        new_class = super_new(mcs, name, bases, attrs)        
        app_config = apps.get_containing_app_config(module)
        if app_config is None:
            if not abstract:
                raise RuntimeError(
                    "FakeModel class %s.%s doesn't declare an explicit "
                    "app_label and isn't in an application in "
                    "INSTALLED_APPS." % (module, name)
                )

        else:
            app_label = app_config.label

        setattr(mcs, '_meta', Options(new_class, app_label))

        #! defences
        return new_class

        
        
        
class FakeModel(metaclass=FakeModelMetaclass):
   #! not overriding
    def _default_manager(self):
        raise FieldError(
            "FakeModel class {0}.{1} should never call _default_manager. Have you set a URL override?".format(
            self.__module__, 
            self.__name__
            ))

#! permissions?
#! caching
class AdminURLs():# BaseModelAdmin):

    def __init__(self, model, admin_site):
        self.model = model
        self.opts = model._meta
        self.admin_site = admin_site
        super().__init__()

    def __str__(self):
        return "%s.%s" % (self.model._meta.app_label, self.__class__.__name__)

    def check(self):    
        return []

    def get_model_perms(self, request):
        """
        Return a dict of all perms for this model. This dict has the keys
        ``add``, ``change``, and ``delete`` mapping to the True/False for each
        of those actions.
        """
        return {
            'add': self.has_add_permission(request),
            'change': self.has_change_permission(request),
            'delete': self.has_delete_permission(request),
        }
        
    def has_add_permission(self, request):
        """
        Return True if the given request has permission to add an object.
        Can be overridden by the user in subclasses.
        """
        opts = self.opts
        codename = get_permission_codename('add', opts)
        return request.user.has_perm("%s.%s" % (opts.app_label, codename))

    def has_change_permission(self, request, obj=None):
        """
        Return True if the given request has permission to change the given
        Django model instance, the default implementation doesn't examine the
        `obj` parameter.

        Can be overridden by the user in subclasses. In such case it should
        return True if the given request has permission to change the `obj`
        model instance. If `obj` is None, this should return True if the given
        request has permission to change *any* object of the given type.
        """
        opts = self.opts
        codename = get_permission_codename('change', opts)
        return request.user.has_perm("%s.%s" % (opts.app_label, codename))

    def has_delete_permission(self, request, obj=None):
        """
        Return True if the given request has permission to change the given
        Django model instance, the default implementation doesn't examine the
        `obj` parameter.

        Can be overridden by the user in subclasses. In such case it should
        return True if the given request has permission to delete the `obj`
        model instance. If `obj` is None, this should return True if the given
        request has permission to delete *any* object of the given type.
        """
        opts = self.opts
        codename = get_permission_codename('delete', opts)
        return request.user.has_perm("%s.%s" % (opts.app_label, codename))

    def has_module_permission(self, request):
        """
        Return True if the given request has any permission in the given
        app label.

        Can be overridden by the user in subclasses. In such case it should
        return True if the given request has permission to view the module on
        the admin index page and access the module's index page. Overriding it
        does not restrict access to the add, change or delete views. Use
        `ModelAdmin.has_(add|change|delete)_permission` for that.
        """
        return request.user.has_module_perms(self.opts.app_label)

    @property
    def urls(self):
        return self.get_urls()

#! extra links
def register(link_text, view, url_name=None, site=admin.site, cacheable=False):
    fake_class = type(link_text, (FakeModel,), {})
    # if no name given, use the name 'default'
    if (not url_name):
        url_name = 'default'
            
    def get_urls(self):
        def admin_url_name(name):
            return '{0}_{1}_{2}'.format(
                self.model._meta.app_label,
                self.model._meta.model_name,
                name
                )   
                
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        stock_url_name = admin_url_name('changelist')
        custom_url_name = admin_url_name(url_name)
        #print('Search info')
        #print(str(custom_url_name))
        #print(str(stock_url_name))
        urlpatterns = [
            # direct the index custom view and url reverse...
            url(r'^$', self.admin_site.admin_view(view, cacheable=cacheable), name=custom_url_name),
            url(r'^wiggly/$', wrap(view), name='wiggly'),

            # ... but we must also add the original reverse, or the 
            # 'admin_url' parameter is not passed to the template, and
            # the link will not be active (overriden or not).
            url(r'^$', wrap('ow'), name=stock_url_name),
        ]
        return urlpatterns

    fake_admin_class = type(link_text + 'Admin', (AdminURLs,), {"get_urls": get_urls})
            
    # the class must be in a list, as register()
    # accepts an iterable, and ours is not based in ModelBase.
    site.register([fake_class], fake_admin_class)
