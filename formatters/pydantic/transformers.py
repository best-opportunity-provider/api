from typing import (
    Callable,
)
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
    MISSING_DISCRIMINATOR = 106
    INVALID_DISCRIMINATOR = 107


def inherit_transformations_from(*classes: type[ErrorTransformer]):
    """
    Method decorator, that allows you to chain transformers (and override error messages).

    The orders of calls goes:
        1. The method, that is being decorated
        2. Transformation functions from `classes` in right order

    Resulting function return value is the first non-null value, that is returned
    from the process of calling transformers chain. Note that the resulting
    function does not execute remaining transformers in chain after the first non-null return.
    """

    def wrapper[**P](fn: Callable[P, Error | None]) -> Callable[P, Error | None]:
        def wrapped(*args: P.args, **kwargs: P.kwargs) -> Error | None:
            if (error := fn(*args, **kwargs)) is not None:
                return error
            for cls in classes:
                if (error := cls.__call__(*args, **kwargs)) is not None:
                    return error

        return wrapped

    return wrapper


def extend_and_override(
    *general_bases: type[ErrorTransformer], error_bases: list[type[ErrorTransformer]] | None = None
):
    """
    Class decorator, that encapsulates all the complex logic, behind transformer inheritance.

    Arguments to the decorator are divided into two categories: ones that are passed through
    `*args` (also called general bases), and ones that are passed through `error_bases` keyword argument.

    General bases are used to inherit transformation functions, while error bases only modify `Errors` class.
    Transformation inheritance is done via `inherit_transformations_from` decorator and follows its execution order.

    The `Errors` class on the resulting class follows this inheritance order:
        1. `Errors` on the class, that is being decorated
        2. `Errors` on classes from `error_bases` in the right order
        3. `Errors` on classes from `general_bases` in the right order

    This decorator can also modify only error messages. To do so call the `add_dummy_call` decorator on your class beforehand.
    """

    assert len(general_bases) > 0
    if error_bases is None:
        error_bases = []

    def wrapper(cls: type[ErrorTransformer]) -> type[ErrorTransformer]:
        class Wrapped(cls, *general_bases):
            class Errors(
                cls.Errors,
                *(base.Errors for base in error_bases),
                *(base.Errors for base in general_bases),
            ):
                pass

            @inherit_transformations_from(cls, *general_bases)
            def __call__(self, error_code: str, **kwargs) -> Errors | None:
                pass

        return Wrapped

    return wrapper


def dummy_call_fn(self, error_code: str, **kwargs) -> None:
    pass


def add_dummy_call(cls: type) -> type[ErrorTransformer]:
    """
    Class decorator, that adds meaningless `__call__` method to your class in order for it to
    comply to `ErrorTransformer` requirements. Call to this dummy method always returns `None`.
    Calling this decorator on class, that already contains `__call__` will override it.

    Can be used together with `extend_and_override` in order to provide simple `Errors` override interface.
    to do so your class should look something like this:

    ```
    @extend_and_override(...)
    @add_dummy_call
    class MyErrorTransformer:
        class Errors:
            ...
    ```
    """

    cls.__call__ = dummy_call_fn
    return cls


class ModifiedErrorTransformer(ErrorTransformer):
    def __init__(self, base: ErrorTransformer, additional: ErrorTransformer):
        self.base = base
        self.additional = additional

    def __call__(self, error_code: str, **kwargs) -> Error | None:
        if (error := self.additional(error_code, **kwargs)) is not None:
            return error
        return self.base(error_code, **kwargs)


def modify(base: ErrorTransformer, additional: ErrorTransformer) -> ErrorTransformer:
    """
    Simple wrapper around `ModifiedErrorTransformer` constructor call. Returns the transformer
    instance, that chains `additional` and `base`. Note that `Errors` from `additional` do not override
    ones from `base`. Proper chaining with `Errors` overriding requires type-level manipulations and
    can't be done on instance level.
    """

    return ModifiedErrorTransformer(base, additional)


