from typing import (
    TypedDict,
)
from enum import StrEnum
from dataclasses import dataclass


class Error(TypedDict):
    type: int
    message: str


type ErrorTrace = dict[str, ErrorTrace | list[Error]]


class Language(StrEnum):
    ENGLISH = 'en'
    RUSSIAN = 'ru'


@dataclass
class TranslatedString:
    en: str
    ru: str

    def get_translation(self, language: Language) -> str:
        return getattr(self, language.value)

    def __call__(self, language: Language) -> str:
        return self.get_translation(language)
