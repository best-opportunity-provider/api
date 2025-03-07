from typing import Protocol

from ..base import (
    Error,
    ErrorTrace,
)


class ErrorAppender(Protocol):
    def __call__(self, trace: ErrorTrace, error_code: str, path: list[str], **kwargs) -> None: ...


class ErrorTransformer(Protocol):
    def __call__(self, error_code: str, **kwargs) -> Error | None: ...
