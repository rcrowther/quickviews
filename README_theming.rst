Templates and style
===================

General approach to theming
---------------------------
The templates are generic.  Very little happens in the templates, no iterative loops or the like. Data is delivered in escaped blobs from the views (which only route the blobs from the builders). Only one layer of inheritance, from the generic base. The system is as dull and minimal as possible. 

The templates are not styled using Django admin (maybe should be, but not). They are styled with a barebones, could-easily-be-the-main-website, lightly-responsive design. The default CSS style is close to Django admin. It can be altered or replaced if you wish.


The Templates
-------------
A constant feature is the template base. This implements an HTML header and body. The body contains a header, body, footer, and two aside blocks in semantic HTML. In the base, other templates provide a form, confirm_form and generic_page templates.


Remove/Add buttons in the default views
-----------------------------------------
The only substancial feature in the default views is the toolbar.

To remove the context data added for the default templates, set, ::

    add_default_context=False
    
If you do this on a form view, all the action bttons will vanish. They can be replaced by following the next steps.

To add buttons? To add a 'Cancel' button to a 'delete' form is user-friendly. This example illustrates how to append to the context using get_context_data(). Add this, ::

    from quickviews import views, inline_templates

    class FireworkDelete(views.ModelDeleteView):
        ...
        
        def get_context_data(self, **kwargs):
            # Run the super first. It adds 'view', 'form' and other
            # context attributes
            ctx = super().get_context_data(**kwargs)
            # 'actions' is rendered into the action bar.
            ctx['actions'].append(
                  # inline_templates makes links and submit HTML.
                  # The URL parameter is from a method built in to the view,
                  # but you could hardcode, use a reverse() etc.
                  inline_templates.link(
                  "No, take me back",
                  ctx['view'].get_admin_base_url(),
                  attrs={'class':'"button"'})
                )
            # Return the context for rendering
            return ctx


Change CSS (and Javascript)
-----------------------------
You'd like the view to be styled in another way, or would like/need Javascript additions. 

This is done with a Django-like API (in QuickViews, consistently applied). All QuickViews implement Django's MediaMixin. To add your own CSS, ::

    class BBView(ModelDetailBuilderView):
        ...
        
        class Media:
            css = {
                'all': ('site/pretty.css',)
            }
        
The view will look for 'site/static/site/pretty.css'. If you wish to remove the default CSS, set 'extend' to False, ::

    class BBView(ModelDetailBuilderView):
        ...
        
        class Media:
            extend = False
            css = {
                'all': ('site/pretty.css',)
            }
        
        
        
Change the base template
--------------------------


Change templates
-----------------
Remember you can change the presentation of a single item using a CellRenderer override. And presentation of a page using CSS anf Javascript.

The DetailView will deliver a context something like, ::

{
'review_pk': <IDfield value>, 
'object': <For ModelViews, a database object, or some data being viewed>, 
'id_name': <<model name>_<title field value>>, 
'view' : <the View object>
'display_name': <title field value>, 
'content':  <object rendered as HTML list>,
'media': <media class printing as media files>
}

So you can add touches of data here. Then duplicate the QuickViews generic templates into your app, revise the 'template' attribute path, and render.

If you want to go further than this, you are stepping to the edge of QuickViews. Remember, one of the main aims is a generic view of the data. If you destroy the generic view, then a lot of useless render code will be run for each view.

There are several scenarios where this may be the case. The main one is that, for better or worse, your database data does not represent what you think a user should see. Perhaps a great table of data needs breaking up for nice presentation in several parts. For display on different URLs, this can be done by field using the 'use_fields' attribute. But this will not work for display on one page. The other variation, displaying substancial data from several database tables on one page, can not be handled very well by QuickViews. Of course, the extra code could be injected into get_context(), but this is mutating the use of QuickViews, which is not generally a good idea.

Other things QuickViews can not do are deliver JSON form a URL, and similar web activity.
