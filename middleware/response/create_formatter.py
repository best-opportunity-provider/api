from database import OpportunityForm
import formatters as fmt
from formatters.pydantic import transformers
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


@transformers.extend_and_override(transformers.StringErrorTransformer)
@transformers.add_dummy_call
class ObjectIdErrorTransformer:
    class Errors:
        INVALID_PATTERN = fmt.TranslatedString(
            en='Field must be a valid id',
            ru='Поле должно быть валидным идентификатором',
        )


@transformers.extend_and_override(transformers.StringErrorTransformer)
@transformers.add_dummy_call
class EmailErrorTransformer:
    class Errors:
        INVALID_PATTERN = fmt.TranslatedString(
            en='Field must be a valid email',
            ru='Поле должно быть валидной электронной почтой',
        )


@transformers.extend_and_override(transformers.StringErrorTransformer)
@transformers.add_dummy_call
class PhoneNumberErrorTransformer:
    class Errors:
        INVALID_PATTERN = fmt.TranslatedString(
            en='Field must be a valid phone number',
            ru='Поле должно быть валидным номером телефона',
        )


@transformers.extend_and_override(transformers.BoolErrorTransformer)
class CheckBoxErrorTransformer:
    class Errors:
        INVALID_LITERAL = fmt.TranslatedString(
            en='Field must be true',
            ru='Поле должно быть истинным',
        )

    def __call__(self, error_code: str, *, language: fmt.Language, **kwargs) -> fmt.Error | None:
        match error_code:
            case 'invalid_literal':
                return fmt.Error(
                    type=fmt.pydantic.transformers.ErrorCode.WRONG_TYPE.value,
                    message=self.Errors.INVALID_LITERAL.get_translation(language),
                )


FIELD_TO_HANDLER = {
    StringField: lambda field: transformers.StringErrorTransformer(
        min_length=(1 if field.is_required else None), max_length=field.max_length
    ),
    RegexField: lambda field: transformers.StringErrorTransformer(
        min_lenth=(1 if field.is_required else None), max_length=field.max_length
    ),
    TextField: lambda field: transformers.StringErrorTransformer(
        min_length=(1 if field.is_required else None), max_length=field.max_length
    ),
    EmailField: lambda field: EmailErrorTransformer(
        min_length=(1 if field.is_required else None), max_length=field.max_length
    ),
    PhoneNumberField: lambda _: fmt.pydantic.appenders.DictErrorAppender(
        element_appenders={
            'country_id': ObjectIdErrorTransformer(),
            'subscriber_number': PhoneNumberErrorTransformer(),
        },
        root_transformer=transformers.DictErrorTransformer(),
    ),
    ChoiceField: lambda _: transformers.StringErrorTransformer(),
    FileField: lambda _: ObjectIdErrorTransformer(),
    CheckBoxField: lambda _: CheckBoxErrorTransformer(),
    IntegerField: lambda field: transformers.IntErrorTransformer(
        lower_bound=field.min, upper_bound=field.max
    ),
    DateField: lambda _: transformers.DateErrorTransformer(),
}


def create_opportunity_form_response_formatter(form: OpportunityForm) -> fmt.pydantic.ErrorAppender:
    return fmt.pydantic.appenders.DictErrorAppender(
        element_appenders={
            key: FIELD_TO_HANDLER[type(field)](field) for key, field in form.fields.items()
        },
        root_transformer=fmt.pydantic.transformers.RootDictErrorTransformer(min_length=1),
    )
