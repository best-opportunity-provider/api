from typing import Protocol
from enum import Enum

from ..base import (
    Error,
    ErrorTrace,
)


class ErrorTransformer[E: Enum](Protocol):
    def __call__(self, error_code: E, **kwargs) -> tuple[Error, list[str]] | None: ...


class ErrorAppender[E: Enum]:
    def __init__(self, transformer: ErrorTransformer[E]):
        self.transformer = transformer

    @classmethod
    def get_errors_list(cls, trace: ErrorTrace, path: list[str]) -> list[Error]:
        for part in path[:-1]:
            if part not in trace:
                trace[part] = {}
            elif not isinstance(trace[part], dict):
                raise ValueError('Conflicting errors')
            trace = trace[part]
        if path[-1] not in trace:
            trace[path[-1]] = []
        elif not isinstance(trace[path[-1]], list):
            raise ValueError('Confilicting errors')
        return trace[path[-1]]

    def __call__(self, trace: ErrorTrace, error_code: E, **kwargs) -> None:
        transformed_error = self.transformer(error_code, **kwargs)
        if transformed_error is None:
            raise ValueError('Unhandled error kind')
        error, path = transformed_error
        self.get_errors_list(trace, path).append(error)
