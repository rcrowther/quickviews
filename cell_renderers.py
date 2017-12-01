import datetime

#from django.utils.html import format_html, mark_safe
from django.utils.html import conditional_escape
from django.forms.widgets import MediaDefiningClass
from django.core.exceptions import ImproperlyConfigured



#! should meta-test missing attributes (see View), but tricky with
#! MediaDefiningClass in way.
#! think we need some basic validation. See ListView?
#! localize
class CellRenderer(metaclass=MediaDefiningClass):
    '''
    The data input to the render methods can be either a dict or an 
    object. The form given may affect  'link' string formatting, see 
    below.
    
    The link parameter is a text string. The text string is 
    formatted with the escaped cell 'value' and the row 'data'. So 'link' 
    can be defined, for example, as '/paper/{value}/edit' or
    '/paper/{data.pk}/edit'. Consider that the 'value' is escaped, but 
    values from 'data' are not.
    
    The link can also be a callable, which takes the data
    e.g. def get_absolute_url(data):...; link=get_absolute_url
       
    'data_field' is the name to look for in supplied objects. Some code
    automatically populates this attribute. Other code should avoid 
    populating the attribute if it is set by declaration or init param.
    Use set_data_field().
    '''
    link = None
    value = None
    data_field = None
    empty_value_display = '-'
    verbose_name = None
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

            
    def set_data_field(self, name):
        # only do this if the cell renderer not
        # set by init params
        if (self.data_field is None):
            self.data_field = name
        
    def get_value(self, data):
        if (not self.data_field):
            return None
        elif (isinstance(data, dict)):
            return data[self.data_field]
        elif (isinstance(data, object)):
            return getattr(data, self.data_field)
        else:
            return None            

    def get_link(self, value, data):
        if callable(self.link):
            return self.link(value, data)
        else:
            return self.link.format(value=value, data=data)
        
    def validate_value(self, value):
        '''
        Test a value can go to subsequent code.
        Should always return a string (empty if the value is )
        '''
        return value  
    
    def format_value(self, value):
        """
        Return a value as it should appear when rendered in a template.
        """
        #if value is None:
        #    value = ''
        # from Admin
        if not value:
            value = self.empty_value_display
        #if self.is_localized:
        #    return formats.localize_input(value)
        return value
        
    def value_as_html(self, value):
        return value
    
    def as_html(self, value, data):
        v = conditional_escape(value)
        o = self.value_as_html(v)
        if (self.link):
            url = self.get_link(value, data)
            o = '<a href="{0}">{1}</a>'.format(url, o)
        return o

    def render(self, data):
        v = self.get_value(data)
        v = self.validate_value(v)
        v = self.format_value(v)
        return self.as_html(v, data)
         
    def __str__(self):
        return  "<{0}>".format(self.__class__.__name__)
             
    def __repr(self):
        return  "<{0}>".format(self.__class__.__name__)
        
        
# Names and values params are escaped
# Anything else, e.g. from field parameter, is not, necessarily.

#? value of choices?
class EmptyCell(CellRenderer):
    def value_as_html(self, value):
        return ''



class TextCell(CellRenderer):
    max_length = None
        
    def format_value(self, value):
        """
        Return a value as it should appear when rendered in a template.
        """
        value = super().format_value(value)
        if (self.max_length and len(value) > self.max_length):
            # trailing char is ellipsis
            value = value[0:self.max_length] + '\u2026'
        return value
        
        
        
class NumericCell(CellRenderer):
    format_str = '{}'
    
    def format_value(self, value):
        """
        Return a value as it should appear when rendered in a template.
        """
        value = super().format_value(value)
        return self.format_str.format(value)
        
        
        
class TimeCell(CellRenderer):
    format_str = ''
    default_date = '%d/%m/%Y'
    default_time = '%H:%M:%S'
    default_datetime = '%d/%m/%Y %H:%M:%S'
    
    def format_value(self, value):
        """
        Return a value as it should appear when rendered in a template.
        """
        if (self.format_str):
            value = value.strftime(format_str)
        else:
            if isinstance(value, datetime.datetime):
                value = value.strftime(self.default_datetime)
            elif isinstance(value, datetime.date):
                value = value.strftime(self.default_date)
            elif isinstance(value, datetime.time):
                value = value.strftime(self.default_time)
        return super().format_value(value) 

    def value_as_html(self, value):
        return '<time>{0}</time>'.format(value)



class ImageCell(CellRenderer):
    def value_as_html(self, value):
        return '<img src="{0}">'.format(value)


    
#? do with text attribute? Neater?
class FixedTextCell(TextCell):
    def __init__(self, **kwargs):
        text = kwargs.pop('text', None)
        if (text is None):
            raise ImproperlyConfigured('FixedTextCell must have a "text" attibute.')        
        self.fixed_value = self.format_value(text)
        super().__init__(**kwargs)

    def render(self, data):
        return self.as_html(self.fixed_value, data)



class FixedImageCell(ImageCell):
    def __init__(self, **kwargs):
        src = kwargs.pop('src', None)
        if (src is None):
            raise ImproperlyConfigured('FixedImageCell must have a "src" attibute.') 
        self.fixed_value = self.format_value(src)
        super().__init__(kwargs)

    def render(self, data):
        return self.as_html(self.fixed_value, data)
        
    
from django.db.models import fields


#DefaultForModelField = dict(
    #CharField=TextCell(),
    #FilePathField=TextCell(),
    #SlugField=TextCell(),
    #GenericIPAddressField=TextCell(),
            ##isinstance(field, fields.files.FileField)

    #TextField=TextCell(max_length=16),

    #URLField=TextCell(link='{value}'),
    #UUIDField=TextCell(link='{value}'),
          
    #AutoField=NumericCell(),
    #BinaryField=NumericCell(),               
    #DecimalField=NumericCell(),
    #FloatField=NumericCell(),
    #IntegerField=NumericCell(),
    #PositiveIntegerField=NumericCell(),
    #PositiveSmallIntegerField=NumericCell(),
    #SmallIntegerField=NumericCell(),

    #ImageField=ImageCell(),

    #DateField=TimeCell(),
    #DateTimeField=TimeCell(),
    #TimeField=TimeCell(),
#)

def default_cell_from_model_field(field, abbreviated=False):
        if(
            isinstance(field, fields.CharField)
            or isinstance(field, fields.FilePathField)
            or isinstance(field, fields.SlugField)
            or isinstance(field, fields.GenericIPAddressField)
            #isinstance(field, fields.files.FileField)
            ):
            return TextCell()
        elif(
            isinstance(field, fields.TextField)
            ):
            
            return TextCell(max_length=16) if (abbreviated) else TextCell()           
        elif(
            isinstance(field, fields.URLField)
            or isinstance(field, fields.UUIDField)
            # NB: Images are not shown as default as an image.
            # Ttheymay be any size. They are shown as their source link.
            or isinstance(field, fields.files.ImageField)
            ):
            return TextCell(link='{value}')
        elif(            
            isinstance(field, fields.AutoField)
            or isinstance(field, fields.BinaryField)               
            or isinstance(field, fields.DecimalField)
            or isinstance(field, fields.FloatField)
            or isinstance(field, fields.IntegerField)
            or isinstance(field, fields.PositiveIntegerField)
            or isinstance(field, fields.PositiveSmallIntegerField)
            or isinstance(field, fields.SmallIntegerField)
            ):
            return NumericCell()
        elif(
            isinstance(field, fields.DateField)
            or isinstance(field, fields.DateTimeField)
            or isinstance(field, fields.TimeField)
        ):
            return TimeCell()
        else:
            return None
