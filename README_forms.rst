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
They lightly but deeply rework the Django view stack for forms. Here are 
the differences,

- querysets replaced with get_object()
Getting objects or data is somewhat offloaded onto the coder. One method,
get_object(). When provided a queryset, the views query an 'filter.all()'. 

- success_action/fail_action hooks
If the forms fail or succeed, hook methods perform actions and send 
preformed messages. Overriding can you do something else without 
reworking chunks of view code.
 
- messages
I like messages. That's the excuse.

- absolute_url()/return_url() methods
If you can find them, they are there.

- default templates
All views render through default templates.


The form views offload their customisable handling onto the coder, or 
rely on other Django code. More so than the Django originals. If the 
form passes validation, the business of the view is done. You do your 
magic in a hook method.

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
Unlike Django views, which go to the absolute_url(), the views often 
default to redirecting to themselves, unless redirects are unsafe (e.g. 
'delete' views, where, if deletion is successful, you wouldn't want to 
do it again).

Redirection
~~~~~~~~~~~
Form views redirect to the return from get_success_url().  

get_success_url() tries the attribute 'success_url'. Except on the most 
basic mixins, if the attribute is empty, the method uses return_url() 
to redirect to the form.

The exception is 'confirm/delete' views. Since the object may be 
deleted, returning to the same URL is inefficient and not user 
expectaion. So confirm/delete'views require the attribute 'success_url' 
to be stated.

get_success_url() can be overridden to the absolute URL, ::

    def get_success_url(self):
        return self.object.get_absolute_url()

or to a guess at the admin base URL (will work ok if admin is not 
modified), ::

    def get_success_url(self):
        return self.get_admin_base_url()

Hooks
~~~~~~
fail_action() is currenlty only for form validation. It mainly for 
rerouting logons and the like. It doesn't protect, or make any provision 
for messages, if the action in a success_action() fails. That will throw an
exception which, uncaught, in Django production would result in a 404
error. 

Object provision
~~~~~~~~~~~~~~~~
Django (not only quickviews, but the Django views stack) has 
interesting mixins which look for self.object. The views do this always,
even if the view is not a model (the views can work from a dict). 
self.object is used mainly to be passed into a POSTed form, to 
generate information such as which fields have been altered.

Quickviews extends this by building messages and titles from self.object. 
Quickviews also contract this a little, by reducing the machinery and 
leaving finding the object to the coder.

Sometimes a current object is not immediately available, for example, in
the case of creating an object. Both Django views and Quickviews solve 
this by setting self.object=None in the view method stages.

Occassionally, you may want a view which does not seek out an object 
first. This may be for many reasons such as quick development, or 
because the object involves complex machinery such
as remote access, or trivial machinery such as an admin form for raw
data. The object seek can be overriden by, ::

    def get_object(self):
        # override an initial load.
        return None
 


Shared attributes and methods
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
template_name
    Defaults to the simple_view templates, but can be anything.

get_object()
    Get data to populate or crosscheck a form. For model forms this method is semi-automatic. It can be overridden to do whatever complex data-gathering you need.

output_title
    Or 'display_title'. For the template.     

success_action()
    Should return a message. This is run through a simple message 
    template that adds the words 'Create', or similar. The template 
    accepts some detail, such as the model name, an object title defined
    by 'object_name_field_key'. Either the detail can be overriden, or, for forcible
    rewording, the entire template overridden.
    
The code contains several other tweaks, but these are the big differences. 
Form handling is unchanged from Django.



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
Create
++++++
A non-model CreateView, ::
    
    from django import forms
    
    class CreateForm(forms.Form):
        name = forms.CharField(max_length=128)
        email = forms.EmailField()
        date = forms.DateField()
        # etc.

    class CreateSomething(CreateView):
        form_class = CreateForm
        # Modify the create messages
        display_title = 'Generate {0}'
        success_message = "Generated {0}"
        
        def success_action(self, form):
            # generate something from 'form' data e.g. 
            form.clean_fields['name']
            form.clean_fields['email']
            form.clean_fields['date']
            # etc.
            return 'some_message'
    
  

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
            return someMessage
        

            
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






