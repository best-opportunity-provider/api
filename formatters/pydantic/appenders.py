from .base import (
    ErrorTrace,
    ErrorAppender,
    ErrorTransformer,
)


class FieldErrorAppender(ErrorAppender):
    def __init__(self, transformer: ErrorTransformer):
        self.transformer = transformer

    def append_error(self, trace: ErrorTrace, error_code: str, path: list[str], **kwargs) -> None:
        assert len(path) == 0
        error = self.transformer(error_code, **kwargs)
        if error is None:
            raise ValueError('Unhandled error kind')
        assert not isinstance(trace.errors, dict)
        if trace.errors is None:
            trace.errors = []
        trace.errors.append(error)

    def __call__(self, trace: ErrorTrace, error_code: str, loc: list[str], **kwargs) -> None:
        self.append_error(trace, error_code, loc, **kwargs)


class DictErrorAppender(ErrorAppender):
    def __init__(
        self,
        element_appenders: dict[str, ErrorAppender | ErrorTransformer],
        root_transformer: ErrorTransformer | None = None,
        extra_appender: ErrorAppender | None = None,
    ):
        self.element_appenders: dict[str, ErrorAppender] = {
            field: handler if isinstance(handler, ErrorAppender) else FieldErrorAppender(handler)
            for field, handler in element_appenders.items()
        }
        self.root_transformer = root_transformer
        self.extra_appender = extra_appender

    def append_error(self, trace: ErrorTrace, error_code: str, path: list[str], **kwargs) -> None:
        if len(path) == 0:  # error on top level of dict, excludes possibility for inner errors
            if self.root_transformer is None:
                raise ValueError('Unhandled error path')
            error = self.root_transformer(error_code, **kwargs)
            if error is None:
                raise ValueError('Unhandled error kind')
            assert not isinstance(trace.errors, dict)
            if trace.errors is None:
                trace.errors = []
            return trace.errors.append(error)
        assert not isinstance(trace.errors, list)
        if trace.errors is None:
            trace.errors = {}
        element_field_name: str = path[0]
        if element_field_name not in trace.errors:
            trace.errors[element_field_name] = ErrorTrace()
        kwargs.update(field_name=element_field_name)
        element_appender = self.element_appenders.get(element_field_name)
        if element_appender is not None:
            element_appender(trace.errors[element_field_name], error_code, path[1:], **kwargs)
        elif self.extra_appender is not None:
            self.extra_appender(trace.errors[element_field_name], error_code, path[1:], **kwargs)
        else:
            raise ValueError('Unhandled error path')

    def __call__(self, trace: ErrorTrace, error_code: str, path: list[str], **kwargs) -> None:
        self.append_error(trace, error_code, path, **kwargs)


class ListErrorAppender(ErrorAppender):
    def __init__(
        self,
        element_appender: ErrorAppender | ErrorTransformer,
        root_transformer: ErrorTransformer | None = None,
    ):
        self.element_appender = (
            element_appender
            if isinstance(element_appender, ErrorAppender)
            else FieldErrorAppender(element_appender)
        )
        self.root_transformer = root_transformer

    def append_error(self, trace: ErrorTrace, error_code: str, path: list[str], **kwargs) -> None:
        if len(path) == 0:  # error on top level of list, excludes possibility for inner errors
            if self.root_transformer is None:
                raise ValueError('Unhandled error path')
            error = self.root_transformer(error_code, **kwargs)
            if error is None:
                raise ValueError('Unhandled error kind')
            assert not isinstance(trace.errors, dict)
            if trace.errors is None:
                trace.errors = []
            return trace.errors.append(error)
        assert not isinstance(trace.errors, list)
        if trace.errors is None:
            trace.errors = {}
        element_field_name = path[0]
        if element_field_name not in trace.errors:
            trace.errors[element_field_name] = ErrorTrace()
        kwargs.update(field_name=element_field_name)
        self.element_error_appender(
            trace.errors[element_field_name], error_code, path[1:], **kwargs
        )

    def __call__(self, trace: ErrorTrace, error_code: str, path: list[str], **kwargs) -> None:
        self.append_error(trace, error_code, path, **kwargs)
