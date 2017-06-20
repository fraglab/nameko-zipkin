nameko-zipkin
-------------

Zipkin tracing for nameko framework

Install
-------

```
pip install nameko-zipkin 
```

Usage
-----

#### Services

```python
from nameko_zipkin import Zipkin
from nameko.rpc import rpc


class Service:
    name = 'service'
    zipkin = Zipkin() # Dependency provider injects py_zipkin.zipkin.zipkin_span object
    
    @rpc
    def method(self):
        assert self.zipkin.service_name == Service.name
        assert self.zipkin.span_name == Service.method.__name__
```

#### Standalone rpc

```python
from py_zipkin import zipkin
from nameko_zipkin import monkey_patch
from nameko_zipkin.transport import HttpHandler
from nameko.standalone.rpc import ClusterRpcProxy


handler = HttpHandler('http://localhost:9411/api/v1/spans').handle
monkey_patch(handler)

with zipkin.zipkin_server_span('RootService',
                               'RootMethod',
                               sample_rate=100.,
                               transport_handler=handler):
    with ClusterRpcProxy({'AMQP_URI': "pyamqp://guest:guest@localhost"}) as proxy:
        proxy.service.method()
```

How it works
------------

* monkey_patch patches MethodProxy class to initialize a client span, it's called in dependency provider setup method
* On service method call a server span is created
* Trace parameters (trace_id, parent_span_id, etc.) are passed through context data and are accessible in py_zipkin.thread_local.get_zipkin_attrs
* If there are no parameters, request isn't traced
* Child service calls are also supported
* Trace results are reported through handler classes in nameko_zipkin.transport


Configuration
-------------

ZIPKIN section must be added to nameko service config.yaml

```yaml
ZIPKIN:
    HANDLER: HttpHandler
    HANDLER_PARAMS:
      url: http://localhost:9411/api/v1/spans
```

Planed changes
--------------

* Trace initialization on trace attrs absence in context data
* Kafka transport support
* Custom handlers support in config.yaml ('my_module.MyHandler')