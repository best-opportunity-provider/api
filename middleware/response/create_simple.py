from database import (
    OpportunityForm,
    OpportunityFormResponse,
    User,
    UserInfo,
)


def create_opportunity_form_response(
    form: OpportunityForm,
    user: User,
) -> OpportunityFormResponse:
    user_info: UserInfo | None = UserInfo.objects.with_id(user.id)
    assert user_info is not None
    data = {}
    for name, field in form.fields.items():
        fill = field.fill_input(user, user_info)
        assert fill[0]
        data[name] = fill[1]
    response = OpportunityFormResponse.create(user, form, data)
    assert isinstance(response, OpportunityFormResponse)
    return response
