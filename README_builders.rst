Builders (and Views)
====================
Render lists and objects.

When to use
-----------
Code control over rendering into any template, including a default template and CSS.

Limitations
-----------
Can render HTML links, but no consideration if the list includes active widgets and is intended as a form.


Classes
-------
The builders for lists and objects share features.


CellRenderers
~~~~~~~~~~~~~

Shared between DetailViews and ListViews
++++++++++++++++++++++++++++++++++++++++
Cellrenderers are used to render both single instances of data records (DetailView) and lists of records (ListViews). Naturally, a single instance renders one list of data, and a list renders multiples e.g. a Firework may render as ::

   <li>name</li>
   <li>description</li>
   <li>effect</li>

A list of Fireworks as, ::

   <ul>
   <li>name</li>
   <li>description</li>
   <li>effect</li>
   </ul>
   <ul>
   <li>name</li>
   <li>description</li>
   <li>effect</li>
   </li>
   ...
   
The rendering can also be as_table(), and as_span().


Cellrenderer definitions
+++++++++++++++++++++++
CellRenderers have a few configuration attributes. Interesting are, ::

    TextCell(max_length=64)

Limits the text length to 64 characters, and adds an ellipsis if the text was truncated.

HTML links can be wrapped round any render. The attribute 'link' is formatted with the cell 'value' (escaped), and the 'data' (complete record). To make a title into a link, ::
 
    title = TextCell(link='/firework/{data.pk}')
    
Extra columns of data can be added, with no direct reference to the queryset. For example, render a column of links with text 'show', which link to a record detail display, ::

    edit_link = FixedTextCell(text='show', link="/firework/{data.pk}")

'link' also takes a callable, so you could use, for example, a callback that supplies the absolute_url().

The headers generators in the list builders (and maybe other code) use the keys cell renderers are set on for column titles. Most of the time, this is ok, especially as the builders make a little effort to reformat the keys for display. But sometimes a reformat is not enough. For example, if you want to add punctuation to a column title e.g. 'edit?', or a verbose descriptive title e.g. 'The way of the rabbit'. Titles like this are not good or not allowed as keys for dicts. The solution is to use the cell renderer attribute,

    verbose_name='The way of the rabbit'
    ...
    
'verbose_name' will print as the column header, and not the hash key.


Builders
--------

Introducing data
~~~~~~~~~~~~~~~~
Data can be given to the classes by,

Initialisation 
    e.g. FireworkClass(data=???)
  
Class definition
    FireworkClass(SomeClass):
        data=???
        
Method overriding
    FireworkClass(SomeClass):
        def get_data(self):
             ...
             
    Which usually recovers self.data. There is no need to call super().
    If you do it checks self.data is present, if not throws an 
    excreption, if it is, returns the data. 
             
For model versions, data can also be recovered by some combination of 
parameters which will do a dynamic search e.g.

    url(r'^(?P<firework_pk>[0-9]+)/$',
        ModelDetailBuilderView.as_view(model=Paper, url_pk_arg='firework_pk', use_fields = ['title', 'summary', 'pub_date']),
    ),
    ...
    
The parameters which can be set are cruder (deliberately) than those in django.views. If you want fine control over what is delivered, override get_data().



Cellrenderers in Builders
-------------------------
API
~~~
The builders have an API similar to django.Form. Declare cells on a class, ::
    
    from quickviews import ListBuilder
    from firework.models import *
    
    class FireworkList(ListBuilder):
        title = TextCell(data_field='title')
        body = TextCell(data_field='body')
        
Definitions can be inherited (like django.Form).

The 'data_field' attribute is where the cell looks in the supplied data for items to render. By default, the CellRenderers use the key, so if the keys match the record keys,

    class FireworkList(ListBuilder):
        title = TextCell()
        body = TextCell()
        
This is slightly different to a form. A form expects the init() values to be split and distributed to each field. Listbuilder expects to process multiple records at once, so each renderer does the work of extracting data from records.

Or define the cells using init(), though this method gets bulky quickly, ::

    from quickviews import ListBuilder
    from firework.models import *
    
    fireworkList = ListBuilder( cells={
        title = TextCell(data_field='title'),
        description = TextCell(data_field='description')
        }
        )
     
     
Order Cellrenderers
+++++++++++++++++++++
Declaring renderers makes them active. To some extent, order of declaration is preserved. However, cellrenderers can be reordered by the 'use_fields' parameter on all builders.

'use_fields' serves another purpose. The Model versions of the builders can build renderers from the models by default. However, they will not do this unless the field in the model is declared by 'use_fields'. This is for the same reasons as django.ModelForms, to prevent accidental display of data.

So this will display nothing, ::

    from quickviews.detail import ModelDetailBuilderView

    url(r'^(?P<firework_pk>[0-9]+)/$',
    ModelDetailBuilderView.as_view(model=Paper, url_pk_arg='firework_pk'),
    ),

It will throw an error, as the parameter 'allow_empty' defaults to False. It needs to be changed to, ::

    url(r'^(?P<firework_pk>[0-9]+)/$',
    ModelDetailBuilderView.as_view(model=Paper, url_pk_arg='firework_pk', use_fields = ['title', 'description', 'effect']),
    ),
    

Other features of Builders
++++++++++++++++++++++++++
They take media, through __init__() or an inner class declaration. Like a form. You are probably doing something to make me sigh, but you can ::


    class FireworkList(ListBuilder):
        title = TextCell(data_field='title')
        body = TextCell(data_field='body')
        
        Media():
            js = 'magic_transition_effects.js'
        
[sigh].


Special features of ListBuilders
++++++++++++++++++++++++++++++++
'use_fields' reorders columns ::

    use_fields=['effect', 'title', 'description'] 

renders in that (more dramatic) order.

They can generate column headers. These are taken from the field keys. See headers_as_table() and similar methods.


Pagination of ListBuilders
__________________________
Listbuilders paginate. They paginate in much the same way as django.ListView, or django.admin.ChangeList, with 'rows_per_page', orphan control etc.

Generating generic HTML for paging from Django conventions is challenging. The solution is to provide custom Page classes, which contain a render() method. These are assembled into custom Paginators. The ListBuilders access using a little method get_pagination_as_html(). If the paginator has no render() method (is not one of ListBuilder's custom paginators) the method quietly returns nothing.
 
Two custom paginators are available. One provides groups of pages, like major search engines. The other provides 'previous'/'next' links. The View default is GroupPaginator.

If you do not want to use the custom rendering, access the paginator Page in your context or template. Work from there.


 
