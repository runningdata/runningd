import inspect
import logging
import os
from functools import wraps

logger = logging.getLogger('django')


from utils.threadlocals import get_current_tracer, get_current_request
from opentracing.ext import tags as ext_tags

def jaeger_tracer_cls(cls):
    def _decorator():
        # with get_current_tracer()._tracer.start_span(
        #                 os.path.basename(cls.__name__,
        #                 child_of=get_current_tracer().get_span(
        #                     get_current_request()))) as ttspan:
        for x in inspect.getmembers(cls.objects):
            if '__' not in x[0]:
                print x
                if hasattr(x[1], 'im_class'):
                    print(x[0] + 'is a method')
                else:
                    print(x[0] + 'is a attr')
        return cls
    return _decorator()

def jaeger_tracer(service='will'):
    def _my_decorator(func):
        def _decorator(*args, **kwargs):
            with get_current_tracer()._tracer.start_span(os.path.basename(inspect.getsourcefile(func))[:-2] + func.func_name,
                                                         child_of=get_current_tracer().get_span(
                                                                 get_current_request())) as ttspan:
                # ttspan.set_tag(ext_tags.SPAN_KIND, ext_tags.SPAN_KIND_RPC_CLIENT)
                # ttspan.set_tag(ext_tags.PEER_SERVICE, service)
                for k, v in kwargs.items():
                    ttspan.set_tag(k, v)
                ttspan.set_tag('args', args[1:])
                ttspan.log_event('this is done by will')
                return func(*args, **kwargs)
        return _decorator
    return _my_decorator

# def exeception_printer():
#     def _exeception_printer(view_func):
#         def _decorator(request, *args, **kwargs):
#             # try:
#             #     response = view_func(request, *args, **kwargs)
#             # except:
#             response = render(request, 'common/message.html', {'message': 'hello'})
#             return response
#
#         return wraps(view_func)(_decorator)
#
#     return _exeception_printer


def exeception_printer(func):
    @wraps(func)
    def returned_wrapper(request, *args, **kwargs):
        raise Exception('dfd')
        # try:
        #     return func(request, *args, **kwargs)
        # except Exception, e:
        #     logger.error(traceback.format_exc())
        #     return render(request, 'common/message.html', {'message': e.message})

    return returned_wrapper
