from nameko.rpc import MethodProxy, RpcReply
from py_zipkin import zipkin


class TracedRpcReply(RpcReply):
    def __init__(self, reply_event, zipkin_span):
        super().__init__(reply_event)
        self.zipkin_span = zipkin_span

    def result(self):
        try:
            return super().result()
        finally:
            self.zipkin_span.stop()


def monkey_patch(transport_handler):
    _call = MethodProxy._call

    def _call_traced(self: MethodProxy, *args, **kwargs):
        span = zipkin.zipkin_client_span(self.service_name,
                                         self.method_name,
                                         transport_handler=transport_handler)
        self.worker_ctx.data.update(zipkin.create_http_headers_for_new_span())
        reply = _call(self, *args, **kwargs)
        span.start()
        return TracedRpcReply(reply.reply_event, span)

    if _call.__name__ != _call_traced.__name__:
        MethodProxy._call = _call_traced
