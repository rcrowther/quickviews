import copy
import re

from collections import OrderedDict
from contextlib import suppress
from django.http import Http404
from django.utils.translation import gettext as _
from django.forms.widgets import Media, MediaDefiningClass
from django.utils.html import format_html, mark_safe
from django.views.generic import TemplateView

from .builders import DeclarativeFieldsMetaclass
from .cell_renderers import default_cell_from_model_field
from .paginators import (InvalidPage, PrevNextPaginator, GroupPaginator)



#? allow_empty only for renderers
#! section, not article, HTML

def space_and_lower(value):
    return re.sub(r'\_', ' ', value).strip().lower()
    


class ListRow():
    '''
    Render a row of data.

    Output is defined by the fields. These can be set directly or
    through an initialisation parameter. To preserve order, the type
    is assumed a list of tuples [(name, CellRenderer), ...]. The field
    keys mean nothing, they are a key. The field values are expected
    to be CellRenderers.

    The link parameter to the renderers is a text string or callable. The
    text string is formatted with the escaped 'value', and the row 'data'.
    See CellRenderer for more info.
     
    Output can be as HTML table elements, list elements, or spans.
    
    Will not render row ends.
    
    Intended to be reusable for generating multiple rows. To set values,
    use populate(). 
    
    Use append_cells() with an iterable key/(CellRenderer)value to add 
    cells programtically. OrderedDict can not maintain order in a 
    constructor.
    '''
    # a list of tuple [(name, RenderField)]
    fields = []

    def __init__(self, fields=None):
        if (fields):
            self.fields = fields

    def append_cells(self, cells):
        for k, v in cells.items():
            self.fields[k].set_value(v)

    def _html_output(self, data, item_start, item_end):
        "Output HTML. Used by as_table(), as_ul(), as_p()."
        b = []
        for name, field in self.fields.items():
            item_classes = ' class="{0}"'.format(name)
            b.append(item_start.format(item_classes))
            b.append(field.render(data))
            b.append(item_end)
        return mark_safe(''.join(b))

    def as_table(self, data):
        "Return this row rendered as HTML <td>s."
        return self._html_output(
            data,
            item_start='<td{0}>',
            item_end='</td>'
            )

    def as_list(self, data):
        "Return this row rendered as HTML <li>s."
        return self._html_output(
            data,
            item_start='<li{0}>',
            item_end='</li>'
            )

    def as_span(self, data):
        "Return this row rendered as HTML <span>s."
        return self._html_output(
            data,
            item_start='<span{0}>',
            item_end='</span>'
            )

    #def __str__(self):
    #    return self.as_table()

    def __repr__(self):
        return '<%(cls)s fields=(%(fields)s)>' % {
            'cls': self.__class__.__name__,
            'fields': ';'.join(self.fields),
        }
        


