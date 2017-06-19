from nameko.extensions import DependencyProvider
from py_zipkin import zipkin
from py_zipkin.util import generate_random_64bit_string

from nameko_zipkin.constants import *
from nameko_zipkin.transport import Transport
from nameko_zipkin.method_proxy import monkey_patch


class Zipkin(DependencyProvider):
    transport = Transport()

    def __init__(self):
        self.spans = {}

    def setup(self):
        monkey_patch(self.transport.handle)

    def get_dependency(self, worker_ctx):
        zipkin_attrs = _read_zipkin_attrs(worker_ctx)

        # if there are no zipking attrs in context data, request isn't traced
        # TODO: support trace initialization in such condition
        if not zipkin_attrs:
            return None
        span = zipkin.zipkin_server_span(worker_ctx.service_name,
                                         worker_ctx.entrypoint.method_name,
                                         zipkin_attrs=zipkin_attrs,
                                         transport_handler=self.transport.handle)
        self.spans[worker_ctx.call_id] = span
        return span

    def worker_setup(self, worker_ctx):
        span = self.spans.get(worker_ctx.call_id)
        if span:
            worker_ctx.data[PARENT_SPAN_ID_HEADER] = span.zipkin_attrs.span_id
            span.start()

    def worker_teardown(self, worker_ctx):
        span = self.spans.get(worker_ctx.call_id)
        if span:
            span.stop()
            del self.spans[worker_ctx.call_id]


def _read_zipkin_attrs(worker_ctx):
    if TRACE_ID_HEADER not in worker_ctx.data:
        return None
    return zipkin.ZipkinAttrs(trace_id=worker_ctx.data[TRACE_ID_HEADER],
                              span_id=generate_random_64bit_string(),
                              parent_span_id=worker_ctx.data[PARENT_SPAN_ID_HEADER],
                              flags=worker_ctx.data[FLAGS_HEADER],
                              is_sampled=worker_ctx.data[SAMPLED_HEADER] == '1')
