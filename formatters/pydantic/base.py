from abc import (
    ABC,
    abstractmethod,
)

from ..base import (
    Error,
    ErrorTrace,
)


class ErrorAppender(ABC):
    @abstractmethod
    def __call__(self, trace: ErrorTrace, error_code: str, path: list[str], **kwargs) -> None: ...


class ErrorTransformer(ABC):
    @abstractmethod
    def __call__(self, error_code: str, **kwargs) -> Error | None: ...
