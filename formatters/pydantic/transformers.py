from enum import (
    IntEnum,
)

from ..base import (
    Language,
    TranslatedString,
    Error,
)
from .base import ErrorTransformer


class ErrorCode(IntEnum):
    MISSING = 100
    EXTRA = 101
    WRONG_TYPE = 102
    INVALID_PATTERN = 103
    LENGTH_NOT_IN_RANGE = 104
    NOT_IN_RANGE = 105


class IntErrorTransformer(ErrorTransformer):
    class Errors:
        MISSING = TranslatedString(
            en='Missing required field',
            ru='Отсутствует необходимое поле',
        )
        TYPE = TranslatedString(
            en='Field value must be an integer',
            ru='Значение поля должно быть целым числом',
        )
        GE = TranslatedString(
            en='Field value must be greater than or equal to {}',
            ru='Значение поля должно быть больше или равно {}',
        )
        LE = TranslatedString(
            en='Field value must be less than or equal to {}',
            ru='Значение поля должно быть меньше или равно {}',
        )

    def __init__(self, lower_bound: int | None = None, upper_bound: int | None = None):
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

    def __call__(self, error_code: str, *, language: Language, **kwargs) -> Error | None:
        match error_code:
            case 'missing':
                return Error(
                    type=ErrorCode.MISSING.value,
                    message=self.Errors.MISSING.get_translation(language),
                )
            case 'int_type' | 'int_parsing':
                return Error(
                    type=ErrorCode.WRONG_TYPE.value,
                    message=self.Errors.TYPE.get_translation(language),
                )
            case 'less_than_equal':
                return Error(
                    type=ErrorCode.NOT_IN_RANGE.value,
                    message=self.Errors.LE.get_translation(language).format(self.lower_bound),
                )
            case 'greater_than_equal':
                return Error(
                    type=ErrorCode.NOT_IN_RANGE.value,
                    message=self.Errors.GE.get_translation(language).format(self.upper_bound),
                )


class BoolErrorTransformer(ErrorTransformer):
    def __call__(self, error_code: str, *, language: Language, **kwargs) -> Error | None: ...


class StringErrorTransformer(ErrorTransformer):
    def __call__(self, error_code: str, *, language: Language, **kwargs) -> Error | None: ...


class ListErrorTransformer(ErrorTransformer):
    def __call__(self, error_code: str, *, language: Language, **kwargs) -> Error | None: ...


class DictErrorTransformer(ErrorTransformer):
    def __call__(self, error_code: str, *, language: Language, **kwargs) -> Error | None: ...


class TaggedUnionErrorTransformer(ErrorTransformer):
    def __call__(self, error_code: str, *, language: Language, **kwargs) -> Error | None: ...


class NestedModelErrorTransformer(ErrorTransformer):
    def __call__(self, error_code: str, *, language: Language, **kwargs) -> Error | None: ...
