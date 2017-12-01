QuickViews
============
It was like this in the old days. When you had food and had to walk to the shops. Views with poor configuration and you can take the code in with a glance. But the same class-based API as modern Views.

QuickViews contains views for rendering forms, lists, and models. All views have default rendering through stock templates  and CSS.


When to use this application
----------------------------
Any of the following,

- You want to see and use forms, lists, or models straight away (you will figure out details later).
- You're happy with stock HTML. Let the CSS do the work.
- You don't want to read through the many Admin and Django views trying to figure out if the code can do what you want.
- You have a form which is not part of Admin provision, yet you want it in Admin (e.g. a search). 

(there are some other uses. In some circumstances, you may also consider this app when you know for sure you will be writing custom templates and CSS on a View)

The documentation contains a wider discussion of these features.


Limitations
-----------
Not the Django stack. Not mature, so likely to change.

Alternatives
------------
See documentation in the detailed READMEs.


Main features
-------------

Consistent API
    Across detail, list, and form view implementations.

Reasonably exhaustive API
    Non-Model and Model versions of most views, etc.

Default rendering
    All views render immediately through default templates and CSS.

Close to Django
    Though it is impossible to reconcile all Django APIs, QuickView code has made progress. 




Screenshots
-----------
.. figure:: https://raw.githubusercontent.com/rcrowther/quickviews/master/text/images/detailview.png
   :width: 100
   :alt: detailview screenshot
   :align: center

   One line in a url.py file

.. figure:: https://raw.githubusercontent.com/rcrowther/quickviews/master/text/images/listview.png
   :width: 100
   :alt: objectview screenshot
   :align: center

   Listview, reduced number of rows, plus group paginator


 
 
Overall guide
-------------

Install
~~~~~~~
In settings.py, ::

    INSTALLED_APPS = [
        'quickviews.apps.QuickViewsConfig',
    ]

Quickviews needs no other setup.

Hints
~~~~~
Some approaches to the API are emerging:

Django's sometimes variable approach to setting parameters has been clarified. All parameters are available as attributes on a View class, for overriding by sub-classing. A set of parameters is included in some __init__()s, mainly for the standalone use in URLs and by builders.

The builders have render methods. These are named as_table() etc. for substancial variations. The __str__() method returns a default render method (Django's Form class uses this approach). The auto-generating Views inherit these builders directly. If extensive, detailed, or dedicated customisation is needed, the Views can be subclassed. But, if not, build parameters can be set on URL construction.

Django provides an inheritable/overridable Media_ class class/attribute/metaclass for handling CSS and JS. It can be found in widgets and forms. This has been enabled on every view in QuickViews. Which makes appending and substituting other CSS and JS easy. Also, all default CSS and JS is delivered this way. So, if you want, you can override to raw HTML.

 

Use
~~~
See the separate READMEs. Files/modules included,

adminlinks
    Put a custom link under permissions into the main AdminView. Freaky, but seems to live here.
    
forms
    Defaulted views for use with Forms and ModelForms

list views and paginators
    Contains a ListBuilder which works from a Django database query. And defaulted views.

detail views
    Same as ListBuilder but for single instances of models or dicts. Contains a DetailBuilder which works from a Django database query or dict. And defaulted views.


.. _Media: https://docs.djangoproject.com/en/1.11/topics/forms/media/
