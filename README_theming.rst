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
