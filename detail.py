import copy

from collections import OrderedDict
from contextlib import suppress
from django.core.exceptions import ImproperlyConfigured
from django.http import Http404
from django.utils.translation import gettext as _
from django.forms.widgets import Media, MediaDefiningClass
from django.utils.html import format_html, mark_safe
from django.views.generic import TemplateView
from django.views.generic.base import ContextMixin
from django.db import models


from .builders import DeclarativeFieldsMetaclass
from .cell_renderers import default_cell_from_model_field




class SingleObjectMixin():
    '''
    Retrieve/stash a single object (or dict) for further manipulation.
    '''
    object = None
    object_model_name = None
    object_name_field_key = None
      
    def get_object_name(self, object):
        """Get the name to use for an object."""
        object_name = None
        #if (not(self.object_name_field_key)):
            #raise ImproperlyConfigured(
                #"%(cls)s needs an 'object_name_field_key' attribute" % {
                    #'cls': self.__class__.__name__
                #}))
        if (object and self.object_name_field_key):
            if (isinstance(object, dict)):
                object_name = object[self.object_name_field_key]
            else:
                object_name = getattr(object, self.object_name_field_key)
        return object_name

    def get_object_model_name(self):
        """Get the group name to use for the object."""
        return self.object_model_name

    def get_display_name(self, object):
        """
        Get the object name, fallback to the group name.
        @return a name, or None
        """
        name = self.get_object_name(object)
        if (not name):
            name = self.get_object_model_name()
        return name
        
    def get_object(self):
        """
        Return the data used to render.

        This method can be overridden if data retrieval requires
        extensive code.
        """
        if self.object is None:
            raise ImproperlyConfigured(
                "%(cls)s is missing an 'object' attribute. Define "
                "%(cls).object, or override "
                "%(cls)s.get_object()." % {
                    'cls': self.__class__.__name__
                }
            )
        return self.object



class SingleObjectContextMixin(ContextMixin, SingleObjectMixin):
    def get_context_data(self, **kwargs):
        """Insert the data into the context dict."""
        if self.object:
            kwargs['object'] = self.object
            object_name = self.get_object_name(self.object)
            if object_name:
                kwargs['object_name'] = object_name
            object_model_name = self.get_object_model_name()
            if object_model_name:
                kwargs['object_model_name'] = object_model_name
        return super().get_context_data(**kwargs)



class SingleModelObjectMixin(SingleObjectMixin):
    '''
    Retrieve/stash a single model object for further manipulation.
    This will not allow the data to be a dict.
    '''
    model = None
    url_pk_arg = None

    def verify_can_try_query(self):
          if (not(self.model and self.url_pk_arg)):
              raise ImproperlyConfigured(
                  "With no 'object' attribute, %(cls)s needs 'model' and 'url_pk_arg' attributes" % {
                      'cls': self.__class__.__name__
                  })
                
    def verify_object_is_from_model(self):
        if (not(isinstance(self.object, models.Model))):
            raise ImproperlyConfigured(
                "%(cls)s.object is not a Model instance" % {
                    'cls': self.__class__.__name__
                })
                
    def get_object_model_name(self):
        """Get the group name to use for the object."""
        return self.model._meta.verbose_name
        
    def get_object(self): 
      # it is useful to use self.object, so test here, as this
      # view may have other model-specific code           
      if (self.object):
          self.verify_object_is_from_model()
          obj = self.object
      else:
          # if we have no self.object, use the other args to get data
          self.verify_can_try_query()
          qs = self.model._default_manager.all()
          pk = self.kwargs.get(self.url_pk_arg)
          try:
              obj = qs.get(pk=pk)
          except self.model.DoesNotExist:
              raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': qs.model._meta.verbose_name})
      return obj



class SingleModelObjectContextMixin(SingleModelObjectMixin, SingleObjectContextMixin):
    pass

        
