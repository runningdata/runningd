from django.views import generic

from dqms.models import DqmsAlert
from will_common.utils.constants import DEFAULT_PAGE_SIEZE


class AlertView(generic.ListView):
    template_name = 'alert/info.html'
    paginate_by = DEFAULT_PAGE_SIEZE
    model = DqmsAlert
    context_object_name = 'objs'
    search_key = 'name'

    def get_queryset(self):
        key = self.get_key()
        if len(key) > 0:
            return DqmsAlert.objects.filter(rule__case__case_name__contains=key)
        return DqmsAlert.objects.all().order_by('-ctime')

    def get_key(self):
        key = ''
        if self.search_key in self.request.session:
            key = self.request.session[self.search_key]
            if self.search_key in self.request.GET:
                key = self.request.GET[self.search_key]
                self.request.session[self.search_key] = key
        elif self.search_key in self.request.GET:
            key = self.request.GET[self.search_key]
            self.request.session[self.search_key] = key
        return key