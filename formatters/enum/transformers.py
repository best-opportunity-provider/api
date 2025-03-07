from enum import Enum
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


class DictErrorTransformer[E: Enum](base.ErrorTransformer):
    def __init__(self, errors: dict[E, Error]):
        self.errors = errors

    def __call__(
        self,
        error_code: E,
        *,
        language: Language,
        **kwargs,
    ) -> tuple[Error, list[str]] | None:
        if error_code not in self.errors:
            raise ValueError('Unhandled error kind')
        error_type, error_message, path = self.errors[error_code].as_tuple()
        return (
            base.Error(
                type=(error_type if error_type is not None else error_code.value),
                message=error_message.get_translation(language),
            ),
            path,
        )
