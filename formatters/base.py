from typing import (
    TypedDict,
)
from enum import StrEnum
from dataclasses import dataclass


class Error(TypedDict):
    type: int
    message: str


@dataclass
class ErrorTrace:
    type Underlying = dict[str, Underlying] | list[Error]

    errors: dict[str, 'ErrorTrace'] | list[Error] | None = None
    error_code: int | None = None

    def to_underlying(self) -> Underlying:
        assert self.errors is not None
        if isinstance(self.errors, list):
            return self.errors
        return {field: trace.to_underlying() for field, trace in self.errors.items()}


class Language(StrEnum):
    ENGLISH = 'en'
    RUSSIAN = 'ru'


@dataclass
class TranslatedString:
    en: str
    ru: str

    def get_translation(self, language: Language) -> str:
        return getattr(self, language.value)
