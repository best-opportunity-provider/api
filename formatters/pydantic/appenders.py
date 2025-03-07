from .base import (
    ErrorTrace,
    ErrorAppender,
    ErrorTransformer,
)


class FieldErrorAppender(ErrorAppender):
    def __init__(self, transformer: ErrorTransformer):
        self.transformer = transformer

    def append_error(
        self,
        trace: ErrorTrace,
        error_code: str,
        path: list[str],
        *,
        field_name: str,
        **kwargs,
    ) -> None:
        error = self.transformer(error_code, field_name=field_name, **kwargs)
        if error is None:
            raise ValueError('Unhandled error kind')
        if field_name not in trace:
            trace[field_name] = []
        trace[field_name].append(error)

    def __call__(
        self,
        trace: ErrorTrace,
        error_code: str,
        loc: list[str],
        **kwargs,
    ) -> None:
        self.append_error(trace, error_code, loc, **kwargs)


class DictErrorAppender(ErrorAppender):
    def __init__(
        self,
        element_appenders: dict[str, ErrorAppender],
        root_transformer: ErrorTransformer | None = None,
        extra_appender: ErrorAppender | None = None,
    ):
        self.element_appenders = element_appenders
        self.root_transformer = root_transformer
        self.extra_appender = extra_appender

    def append_error(
        self,
        trace: ErrorTrace,
        error_code: str,
        path: list[str],
        *,
        field_name: str,
        **kwargs,
    ) -> None:
        if len(path) == 0:  # error on top level of dict, excludes possibility for inner errors
            if self.root_transformer is None:
                raise ValueError('Unhandled error path')
            error = self.root_transformer(error_code, field_name=field_name, **kwargs)
            if error is None:
                raise ValueError('Unhandled error kind')
            if field_name not in trace:
                trace[field_name] = []
            trace[field_name].append(error)
            return
        if field_name not in trace:
            trace[field_name] = {}
        element_field_name: str = path[0]
        kwargs.update(field_name=element_field_name)
        element_appender = self.element_appenders.get(element_field_name)
        if element_appender is not None:
            element_appender(trace[field_name], error_code, path[1:], **kwargs)
        elif self.extra_appender is not None:
            self.extra_appender(trace[field_name], error_code, path[1:], **kwargs)
        else:
            raise ValueError('Unhandled error path')

    def __call__(
        self,
        trace: ErrorTrace,
        error_code: str,
        path: list[str],
        **kwargs,
    ) -> None:
        self.append_error(trace, error_code, path, **kwargs)


class ListErrorAppender(ErrorAppender):
    def __init__(
        self,
        element_appender: ErrorAppender,
        root_transformer: ErrorTransformer | None = None,
    ):
        self.element_appender = element_appender
        self.root_transformer = root_transformer

    def append_error(
        self,
        trace: ErrorTrace,
        error_code: str,
        path: list[str],
        *,
        field_name: str,
        **kwargs,
    ) -> None:
        if len(path) == 0:  # error on top level of list, excludes possibility for inner errors
            if self.root_transformer is None:
                raise ValueError('Unhandled error path')
            error = self.root_transformer(error_code, field_name=field_name, **kwargs)
            if error is None:
                raise ValueError('Unhandled error kind')
            if field_name not in trace:
                trace[field_name] = []
            trace[field_name].append(error)
            return
        if field_name not in trace:
            trace[field_name] = {}
        kwargs.update(field_name=path[0])
        self.element_error_appender(trace[field_name], error_code, path[1:], **kwargs)

    def __call__(
        self,
        trace: ErrorTrace,
        error_code: str,
        path: list[str],
        **kwargs,
    ) -> None:
        self.append_error(trace, error_code, path, **kwargs)
