from typing import (
    Annotated,
    Literal,
)
from datetime import date

import pydantic

from ..base import ObjectId
from database import OpportunityForm, User
from database.models.opportunity.form import (
    StringField,
    RegexField,
    TextField,
    EmailField,
    PhoneNumberField,
    ChoiceField,
    FileField,
    CheckBoxField,
    IntegerField,
    DateField,
)


def get_string_field_type(is_required: bool, max_length: int | None = None) -> type:
    match (is_required, max_length is None):
        case (True, True):
            return Annotated[str, pydantic.Field(min_length=1)]
        case (True, False):
            return Annotated[str, pydantic.Field(min_length=1, max_length=max_length)]
        case (False, False):
            return Annotated[str, pydantic.Field(max_length=max_length)]
        case _:
            return Annotated[str, pydantic.Field()]


def get_regex_field_type(is_required: bool, regex: str, max_length: int | None = None) -> type:
    match (is_required, max_length is None):
        case (True, True):
            return Annotated[str, pydantic.Field(min_length=1, pattern=regex)]
        case (True, False):
            return Annotated[
                str, pydantic.Field(min_length=1, max_length=max_length, pattern=regex)
            ]
        case (False, False):
            return Annotated[str, pydantic.Field(max_length=max_length, pattern=regex)]
        case _:
            return Annotated[str, pydantic.Field(pattern=regex)]


class PhoneNumberFieldModel(pydantic.BaseModel):
    model_config = {
        'extra': 'ignore',
    }

    country_id: ObjectId
    subscriber_number: Annotated[str, pydantic.Field(pattern=r'\d{6,12}')]


def get_phone_number_field_type(is_required: bool) -> type:
    if is_required:
        return Annotated[PhoneNumberFieldModel, pydantic.Field()]
    return Annotated[PhoneNumberFieldModel | None, pydantic.Field()]


def get_choice_field_type(is_required: bool) -> type:
    if is_required:
        return Annotated[str, pydantic.Field()]
    return Annotated[str | None, pydantic.Field()]


def get_file_field_type(is_required: bool) -> type:
    if is_required:
        return ObjectId
    return ObjectId | None


def get_checkbox_field_type(is_required: bool) -> type:
    if is_required:
        return Annotated[Literal[True], pydantic.Field()]
    return Annotated[bool, pydantic.Field()]


def get_integer_field_type(
    is_required: bool, min: int | None = None, max: int | None = None
) -> type:
    match (min is None, max is None):
        case (True, True):
            field_type = Annotated[int, pydantic.Field()]
        case (True, False):
            field_type = Annotated[int, pydantic.Field(le=max)]
        case (False, True):
            field_type = Annotated[int, pydantic.Field(ge=min)]
        case _:
            field_type = Annotated[int, pydantic.Field(ge=min, le=max)]
    if is_required:
        return field_type
    return field_type | None


def get_date_field_type(is_required: bool) -> type:
    if is_required:
        return Annotated[date, pydantic.Field()]
    return Annotated[date | None, pydantic.Field()]


# IMPORTANT: for some handlers (marked with `(*)`) additional database checks must be performed
FIELD_TO_HANDLER = {
    StringField: lambda field: get_string_field_type(field.is_required, field.max_length),
    RegexField: lambda field: get_regex_field_type(
        field.is_required, field.regex, field.max_length
    ),
    TextField: lambda field: get_string_field_type(field.is_required, field.max_length),
    EmailField: lambda field: get_regex_field_type(
        field.is_required, User.EMAIL_REGEX, field.max_length
    ),
    PhoneNumberField: lambda field: get_phone_number_field_type(field.is_required),  # (*)
    ChoiceField: lambda field: get_choice_field_type(field.is_required),  # (*)
    FileField: lambda field: get_file_field_type(field.is_required),  # (*)
    CheckBoxField: lambda field: get_checkbox_field_type(field.is_required),
    IntegerField: lambda field: get_integer_field_type(field.is_required, field.min, field.max),
    DateField: lambda field: get_date_field_type(field.is_required),
}


def create_opportunity_form_response_model(form: OpportunityForm) -> type[pydantic.BaseModel]:
    fields: dict[str, type] = {}
    for key, field in form.fields.items():
        fields[key] = FIELD_TO_HANDLER[type(field)](field)
    return pydantic.create_model(
        'ResponseModel',
        __config__=pydantic.ConfigDict(extra='ignore'),
        **fields,
    )