class ListBase():
    '''
    Render an iterable of objects as a list.
    The iterable or object can be a queryset from a model, or any 
    iterable of objects with similar fields. It is sttributes which are
    retrieved (dicts will not work).
    
    Fields defines the mapping to the objects, keys are the fields 
    sought in objects. Values are CellRenderers.
     
    You can set a kind of render on a field, either preset or custom.
    You can adapt the renderer to deliver a URL
    
    Will render a full table section, but may need further tags such as 
    <table> to finish.
     
    @param list_ordering  order_by args applied to list
    @param output_title for rendering. If supplied, renderers may read
    from this field to provide page titles 
    '''
    list = None
    list_ordering = None
    list_model_name = None
    list_selection_name = None
    
    use_fields=None
    
    #paginate_by = None
    allow_empty = False
    rows_per_page = 25
    paginate_orphans = 0
    #paginator_class = Paginator
    #paginator_class = PrevNextPaginator
    paginator_class = GroupPaginator
    paginator_url = '/'
    
    
    def __init__(self,
        list=None, list_ordering=None, use_fields=None,
        allow_empty=False, rows_per_page=None,
        list_model_name=None, list_selection_name=None
        ):
        if list is not None:
            self.list = list
        if list_ordering is not None:
            self.list_ordering = list_ordering
        if use_fields is not None:
            self.use_fields = use_fields
        if allow_empty is not None:
            self.allow_empty = allow_empty
        if rows_per_page is not None:
            self.rows_per_page = rows_per_page
        if list_model_name is not None:
            self.list_model_name = list_model_name
        if list_selection_name is not None:
            self.list_selection_name = list_selection_name

        # The base_fields class attribute is the *class-wide* definition of
        # fields. Because a particular *instance* of the class might want to
        # alter self.fields, we create self.fields here by copying base_fields.
        # Instances should always modify self.fields; they should not modify
        # self.base_fields.
        self.cells = copy.deepcopy(self.base_fields)
        
        # order by use_fields
        # (the model version both orders and retrieves defaulted fields)
        self.inflect_by_use_fields(self.use_fields)

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
             
        # build the row renderer
        self.row_renderer = ListRow()
        self.row_renderer.fields = self.cells

    def inflect_by_use_fields(self, use_fields):
        if use_fields is None:
            return
        b = OrderedDict()
        for key in use_fields:
            with suppress(KeyError):
                b[key] = self.cells.pop(key)
        # add remaining fields in original order
        b.update(self.cells) 
        self.cells = b

    def _order_list(self, list):
        if self.list_ordering:
            if isinstance(self.list_ordering, str):
                self.list_ordering = (self.list_ordering,)
            list = list.order_by(*self.list_ordering)
        return list
            
      
    def get_list(self):
        """
        Return the list of items for this view.

        The return value must be an iterable and may be an instance of
        `QuerySet` in which case `QuerySet` specific behavior will be enabled.
        """
        if self.list is not None:
            list = self.list
            if isinstance(list, QuerySet):
                list = list.all()
        else:
            raise ImproperlyConfigured(
                "%(cls)s is missing a 'list' attribute. Define "
                "%(cls)s.list, or override "
                "%(cls)s.get_list()." % {
                    'cls': self.__class__.__name__
                }
            )
        return self._order_list(list)

    def get_list_model_name(self):
        """Get the group name to use for the object."""
        return self.list_model_name

    def get_list_selection_name(self):
        """Get the name to use for this selection in the list."""
        return self.list_selection_name

    def get_display_name(self):
        """
        Get the object name, fallback to the group name.
        @return a name, or None
        """
        name = self.get_list_selection_name()
        if (not name):
            name = self.get_list_model_name()
        return name
        
    def get_pagination_as_html(self, page_number):
        paginator = self.get_paginator()
        page = paginator.page(page_number)
        return '' if (getattr(page, 'render', None) is None) else page.render()
      
    def get_paginator(self, **kwargs):
        """Return an instance of the paginator for this view."""
        p = self.paginator_class(
            self.list,
            self.rows_per_page,
            orphans=self.paginate_orphans,
            allow_empty_first_page=self.allow_empty,
            **kwargs
            )
        p.paginator_url = self.paginator_url
        return p
        
    def paginate_list(self, page_number):
        """Paginate the list, if needed."""
        paginator = self.get_paginator()
        #page_kwarg = self.page_kwarg
        #page = self.kwargs.get(page_kwarg) or self.request.GET.get(page_kwarg) or 1
        #try:
            #page_number = int(page)
        #except ValueError:
            #if page == 'last':
                #page_number = paginator.num_pages
            #else:
                #raise Http404(_("Page is not 'last', nor can it be converted to an int."))
        try:
            page = paginator.page(page_number)
        except InvalidPage as e:
            raise Http404(_('Invalid page (%(page_number)s): %(message)s') % {
                'page_number': page_number,
                'message': str(e)
            })
        return (paginator, page, page.object_list, page.has_other_pages())

    def _field_names(self):
        return self.cells.keys()

    def _header_output(self, 
        header_start, 
        header_end,
        cell_rend_template
        ):
        "Output HTML. Used by headers_as_table(), headers_as_ul(), headers_as_p()."
        b = []
        b.append(header_start)
        for name, cell in self.cells.items():
            if (cell.verbose_name):
                name = cell.verbose_name
            else:
                name = space_and_lower(name)
            b.append(cell_rend_template.format(name))
        b.append(header_end)
        return mark_safe(''.join(b))
          
    def headers_as_table(self):
        "Return this header rendered as HTML <thread> and <th>."
        return self._header_output(
            header_start='<thead><tr>',
            header_end='</tr></thead>\n',
            cell_rend_template='<th>{0}</th>'
            )
            
    def headers_as_ul(self):
        "Return this header rendered as HTML <ul> and <li>."
        return self._header_output(
            header_start='<ul class="header">',
            header_end='</ul>\n',
            cell_rend_template='<li>{0}</li>'
            )
            
    def headers_as_p(self):
        "Return this header rendered as HTML <p> and <span>."
        return self._header_output(
            header_start='<div class="header"><p>',
            header_end='</p></div>\n',
            cell_rend_template='<span>{0}</span>'
            )
            
    def get_item_attrs(self, item):
        item_attrs = ' class="detail"'
        return item_attrs
        
    def _html_output(self, 
        row_rend_method, 
        row_start, 
        row_end, 
        list_start,
        list_end,
        page_number
        ):
        "Output HTML. Used by as_table(), as_ul(), as_p()."
        b = []
        b.append(list_start)
        paginator, page, list, is_paginated = self.paginate_list(page_number)
        for item in list:
            b.append(row_start.format(self.get_item_attrs(item)))
            b.append(row_rend_method(item))
            b.append(row_end)
        b.append(list_end)
        return mark_safe(''.join(b))

    def as_table(self, page_number=1):
        "Return this list rendered as HTML table."
        return self._html_output(
            row_rend_method = self.row_renderer.as_table,
            row_start='<tr{0}>',
            row_end='</tr>\n',
            list_start='<tbody>',
            list_end='</tbody>',
            page_number=page_number
            )

    def as_ul(self, page_number=1):
        "Return this list rendered as HTML list."
        return self._html_output(
            row_rend_method = self.row_renderer.as_list,
            row_start='<li{0}>',
            row_end='</li>\n',
            list_start='<ul>',
            list_end='</ul>',
            page_number=page_number
            )

    def as_p(self, page_number=1):
        "Return this list rendered as HTML <p>s in a <div>."
        return self._html_output(
            row_rend_method = self.row_renderer.as_span,
            row_start='<p{0}>',
            row_end='</p>\n',
            list_start='<div>',
            list_end='</div>',
            page_number=page_number
            )

    def as_finished_table(self, page_number=1):
        b = []
        b.append('<table class="detail-list">')
        b.append(self.headers_as_table())
        b.append(self.as_table(page_number=page_number))
        b.append('</table>')
        return mark_safe(''.join(b))
        
    @property
    def media(self):
        """Return all media required to render the cells on this builder."""
        media = Media()
        for cell in self.cells.values():
            media = media + cell.media
        return media

    def __str__(self):
        return self.as_finished_table()

    def __repr__(self):
        return '<%(cls)s fields=(%(fields)s)>' % {
            'cls': self.__class__.__name__,
            'fields': ';'.join(self._field_names()),
        }



