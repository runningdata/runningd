import logging
from functools import wraps


from metamap.models import SqoopHive2Mysql

logger = logging.getLogger('django')


def my_decorator(key='s'):
    def _my_decorator(view_func):
        def _decorator(request, *args, **kwargs):
            # maybe do something before the view_func call
            print('I got args %s ' % len(args))
            print('I got kwargs %s ' % kwargs)
            i = kwargs[key]
            print(SqoopHive2Mysql.objects.get(pk=i).name)
            print('I got request %s ' % request)
            response = view_func(request, *args, **kwargs)
            # maybe do something after the view_func call
            return response

        return wraps(view_func)(_decorator)

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
