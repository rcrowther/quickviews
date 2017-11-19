Adminlinks
==========
Insert a custom URL link, under permission control and cacheable, into the Django admin index.

When to use
-----------
Your view is not a changelist, yet you want it on the main menu.

Limitations
-----------
Can only direct to a lowercased path modification of the link name. 'Octopus' will direct to '.../octopus/'.

The 'change' icon will appear in the action menu.

The internals are horrible. You may reject the module for this alone.


Alternatives
------------
None.


Quickstart
----------
Assume you have a view called 'search'. In 'admin.py' add,

    from quickviews import adminlinks
    from . import views
        
    adminlinks.register("Search", views.search)
    
A link 'Search' in the Admin menu will appear under the appname, which leads to the '.views.search' view.

API
---

def register(link_text, view, url_name=None, site=admin.site, cacheable=False):
  ...
  
You will not use 'site' often, but if you need it, it is there.


Extra
-----
Background
~~~~~~~~~~
Django.sites has, somehat conrary to it's documentation and Django in genrral, no ability to customise the URLs. 

If you consult the web, you will find the Django documentation https://docs.djangoproject.com/en/1.11/ref/contrib/admin/#modeladmin-methods on ModelAdmin.get_urls rrepeatedly cut and pasted. This is misleading. Added URLs can only be attached to Models. The URLs are not visible in the menu. The menu wrapper is not DRY API. If the original URLs are dropped, the model link and it's index are dropped too, leaving a dead entry in the index. The templates can not handle addittional URLs, and are stacked. Reverse URLs are lost.

This is an estensive list of non-provision. So much, I wonder, was it by design? The only way out is to provide your own site. This can be done, but the customisation rewired is massive. And a non-desired interface for the user.

I tried rewiring inside and outside the main site instance. Outside involved much ugly code, inside is limited to non-visible links. So this module provides fake 'models', which can provide an entry into the menu, and then a URL override, to target the view. It's nasty, but it works and, third time round, I can't see how it can be improved.
