from nameko.rpc import MethodProxy, RpcReply
from py_zipkin import zipkin

from nameko_zipkin.utils import stop_span, start_span


class TracedRpcReply(RpcReply):
    def __init__(self, reply_event, zipkin_span):
        super().__init__(reply_event)
        self.zipkin_span = zipkin_span

    def result(self):
        try:
            return super().result()
        finally:
            stop_span(self.zipkin_span)


def monkey_patch(transport_handler):
    _call = MethodProxy._call

    def _call_traced(self: MethodProxy, *args, **kwargs):
        span = zipkin.zipkin_client_span(self.service_name,
                                         self.method_name,
                                         transport_handler=transport_handler)
        start_span(span)
        self.worker_ctx.data.update(zipkin.create_http_headers_for_new_span())
        try:
            reply = _call(self, *args, **kwargs)
        except:
            stop_span(span)
            raise
        return TracedRpcReply(reply.reply_event, span)

    if _call.__name__ != _call_traced.__name__:
        MethodProxy._call = _call_traced