class ListBuilder(ListBase, metaclass=DeclarativeFieldsMetaclass):
    pass



class ListBuilderView(ListBuilder, TemplateView):
    template_name = 'quickviews/generic_page.html'

    def get_context_data(self, **kwargs):
        #? add pagenumber from kwargs
        page_number = 1
        kwargs.update({
        'content' : self.as_finished_table(page_number),
        'media' : self.media
        })
        display_name = self.get_display_name(self.object)
        if (display_name):
            kwargs['title'] = display_name
        return super().get_context_data(**kwargs)

    class Media:
        css = {
            'all': ('quickviews/css/table.css',)
            }
        
        
class ModelListBase(ListBase):
    '''
    Render a list or model as a list.
    Renders using default template, which can be substituted, and uses 
    all the methods in django.views.ListView.
    You can let the let the View do it's work and guess how fields in the 
    model are to be rendered.
    You can override which fields are to be rendered.
    You can set a kind of render on a field, either preset or custom.
    You can adapt the renderer to deliver a URL 
    
    Will render a full table section, but may need further tags such as 
    <table> to finish.
    '''
    model = None
    url_filter_arg = {}

    def __init__(self,  
        model=None,
        url_filter_arg=None,
        list=None, list_ordering=None, use_fields=None,
        allow_empty=False, rows_per_page = None,
        list_model_name=None, list_selection_name=None
        ):
        if (model):
            self.model = model
        if (not self.model):
            raise AttributeError("ModelListBuilder must be called with a coder-defined attribute 'model'.")
        if (url_filter_arg):
            self.url_filter_arg = url_filter_arg
        if (not isinstance(self.url_filter_arg, dict)):
            raise AttributeError("ModelListBuilder.url_filter_arg must be a dict() of Django query attributes.")

        super().__init__(
            list=list, list_ordering=list_ordering, use_fields=use_fields, 
            allow_empty=allow_empty, rows_per_page=rows_per_page, 
            list_model_name=list_model_name, list_selection_name=list_selection_name
            )

    def inflect_by_use_fields(self, use_fields):
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
        # sort
        super().inflect_by_use_fields(use_fields)

    def _verify_can_try_query(self):
          if (not(self.list)):
              raise ImproperlyConfigured(
                  "With no 'object' attribute, %(cls)s needs 'model' and 'url_pk_arg' attributes" % {
                      'cls': self.__class__.__name__
                  })

    def _verify_list_is_from_model(self):
        if (not(isinstance(self.object, Queryset))):
            raise ImproperlyConfigured(
                "%(cls)s.list is not a Queryset" % {
                    'cls': self.__class__.__name__
                })
                
    def get_list(self):
        """
        Return the list of items for this view.

        The return value must be an iterable and may be an instance of
        `QuerySet` in which case `QuerySet` specific behavior will be enabled.
        """
        if (self.list is not None):
            self._verify_list_is_from_model()
            list = self.list
        else:
            # if we have no data, use the other args to get some
            # NB: will return 'all' if url_filter_arg = {}
            self._verify_can_try_query()
            filter_exp = self.kwargs.get(self.url_filter_arg)
            try:
                list = self.model._default_manager.filter(**filter_exp)
            except self.model.DoesNotExist:
                raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': list.model._meta.verbose_name})
        return self._order_list(list)

    def get_list_model_name(self):
        """Get the group name to use for the object."""
        return self.model._meta.verbose_name_plural
        
    def get_item_attrs(self, item):
        item_attrs = ' id="model-{0}-{1}" class="detail"'.format(
            self.model._meta.model_name,
            item.pk
            )
        return item_attrs
        
        
        
class ModelListBuilder(ModelListBase, metaclass=DeclarativeFieldsMetaclass):
    pass



class ModelListBuilderView(ModelListBuilder, TemplateView):
    template_name = 'quickviews/generic_page.html'
    rows_per_page = 25
        
    def get_context_data(self, **kwargs):
        # 'page' implemented as a query parameter
        self.paginator_url=self.request.path + '?page={}'        
        self.list = self.model.objects.all()
        page_number = self.request.GET.get('page', '1')

        kwargs.update({
        'content' : self.as_finished_table(page_number),
        'pagination_nav' : self.get_pagination_as_html(page_number),
        'media' : self.media
        })
        display_name = self.get_display_name()
        if (display_name):
            kwargs['title'] = display_name
        return super().get_context_data(**kwargs)

    class Media:
        css = {
            'all': ('quickviews/css/table.css',)
            }
