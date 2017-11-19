

__version__ = '3.0.0'

from .form import (
    GetView,
    CreateView, ModelCreateView, 
    UpdateView, ModelUpdateView, 
    ConfirmView, ModelConfirmView, ModelDeleteView
)

from .list import (
    ListBuilder, ListBuilderView, ModelListBuilder, ModelListBuilderView
)

from .detail import (
    DetailBuilder, DetailBuilderView, ModelDetailBuilder, ModelDetailBuilderView
)

__all__ = [
    #'View', 'TemplateView', 'RedirectView', 'ArchiveIndexView',
    'ListBuilder', 'ListBuilderView', 'ModelListBuilder', 'ModelListBuilderView',
    'DetailBuilder', 'DetailBuilderView', 'ModelDetailBuilder', 'ModelDetailBuilderView',
]
