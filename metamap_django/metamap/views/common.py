from django.http import HttpResponse

from will_common.utils.constants import DEFAULT_PAGE_SIEZE
from django.views import generic


class StatusListView(generic.ListView):
    template_name = 'components/common_executions_list.html'
    context_object_name = 'executions'
    url_base = 'url_base'

    def get(self, request, status):
        self.paginate_by = DEFAULT_PAGE_SIEZE
        self.object_list = self.model.objects.filter(status=status).order_by('-start_time')
        allow_empty = self.get_allow_empty()

        if not allow_empty:
            if (self.get_paginate_by(self.object_list) is not None
                and hasattr(self.object_list, 'exists')):
                is_empty = not self.object_list.exists()
            else:
                is_empty = len(self.object_list) == 0
            if is_empty:
                raise Exception("Empty list and '%(class_name)s.allow_empty' is False.")
        context = self.get_context_data()
        context['url_base'] = self.url_base
        return self.render_to_response(context)