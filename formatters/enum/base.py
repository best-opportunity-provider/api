from typing import Protocol

from ..base import (
    Error,
    ErrorTrace,
)


class ErrorTransformer[E](Protocol):
    def __call__(self, error_code: E, **kwargs) -> tuple[Error, list[str]] | None: ...


class ErrorAppender[E]:
    def __init__(self, transformer: ErrorTransformer[E]):
        self.transformer = transformer

    @classmethod
    def get_errors_list(cls, trace: ErrorTrace, path: list[str]) -> list[Error]:
        for part in path:
            assert not isinstance(trace.errors, list)
            if trace.errors is None:
                trace.errors = {}
            if part not in trace.errors:
                trace.errors[part] = ErrorTrace()
            trace = trace.errors[part]
        assert not isinstance(trace.errors, dict)
        if trace.errors is None:
            trace.errors = []
        return trace.errors

    def __call__(self, trace: ErrorTrace, error_code: E, **kwargs) -> None:
        transformed_error = self.transformer(error_code, **kwargs)
        if transformed_error is None:
            raise ValueError('Unhandled error kind')
        error, path = transformed_error
        self.get_errors_list(trace, path).append(error)
