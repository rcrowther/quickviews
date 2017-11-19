DetailBuilder (and Views)
=========================
Render pages from information in dicts or Django Model instances.

When to use
-----------
Code control over rendering into any template, including a default template and CSS.

Limitations
-----------
Can render HTML links, but no consideration if the data includes active widgets and is intended as a form.

Alternatives
------------
django.DetailView
    Needs a template. No default rendering. Model instances only.
    
    
Quickstart
----------
Pick a model, import the code, set a URL, ::

    from quickviews import ModelListView

    url(r'^list/$', list.ModelListView.as_view(model=Fireworks, use_fields=['title', 'description', 'effect']))

Note that 'use_fields' must be declared with some field names from the model, or nothing will be visible.

For more control, override ModelListView as below.


Classes
-------

DetailBuilder
~~~~~~~~~~~
Works from any dict or Model instance.

First the builder needs a cell definition. See the seperate README for more details. Assume we have this e.g. ::
    
    from quickviews import DetailBuilder
    from firework.models import *
    
    class FireworkDetail(DetailBuilder):
        title = TextCell()
        body = TextCell()
        
Set data. For a shortcut, we'll use data from a model (usually, you would use the ModelDetailBuilder), ::

    FireworkDetail.data = Firework.objects.get(pk=9)
        
Optionally, set the fields to use. Because we declared fields, not necessary, but this can reorder, ::

    FireworkDetail.use_fields = ['title','description']

Render, ::

    FireworkDetail.as_table()
    FireworkDetail.as_ul()
    fireworkList.as_p()
    

Rendering of Detailbuilder
+++++++++++++++++++++++++
Note that detail builders, like list builders but unlike Django views like ListView, output finished blocks of HTML. They are completed with surrounding tags, ::

    <ul>
        <li>
        </li>    
        <li>
        </li>
        <li>
        </li>
        ...
    </ul>
 
The detail builders follow this paradigm (even when not using table tags).
 

ModelDetailBuilder
~~~~~~~~~~~~~~~~
Same as above, but takes a model attribute. It can query the model to autobuild cells, and use the model's DB manager to grab data.

Auto-build of fields
++++++++++++++++++++
If it finds an entry in 'use_fields', but the entry has no declared field, then it will try to (like a ModelForm, and this module's ModelListBuilder) guess fields. You can override with an explicit definition if you wish.

This is how the View in Quickstart (see above) is working. With no declarations to work from, it uses default field configurations to guess.  


ModelDetailBuilder API
~~~~~~~~~~~~~~~~~~~~~~~
This has quirks worth noting. It takes a 'data' or dict, as data. If it fails to find data there, it will try to use the 'model'. It searches for all() as the queryset, but this can be altered by the 'url_pk_arg' argument, taken from a url pattern.

Veterans of Django views should note that this feature and handle method is a little like DetailView. It is simpler (there is no no maniplulation of the queryset, only the possibility to select). It is consistent, in this app, with the class ListBuilderView.

Odd parameter; if given, 'title_field_key' will search in the data for the given field and place the data on 'self.output_title'. Of a context or templae enables it
