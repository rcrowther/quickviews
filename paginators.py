import math
from django.utils.html import format_html, mark_safe

from django.core.paginator import InvalidPage, Paginator, Page



class PrevNextPage(Page):
    '''
    Pagination Page with prev/next links.
    '''
    def html_previous(self, idx):
        href = self.paginator.paginator_url.format(idx)
        return '<li><a href="{0}" class="direction">Previous</a></li>'.format(href)

    def html_next(self, idx):
        href = self.paginator.paginator_url.format(idx)
        return '<li><a href="{0}" class="direction">Next</a></li>'.format(href)

    def render(self):
        b = []
        if (self.has_previous()):
              b.append(self.html_previous(self.number - 1))
        if(self.has_next()):
              b.append(self.html_next(self.number + 1))
        return mark_safe(''.join(b))
        
        
        
class PrevNextPaginator(Paginator):
    def _get_page(self, *args, **kwargs):
        return PrevNextPage(*args, **kwargs)


        
class GroupPage(Page):
    '''
    Pagination Page with group renderer.
    A group renderer renders a shunting window of page 'groups'
    with 'prev' and 'next' to the next 'groups' of pages.
    Like classic Google, etc.
    '''
    group_size = 8
    
    def page_idx_as_html(self, idx, css_class):
        href = self.paginator.paginator_url.format(idx)
        return '<li><a href="{0}"{1}>{2}</a></li>'.format(href, css_class, idx)
   
    def html_previous(self, idx):
        href = self.paginator.paginator_url.format(idx)
        return '<li><a href="{0}" class="groupnav">Previous</a></li>'.format(href)

    def html_next(self, idx):
        href = self.paginator.paginator_url.format(idx)
        return '<li><a href="{0}" class="groupnav">Next</a></li>'.format(href)

    def render(self):
        b = []
        page_count = self.paginator.num_pages
        current_page_idx = self.number
        #group_size = self.paginator.per_page
        if (page_count <= self.group_size):
            for idx in range(1, page_count + 1):
                css_class = ''
                if (idx == current_page_idx):
                    css_class = ' class="active"' 
                b.append(self.page_idx_as_html(idx, css_class))
        else:
            current_group = math.floor((current_page_idx - 1) / self.group_size) + 1
            start_page = ((current_group - 1) * self.group_size) + 1
            until_page = min(start_page + self.group_size, page_count + 1)
            if (start_page > 1):
                b.append(self.html_previous(start_page - 1))
            for idx in range(start_page, until_page):
                css_class = ''
                if (idx == current_page_idx):
                    css_class = ' class="active"' 
                b.append(self.page_idx_as_html(idx, css_class))            
            if (until_page <= page_count):
                b.append(self.html_next(until_page))
        return mark_safe(''.join(b))


            
class GroupPaginator(Paginator):
    def _get_page(self, *args, **kwargs):
        return GroupPage(*args, **kwargs)
        