###############################################################################
#? truncate in django.utils.text
#? cells is cell_map
class DetailBase(SingleObjectMixin):  
    '''
    Builder for field data.
    The builder will build from declared fields. It can be ordered by
    'use_fields'.
    The data can be on self.data. More extensive custom data can be 
    retrieved by overriding,
       def get_object()
    '''
    use_fields=None
    allow_empty = False

    def __init__(self, 
        object=None, use_fields=None,
        allow_empty=False,
        object_model_name = None
        ):
        if object is not None:
            self.object = object
        if use_fields is not None:
            self.use_fields = use_fields
        if allow_empty is not None:
            self.allow_empty = allow_empty
        if object_model_name is not None:
            self.object_model_name = object_model_name
            
        # The base_fields class attribute is the *class-wide* definition of
        # fields. Because a particular *instance* of the class might want to
        # alter self.fields, we create self.fields here by copying base_fields.
        # Instances should always modify self.fields; they should not modify
        # self.base_fields.
        self.cells = copy.deepcopy(self.base_fields)
        
        # append init-supplied fields
        #if (cells):
        #   self.cells = self.cells + cells
           
        # order by use_fields
        # (the model version both orders and retrieves defaulted fields)
        self._inflect_by_use_fields(self.use_fields)
        
        # the renderers may return nothing, but this will except
        # if they do not try
        if (not self.cells):
                raise Http404(_("'%(class_name)s.cells' contains no entries.") % {
                    'class_name': self.__class__.__name__,
                })
                
        # load the field names from the keys into the fields
        # (only has effect if not defined in a cell renderer)
        for name, cell in self.cells.items():
            cell.set_data_field(name)

    def _inflect_by_use_fields(self, use_fields):
        if use_fields is None:
            return
        b = OrderedDict()
        for key in use_fields:
            with suppress(KeyError):  # ignore unknown fields
                b[key] = self.cells.pop(key)
        b.update(self.cells)  # add remaining fields in original order
        self.cells = b
        
    def append_cells(self, cells):
        for k, v in cells.items():
            self.fields[k].set_value(v)
        
    def get_item_attrs(self):
        item_attrs = ' class="detail"'
        return item_attrs
        
    def _html_output(self, field_start, field_end, data_start, data_end):
        "Output HTML. Used by as_table(), as_ul(), as_p()."
        b = []
        b.append(data_start.format(self.get_item_attrs()))
        data = self.get_object()
        for name, cell in self.cells.items():
            item_classes = ' class="{0}"'.format(name)
            b.append(field_start.format(item_classes))
            b.append(cell.render(data))
            b.append(field_end)
        b.append(data_end)
        return mark_safe(''.join(b))

    def as_table(self):
        "Return this data rendered as HTML <tbody>."
        return self._html_output(
            field_start='<td{0}>',
            field_end='</td>',
            data_start='<tbody{0}>',
            data_end='</tbody>'
            )

    def as_list(self):
        "Return this data rendered as HTML <li>s in an <ul>."
        return self._html_output(
            field_start='<li{0}>',
            field_end='</li>',
            data_start='<ul{0}>',
            data_end='</ul>'
            )

    def as_span(self):
        "Return this data rendered as HTML <span>s in a <p>."
        return self._html_output(
            field_start='<span{0}>',
            field_end='</span>',
            data_start='<p{0}>',
            data_end='</p>'
            )

    @property
    def media(self):
        """Return all media required to render the cells on this builder."""
        media = Media()
        for cell in self.cells.values():
            media = media + cell.media
        return media

    def __str__(self):
        return self.as_list()

    def __repr__(self):
        return '<%(cls)s fields=(%(fields)s)>' % {
            'cls': self.__class__.__name__,
            'fields': ';'.join(self.cells),
        }



class DetailBuilder(DetailBase, metaclass=DeclarativeFieldsMetaclass):
    pass



class DetailBuilderView(DetailBuilder, SingleObjectContextMixin, TemplateView):
    template_name = 'quickviews/generic_page.html'

    def get_context_data(self, **kwargs):
        kwargs.update({
        'content' : self.as_list(),
        'media' : self.media
        })
        display_name = self.get_display_name(self.object)
        if (display_name):
            kwargs['title'] = display_name
        return super().get_context_data(**kwargs)
        
    class Media:
      css = {
          'all': ('quickviews/css/list.css',)
          }



class ModelDetailBase(SingleModelObjectMixin, DetailBase):
    '''
    Builder for model data.
    The builder will build from declared fields, also auto-build fields 
    from undeclared model fields if present in 'use_fields'.
    The data can be either on self.data, or retrieved via the 
    'url_pk_arg' argument and the model default_manager.  
    More extensive custom data can be retrieved by overriding
       def get_object()
       
    @param object_name_field_key search in data for this field and load 
    to self.output title.
    '''
    model = None
    url_pk_arg = None
    object_name_field_key = None

    def __init__(self,
        model= None,
        url_pk_arg=None, object_name_field_key=None,
        object=None, use_fields=None,
        allow_empty=False,
        object_model_name = None
        ):
        if (model):
            self.model = model
        if (not self.model):
            raise AttributeError("ModelDetail must be called with a coder-defined attribute 'model'.")

        # can't test here, get_data() may be overridden
        if (url_pk_arg):
            self.url_pk_arg = url_pk_arg
        if (object_name_field_key):
            self.object_name_field_key = object_name_field_key
        super().__init__(
            object=object, use_fields=use_fields,
            allow_empty=allow_empty,
            object_model_name=object_model_name
            )

    def _inflect_by_use_fields(self, use_fields):
        if use_fields is None:
            return
        # All the fields in use_fields not in declared or added fields
        # but in model... add as defaulted.
        model_field_names = [f.name for f in self.model._meta.fields]
        for fn in use_fields:
          if ((fn not in self.cells) and (fn in model_field_names)):
              df = default_cell_from_model_field(self.model._meta.get_field(fn))
              if (df):
                self.cells[fn] = df
        # protect and sort
        super()._inflect_by_use_fields(use_fields)
        
    def get_item_attrs(self):
        item_attrs = ' id="model-{0}-{1}" class="detail"'.format(
            self.model._meta.model_name,
            self.kwargs.get(self.url_pk_arg)
            )
        return item_attrs



class ModelDetailBuilder(ModelDetailBase, metaclass=DeclarativeFieldsMetaclass):
    pass



class ModelDetailBuilderView(ModelDetailBuilder, SingleObjectContextMixin, TemplateView):
    template_name = 'quickviews/generic_page.html'

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        kwargs.update({
        'content' : self.as_list(),
        'media' : self.media
        })
        display_name = self.get_display_name(self.object)
        if (display_name):
            kwargs['title'] = display_name
        return super().get_context_data(**kwargs)
        
    class Media:
        css = {
            'all': ('quickviews/css/list.css',)
            }
