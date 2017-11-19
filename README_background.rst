A note on implementation
~~~~~~~~~~~~~~~~~~~~~~~~
Django has caused me a great deal of trouble and wasted a lot of time, on forms. For a beginner, it is not clear which of the many rendering cababilities will answer needs. I didn't try, and built my forms from scratch. I needed to enable them, and this is not well documentated. Indeed, you can say, beyond the `basic form documentation`_, the rendering of custom forms has no documentation. Django also contains many view possibilities, with varied methods for overriding, and so on. I tried these Views, such as UpdateView, and they sprawl worse than the original code.

This application, for me, has been a relief. It has replaced over a thousand lines of code with systematic handlers. The various assumptions mean the code which enables the forms can sometimes be less than ten lines of essential configuration.


.. _basic form dcumentation: https://docs.djangoproject.com/en/1.11/topics/forms/
.. _what is a save()?: https://docs.djangoproject.com/en/1.11/ref/models/instances/#django.db.models.Model.save
