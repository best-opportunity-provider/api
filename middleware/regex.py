from typing import Annotated
import re

from fastapi import (
    Path,
    Query,
)

import formatters as fmt


def error_fn(*, transformed_error_code: int, path: list[str], **kwargs) -> fmt.enum.Error:
    return fmt.enum.Error(
        type=transformed_error_code,
        message=fmt.TranslatedString(
            en="Regex is not valid",
            ru='Паттерн регулярного выражения не прошел проверку на валидацию',
        ),
        path=path,
    )


error_appender = fmt.enum.ErrorAppender[None](
    transformer=fmt.enum.transformers.SingleErrorTransformer(error_fn),
)


def validate_regex(
    regex: str,
    *,
    error_code: int,
    path: list[str],
) -> str | fmt.ErrorTrace:
    try:
        re.compile(regex)
    except re.PatternError:
        error = fmt.ErrorTrace()
        error_appender(
            error,
            None,
            transformed_error_code=error_code,
            path=path,
        )
        return error
    return regex
