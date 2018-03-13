Form Views
==========
Form and ModelForm views with auto 'create'/'update'/'delete' handling.

When to use
-----------
Shorthand operative views. Includes default templates and CSS, overridable. Plus extra hooks. But auto-rendered views of a model form is the main interest.

Limitations
-----------
Finally, if you want custom views with special templates and media additions, you'll write your own. Not use this or any other formbuilder.


Alternatives
------------
django.views.(FormView, CreateView, UpdateView, DeleteView). 
    These are near the QuickViews, and the Django way. But they have no default rendering, the code they generate is larger than hand-written view handling,
    and their control flow needs a leap of conception.

django.admin.views
    For admin forms, these are the place to start. But custom forms and action is a mass of configuration, with modular templates to handle. Outside Admin, near unusable.
    
FormBuilder app
    Answers the question in a different way. Well worth considering if you need instances of custom forms.

CrispyForms app
    Lighten your load for Form writing. Seems commonly used.


How FormViews work
------------------
They lightly but deeply rework the Django view stack for forms. Here are the differences,

- querysets replaced with get_object()
Getting objects or data is offloaded onto the coder. One method. Model 
versions of the views query an 'filter.all()'.

- success_action/fail_action hooks
If the forms fail or succeed, hook methods let you do something else without reworking chunks of view code.
 
- messages
I like messages. That's the only excuse.

- absolute_url()/return_url() methods
If you can find them, they are there.

- default templates
All views render through default templates.


The form views offload their customisable handling onto the coder, or rely on other Django code. More so than the Django originals. If the form passes validation, the business of the view is done. You do your magic in a hook method.

This module is about what you don't do in the view, not building two tonnes of machinery to deliver a page.


Classes
-------
Quick list, ::

    GetView
    CreateView, ModelCreateView, 
    UpdateView, ModelUpdateView, 
    ConfirmView, ModelConfirmView, 
    ModelDeleteView


GetView
~~~~~~~
GetView is worth a note. It is HTML GET method only. It defaults to redirecting to itself, and is, by default, populated by submitted data. It is intended for 'Search' or other display forms. It retains most of the features of the other views here, including default rendering.


The Views
-----------
The views often default to redirecting to themselves, unless redirects are unsafe.

Shared attributes and methods
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
template_name
    Defaults to the simple_view templates, but can be anything.

get_object()
    Get data to populate or crosscheck a form. For model forms this method is semi-automatic. It can be overridden to do whatever complex data-gathering you need.

output_title
    Or 'display_title'. For the template.     

success_action()
    Should return a message. This is run through a simple template that adds the words 'Create', or similar.
    
The code contains several other tweaks, but these are the big differences. Form handling is unchanged from Django.


Model-based views
+++++++++++++++++
model
    Required. A Model class
    
object_name_field_key
    Fills the name of of the object in messages and templates e.g. 'Deleted "quartz"'. The default uses the generic modelname e.g. 'Deleted Pebble'.

get_absolute_url()
    retrieves the absolute URL from a model instance. Of course, the mixin must have sucessfully retrieved a model instance. Should be available in the get_context_data() method of any Model-based view.




Examples
~~~~~~~~
All these are model views. Non-model views are alao available.

ModelCreate
+++++++++++
Use auto-form generation for models, but override the success method for a custom save, ::

    from quickviews import views

    class FireworkCreate(views.ModelUpdate):
        model = Firework
        object_name_field_key = 'name' 
        fields=['name', 'description', 'effect']
        success_url = '/firework/{obj.pk}'

        def success_action(self, form):
            # do something to save...
            return obj
        

            
ModelUpdate
+++++++++++
Or provide a custom form, but lean on the default success method for Model-based views, ::

    from quickviews import views

    class FireworkUpdate(views.ModelUpdate):
        model = Firework
        object_name_field_key = 'name'
        form_class = FireowkUpdateForm
        fields=['name', 'description', 'effect']
        success_url = '/firework/{obj.pk}'
      
      
            
ModelDelete
+++++++++++
Delete. We always need a delete, ::

    from quickviews import views

    class FireworkDelete(views.ModelDelete):
        model = Firework
        url_pk_arg = 'article_pk'
        object_name_field_key = 'name'
        success_url = '/firework/list'
        

Extra attributes
++++++++++++++++



Extra
-----






