ListBuilder (and Views)
=======================
Render lists from a queryset or iterable.

When to use
-----------
Code control over rendering into any template, including a default template and CSS.

Limitations
-----------
Can render HTML links, but no consideration if the list includes active widgets and is intended as a form.

In the display, no table filtering. Could be done, but I've not worked on it.


Alternatives
------------
django.ListView
    One of the cutest pieces of code in Django. But needs a dedicated template and queries. No default rendering. Neater than ListBuilder for one-off lists.
    
django.admin.changelist
    Use this if you need a list in Admin. Otherwise, a mass of configuration and the stacked templates are not helpful.
    
    
    
Quickstart
----------
Pick a model, import the code, set a URL, ::

    from simple_views import ModelListBuilderView

    url(r'^list/$', list.ModelListBuilderView.as_view(model=Fireworks, use_fields=['title', 'description', 'effect']))

Note that 'use_fields' must be declared with some field names from the model, or nothing will be visible.

For more control, override ModelListView as below.


Classes
-------

ListBuilder
~~~~~~~~~~~
Works from any dict or queryset with repeated records. The data can be in the form of dicts or objects (as returned by a Django DB query, for example).

First the builder needs a cell definition. See the seperate README for more details. Assume we have this e.g. ::
    
    from simple_views import ListBuilder
    from firework.models import *
    
    class FireworkList(ListBuilder):
        title = TextCell()
        body = TextCell()
            
Set a queryset. For a shortcut, we'll use data from a model (usually, you would use the ModelDetailBuilder), ::

    fireworkList.queryset = Firework.objects.all()
        
Optionally, set the fields to use. Because we declared fields, not necessary, but this can reorder, ::

    fireworkList.use_fields = ['title','description']

Render, ::

    fireworkList.as_table()
    fireworkList.as_ul()
    fireworkList.as_p()
    


Rendering of Listbuilder
+++++++++++++++++++++++++
Note that list builders, like detail builders but unlike Django views like ListView, output finished blocks of HTML. They are completed with surrounding tags.

However, a completed HTML block means not a 'complete table'. HTML has the concent that you can put multiple table bodies and headers into a table, ::

    <table>
        <thead>
        ...
        </thead>
        
        <tbody>
        ...
        </tbody>
        
        <tbody>
        ...
        </tbody>
        ...
    </table>
 
The list builders follow this paradigm (even when not using table tags). You get finished output, but this is only a potential section of a list. You may need a further wrap to complete the full list.
 
If you know that the queryset render of one builder is all you need, ::

    def as_finished_table(self, page_number=1)

returns a header and body wrapped in <table> tags.


     
Other features of ListBuilder
+++++++++++++++++++++++++++++

It can reorder columns. No separate attribute for this, the order is taken from 'use_fields', ::

    use_fields=['effect', 'title', 'desription'] 

renders in that (more dramatic) order. So if you want to reorder, add detail to 'use_fields'.

It can generate column headers. These are taken from the field keys. See headers_as_table() and similar methods.

It takes media, through __init__() or an inner class declaration. Like a form. You are probably doing something to make me sigh, but you can ::


    class FireworkList(ListBuilder):
        title = TextCell(data_field='title')
        body = TextCell(data_field='body')
        
        Media():
            js = 'magic_transition_effects.js'
        
[sigh].


Pagination
__________
Listbuilder paginates. It paginates in much the same way as django.ListView, or django.admin.ChangeList, with 'rows_per_page', orphan control etc.

Generating generic HTML for paging from Django conventions is challenging. The solution is to provide custom Page classes, which contain a render() method. These are assembled into custom Paginators. The Builders access using a little method get_pagination_as_html(). If the paginator has no render() method (is not one of ListBuilder's custom paginators) the method quiety returns nothing.
 
Two custom paginators are available. One provides groups of pages, like major search engines. The other provides 'previous'/'next' links. The View default is GroupPaginator.

If you do not want to use the custom rendering, access the paginator Page in your context or template. Work from there.

ModelListBuilder
~~~~~~~~~~~~~~~~
Same as above, but takes a model attribute. It can query the model to autobuild cells, and use the model's DB manager to grab data.

Auto-build of fields
++++++++++++++++++++
If it finds an entry in 'use_fields', but the entry has no declared field, then it will try to (like a ModelForm, and this module's ModelDetailBuilder) guess fields. You can override with an explicit definition if you wish.

This is how the View in Quickstart (see above) is working. With no declarations to work from, it uses default field configurations to guess.  

ModelListBuilderView passes the page number parameter through the querystring.


ModelListBuilder API
~~~~~~~~~~~~~~~~~~~~
This has quirks worth noting. It takes a Queryset or iterable of dicts, as data. If it fails to find data there, it will try to use the 'model'. It searches for all() as the queryset, but this can be altered by the 'url_filter_arg' argument. The arg should be a dict e.g. {'pk__in':[9,6,2,1]}, or dict(pk__in=[9,6,2,1])

Veterans of Django views should note that this feature and handle method is not like ListView, or any other Django view. It is consistent, in this app, with the class DetailBuilderView.
