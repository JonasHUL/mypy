import http.server
import pydoc
import socketserver
from collections.abc import Callable, Iterable, Mapping
from re import Pattern
from typing import Any, ClassVar, Protocol
from typing_extensions import TypeAlias
from xmlrpc.client import Fault, _Marshallable

# The dispatch accepts anywhere from 0 to N arguments, no easy way to allow this in mypy
class _DispatchArity0(Protocol):
    def __call__(self) -> _Marshallable: ...

class _DispatchArity1(Protocol):
    def __call__(self, __arg1: _Marshallable) -> _Marshallable: ...

class _DispatchArity2(Protocol):
    def __call__(self, __arg1: _Marshallable, __arg2: _Marshallable) -> _Marshallable: ...

class _DispatchArity3(Protocol):
    def __call__(self, __arg1: _Marshallable, __arg2: _Marshallable, __arg3: _Marshallable) -> _Marshallable: ...

class _DispatchArity4(Protocol):
    def __call__(
        self, __arg1: _Marshallable, __arg2: _Marshallable, __arg3: _Marshallable, __arg4: _Marshallable
    ) -> _Marshallable: ...

class _DispatchArityN(Protocol):
    def __call__(self, *args: _Marshallable) -> _Marshallable: ...

_DispatchProtocol: TypeAlias = (
    _DispatchArity0 | _DispatchArity1 | _DispatchArity2 | _DispatchArity3 | _DispatchArity4 | _DispatchArityN
)

def resolve_dotted_attribute(obj: Any, attr: str, allow_dotted_names: bool = True) -> Any: ...  # undocumented
def list_public_methods(obj: Any) -> list[str]: ...  # undocumented

class SimpleXMLRPCDispatcher:  # undocumented
    funcs: dict[str, _DispatchProtocol]
    instance: Any | None
    allow_none: bool
    encoding: str
    use_builtin_types: bool
    def __init__(self, allow_none: bool = False, encoding: str | None = None, use_builtin_types: bool = False) -> None: ...
    def register_instance(self, instance: Any, allow_dotted_names: bool = False) -> None: ...
    def register_function(self, function: _DispatchProtocol | None = None, name: str | None = None) -> Callable[..., Any]: ...
    def register_introspection_functions(self) -> None: ...
    def register_multicall_functions(self) -> None: ...
    def _marshaled_dispatch(
        self,
        data: str,
        dispatch_method: Callable[[str | None, tuple[_Marshallable, ...]], Fault | tuple[_Marshallable, ...]] | None = None,
        path: Any | None = None,
    ) -> str: ...  # undocumented
    def system_listMethods(self) -> list[str]: ...  # undocumented
    def system_methodSignature(self, method_name: str) -> str: ...  # undocumented
    def system_methodHelp(self, method_name: str) -> str: ...  # undocumented
    def system_multicall(self, call_list: list[dict[str, _Marshallable]]) -> list[_Marshallable]: ...  # undocumented
    def _dispatch(self, method: str, params: Iterable[_Marshallable]) -> _Marshallable: ...  # undocumented

class SimpleXMLRPCRequestHandler(http.server.BaseHTTPRequestHandler):
    rpc_paths: ClassVar[tuple[str, ...]]
    encode_threshold: int  # undocumented
    aepattern: Pattern[str]  # undocumented
    def accept_encodings(self) -> dict[str, float]: ...
    def is_rpc_path_valid(self) -> bool: ...
    def do_POST(self) -> None: ...
    def decode_request_content(self, data: bytes) -> bytes | None: ...
    def report_404(self) -> None: ...

class SimpleXMLRPCServer(socketserver.TCPServer, SimpleXMLRPCDispatcher):
    _send_traceback_handler: bool
    def __init__(
        self,
        addr: tuple[str, int],
        requestHandler: type[SimpleXMLRPCRequestHandler] = ...,
        logRequests: bool = True,
        allow_none: bool = False,
        encoding: str | None = None,
        bind_and_activate: bool = True,
        use_builtin_types: bool = False,
    ) -> None: ...

class MultiPathXMLRPCServer(SimpleXMLRPCServer):  # undocumented
    dispatchers: dict[str, SimpleXMLRPCDispatcher]
    def __init__(
        self,
        addr: tuple[str, int],
        requestHandler: type[SimpleXMLRPCRequestHandler] = ...,
        logRequests: bool = True,
        allow_none: bool = False,
        encoding: str | None = None,
        bind_and_activate: bool = True,
        use_builtin_types: bool = False,
    ) -> None: ...
    def add_dispatcher(self, path: str, dispatcher: SimpleXMLRPCDispatcher) -> SimpleXMLRPCDispatcher: ...
    def get_dispatcher(self, path: str) -> SimpleXMLRPCDispatcher: ...

class CGIXMLRPCRequestHandler(SimpleXMLRPCDispatcher):
    def __init__(self, allow_none: bool = False, encoding: str | None = None, use_builtin_types: bool = False) -> None: ...
    def handle_xmlrpc(self, request_text: str) -> None: ...
    def handle_get(self) -> None: ...
    def handle_request(self, request_text: str | None = None) -> None: ...

class ServerHTMLDoc(pydoc.HTMLDoc):  # undocumented
    def docroutine(  # type: ignore[override]
        self,
        object: object,
        name: str,
        mod: str | None = None,
        funcs: Mapping[str, str] = ...,
        classes: Mapping[str, str] = ...,
        methods: Mapping[str, str] = ...,
        cl: type | None = None,
    ) -> str: ...
    def docserver(self, server_name: str, package_documentation: str, methods: dict[str, str]) -> str: ...

class XMLRPCDocGenerator:  # undocumented
    server_name: str
    server_documentation: str
    server_title: str
    def set_server_title(self, server_title: str) -> None: ...
    def set_server_name(self, server_name: str) -> None: ...
    def set_server_documentation(self, server_documentation: str) -> None: ...
    def generate_html_documentation(self) -> str: ...

class DocXMLRPCRequestHandler(SimpleXMLRPCRequestHandler):
    def do_GET(self) -> None: ...

class DocXMLRPCServer(SimpleXMLRPCServer, XMLRPCDocGenerator):
    def __init__(
        self,
        addr: tuple[str, int],
        requestHandler: type[SimpleXMLRPCRequestHandler] = ...,
        logRequests: bool = True,
        allow_none: bool = False,
        encoding: str | None = None,
        bind_and_activate: bool = True,
        use_builtin_types: bool = False,
    ) -> None: ...

class DocCGIXMLRPCRequestHandler(CGIXMLRPCRequestHandler, XMLRPCDocGenerator):
    def __init__(self) -> None: ...
