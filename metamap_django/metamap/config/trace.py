import django_opentracing

# OpenTracing settings

# if not included, defaults to False
# has to come before OPENTRACING_TRACER setting because python...
import opentracing
from django_opentracing import DjangoTracer
from django_opentracing import OpenTracingMiddleware

OPENTRACING_TRACE_ALL = True,

# defaults to []
# only valid if OPENTRACING_TRACE_ALL == True
OPENTRACING_TRACED_ATTRIBUTES = ['path']

# Callable that returns an `opentracing.Tracer` implementation.
OPENTRACING_TRACER_CALLABLE = 'opentracing.Tracer'

from jaeger_client import Config


class LazyOpenTracingMiddleware(OpenTracingMiddleware):
    '''Opentracing middleware which evaluates the tracer lazily.

    In part due to
    https://github.com/uber/jaeger-client-python/issues/60, and further because
    it's just a good idea to avoid issues like unintentionally shared file
    descriptors between processes, we need to initialize the jaeger tracer
    after the gunicorn fork. Since OpenTracingMiddleware is configured in
    MIDDLEWARE_CLASSES in sites/postmates/settings/base.py, which is imported
    pre-fork, this presents a problem.

    This class modifies OpenTracingMiddleware such that it will do nothing
    until a global tracer exists at `opentracing.tracer`.
    '''

    def __init__(self):
        '''Do nothing.

        OpenTracingMiddleware.__init__ only sets self._tracer, which we don't
        want to do.
        '''

    @property
    def _tracer(self):
        '''Get a DjangoTracer, or None if opentracing not initialized.

        Once opentracing is initialized (indicated by the presence of
        `opentracing.tracer`), will return the same instance of DjangoTracer in
        perpetuity.
        '''
        try:
            return self._django_tracer
        except AttributeError:
            pass

        try:
            tracer = opentracing.tracer
        except AttributeError:
            return None

        self._django_tracer = DjangoTracer(tracer)
        return self._tracer

    def process_view(self, *a, **kw):
        if self._tracer is None:
            return
        OpenTracingMiddleware.process_view(self, *a, **kw)

    def process_response(self, request, response):
        if self._tracer is None:
            return response
        return OpenTracingMiddleware.process_response(self, request, response)


# config = Config(
#     config={
#         'sampler': {
#             'type': 'const',
#             'param': 1
#         },
#         'local_agent' : {
#             'reporting_host': '10.103.27.152'
#         }
#     },
#     service_name='will-django'
# )

# OPENTRACING_TRACER = config.initialize_tracer()



# Parameters for the callable (Depending on the tracer implementation chosen)
OPENTRACING_TRACER_PARAMETERS = {
    # 'example-parameter-host': 'collector',
}