class MissingErrorTransformer(ErrorTransformer):
    class Errors:
        MISSING = TranslatedString(
            en='Missing required field',
            ru='Отсутствует необходимое поле',
        )

    def __call__(self, error_code: str, *, language: Language, **kwargs) -> Error | None:
        if error_code == 'missing':
            return Error(
                type=ErrorCode.MISSING.value,
                message=self.Errors.MISSING.get_translation(language),
            )


@extend_and_override(MissingErrorTransformer)
class IntErrorTransformer:
    class Errors:
        TYPE = TranslatedString(
            en='Field must be an integer',
            ru='Поле должно быть целым числом',
        )
        GE = TranslatedString(
            en='Field must be greater than or equal to {}',
            ru='Поле должно быть меньше или равно {}',
        )
        LE = TranslatedString(
            en='Field must be less than or equal to {}',
            ru='Поле должно быть меньше или равно {}',
        )

    def __init__(self, *, lower_bound: int | None = None, upper_bound: int | None = None):
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

    def __call__(self, error_code: str, *, language: Language, **kwargs) -> Error | None:
        match error_code:
            case 'int_type' | 'int_parsing':
                return Error(
                    type=ErrorCode.WRONG_TYPE.value,
                    message=self.Errors.TYPE.get_translation(language),
                )
            case 'less_than_equal':
                return Error(
                    type=ErrorCode.NOT_IN_RANGE.value,
                    message=self.Errors.LE.get_translation(language).format(self.upper_bound),
                )
            case 'greater_than_equal':
                return Error(
                    type=ErrorCode.NOT_IN_RANGE.value,
                    message=self.Errors.GE.get_translation(language).format(self.lower_bound),
                )


@extend_and_override(MissingErrorTransformer)
class BoolErrorTransformer:
    class Errors:
        TYPE = TranslatedString(
            en='Field must be a boolean',
            ru='Поле должно быть булевого типа',
        )

    def __call__(self, error_code: str, *, language: Language, **kwargs) -> Error | None:
        match error_code:
            case 'bool_type' | 'bool_parsing':
                return Error(
                    type=ErrorCode.WRONG_TYPE.value,
                    message=self.Errors.TYPE.get_translation(language),
                )


@extend_and_override(MissingErrorTransformer)
class StringErrorTransformer:
    class Errors:
        TYPE = TranslatedString(
            en='Field must be a string',
            ru='Поле должно быть строкой',
        )
        TOO_SHORT = TranslatedString(
            en='Field must contain at least {} characters',
            ru='Поле должно содержать не менее {} символов',
        )
        TOO_LONG = TranslatedString(
            en='Field can contain at most {} characters',
            ru='Поле может содержать не более {} символов',
        )

    def __init__(self, *, min_length: int | None = None, max_length: int | None = None):
        self.min_length = min_length
        self.max_length = max_length

    def __call__(self, error_code: str, *, language: Language, **kwargs) -> Error | None:
        match error_code:
            case 'string_type':
                return Error(
                    type=ErrorCode.WRONG_TYPE.value,
                    message=self.Errors.TYPE.get_translation(language),
                )
            case 'string_too_short':
                return Error(
                    type=ErrorCode.LENGTH_NOT_IN_RANGE.value,
                    message=self.Errors.TOO_SHORT.get_translation(language).format(self.min_length),
                )
            case 'string_too_long':
                return Error(
                    type=ErrorCode.LENGTH_NOT_IN_RANGE.value,
                    message=self.Errors.TOO_LONG.get_translation(language).format(self.max_length),
                )


