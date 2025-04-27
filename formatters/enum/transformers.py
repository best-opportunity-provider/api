from typing import Protocol
from dataclasses import dataclass

from ..base import (
    Language,
    TranslatedString,
)
from . import base

# Helper global variable to signal, that error code should be inferred from enum value
infer = None


@dataclass
class Error:
    type: int | None
    message: TranslatedString
    path: list[str]

    def as_tuple(self) -> tuple[int | None, TranslatedString, list[str]]:
        return self.type, self.message, self.path


class TransformerCallable(Protocol):
    def __call__(self, **kwargs) -> Error: ...


class SingleErrorTransformer(base.ErrorTransformer):
    def __init__(self, error: Error | TransformerCallable):
        self.error = error

    def __call__(
        self,
        error_code: None,
        *,
        language: Language,
        **kwargs,
    ) -> tuple[base.Error, list[str]] | None:
        if isinstance(self.error, Error):
            error = self.error
        else:
            error = self.error(language=language, **kwargs)
        error_type, error_message, path = error.as_tuple()
        return (
            base.Error(
                type=error_type,
                message=error_message.get_translation(language),
            ),
            path,
        )


class DictErrorTransformer[E](base.ErrorTransformer):
    def __init__(self, errors: dict[E, Error | TransformerCallable]):
        self.errors = errors

    def __call__(
        self,
        error_code: E,
        *,
        language: Language,
        **kwargs,
    ) -> tuple[base.Error, list[str]] | None:
        if error_code not in self.errors:
            raise ValueError('Unhandled error kind')
        handler = self.errors[error_code]
        if isinstance(handler, Error):
            error = handler
        else:
            error = handler(language=language, **kwargs)
        error_type, error_message, path = error.as_tuple()
        return (
            base.Error(
                type=(error_type if error_type is not None else error_code.value),
                message=error_message.get_translation(language),
            ),
            path,
        )
