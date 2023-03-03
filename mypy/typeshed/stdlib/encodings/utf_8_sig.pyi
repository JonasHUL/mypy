import codecs
from _typeshed import ReadableBuffer

class IncrementalEncoder(codecs.IncrementalEncoder):
    def __init__(self, errors: str = "strict") -> None: ...
    def encode(self, input: str, final: bool = False) -> bytes: ...
    def getstate(self) -> int: ...  # type: ignore[override]
    def setstate(self, state: int) -> None: ...  # type: ignore[override]

class IncrementalDecoder(codecs.BufferedIncrementalDecoder):
    def __init__(self, errors: str = "strict") -> None: ...
    def _buffer_decode(self, input: ReadableBuffer, errors: str | None, final: bool) -> tuple[str, int]: ...

class StreamWriter(codecs.StreamWriter):
    def encode(self, input: str, errors: str | None = "strict") -> tuple[bytes, int]: ...

class StreamReader(codecs.StreamReader):
    def decode(self, input: ReadableBuffer, errors: str | None = "strict") -> tuple[str, int]: ...

def getregentry() -> codecs.CodecInfo: ...
def encode(input: str, errors: str | None = "strict") -> tuple[bytes, int]: ...
def decode(input: ReadableBuffer, errors: str | None = "strict") -> tuple[str, int]: ...