@extend_and_override(MissingErrorTransformer)
class ListErrorTransformer:
    class Errors:
        TYPE = TranslatedString(
            en='Field must be a list',
            ru='Поле должно быть массивом',
        )
        TOO_SHORT = TranslatedString(
            en='Field must contain at least {} element(s)',
            ru='Поле должно содержать не менее {} элемента(ов)',
        )
        TOO_LONG = TranslatedString(
            en='Field can contain at most {} element(s)',
            ru='Поле может содержать не более {} элемента(ов)',
        )

    def __init__(self, *, min_length: int | None = None, max_length: int | None = None):
        self.min_length = min_length
        self.max_length = max_length

    def __call__(self, error_code: str, *, language: Language, **kwargs) -> Error | None:
        match error_code:
            case 'list_type':
                return Error(
                    type=ErrorCode.WRONG_TYPE.value,
                    message=self.Errors.TYPE.get_translation(language),
                )
            case 'too_short':
                return Error(
                    type=ErrorCode.LENGTH_NOT_IN_RANGE.value,
                    message=self.Errors.TOO_SHORT.get_translation(language).format(self.min_length),
                )
            case 'too_long':
                return Error(
                    type=ErrorCode.LENGTH_NOT_IN_RANGE.value,
                    message=self.Errors.TOO_LONG.get_translation(language).format(self.max_length),
                )


@extend_and_override(ListErrorTransformer)
@add_dummy_call
class RootListErrorTransformer:
    class Errors:
        TYPE = TranslatedString(
            en='Object must be a list',
            ru='Объект должен быть массивом',
        )
        TOO_SHORT = TranslatedString(
            en='Object must contain at least {} element(s)',
            ru='Объект должен содержать не менее {} элемента(ов)',
        )
        TOO_LONG = TranslatedString(
            en='Object can contain at most {} element(s)',
            ru='Объект может содержать не более {} элемента(ов)',
        )


@extend_and_override(ListErrorTransformer)
class DictErrorTransformer:
    class Errors:
        TYPE = TranslatedString(
            en='Field must be a dictionary',
            ru='Поле должно быть словарем',
        )

    def __init__(self, *, min_length: int | None = None, max_length: int | None = None):
        super().__init__(min_length=min_length, max_length=max_length)

    def __call__(self, error_code: str, *, language: Language, **kwargs) -> Error | None:
        if error_code == 'dict_type':
            return Error(
                type=ErrorCode.WRONG_TYPE.value,
                message=self.Errors.TYPE.get_translation(language),
            )


@extend_and_override(DictErrorTransformer, error_bases=[RootListErrorTransformer])
@add_dummy_call
class RootDictErrorTransformer:
    class Errors:
        TYPE = TranslatedString(
            en='Object must be a dictionary',
            ru='Объект должен быть словарем',
        )


@extend_and_override(MissingErrorTransformer)
class NestedModelErrorTransformer:
    class Errors:
        TYPE = TranslatedString(
            en='Field must be a dictionary',
            ru='Поле должно быть словарем',
        )

    def __call__(self, error_code: str, *, language: Language, **kwargs) -> Error | None:
        if error_code == 'model_attributes_type':
            return Error(
                type=ErrorCode.WRONG_TYPE.value,
                message=self.Errors.TYPE.get_translation(language),
            )


@extend_and_override(NestedModelErrorTransformer)
class TaggedUnionErrorTransformer:
    class Errors:
        TAG_NOT_FOUND = TranslatedString(
            en='Object misses union discriminator field `{}`',
            ru='Объект не содержит поле-дискриминатор `{}`',
        )
        TAG_INVALID = TranslatedString(
            en='Object has invalid union discriminator value',
            ru='Поле-дискриминатор объекта содержит некорректное значение',
        )

    def __init__(self, *, discriminator_field: str):
        self.discriminator_field = discriminator_field

    def __call__(self, error_code: str, *, language: Language, **kwargs) -> Error | None:
        match error_code:
            case 'union_tag_not_found':
                return Error(
                    type=ErrorCode.MISSING_DISCRIMINATOR,
                    message=self.TAG_NOT_FOUND.get_translation(language).format(
                        self.discriminator_field
                    ),
                )
            case 'union_tag_invalid':
                return Error(
                    type=ErrorCode.INVALID_DISCRIMINATOR,
                    message=self.TAG_INVALID.get_translation(language),
                )
