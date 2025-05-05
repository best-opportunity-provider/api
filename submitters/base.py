from typing import Any
import tempfile

from config import minio_client
from database import (
    OpportunityForm,
    OpportunityFormResponse,
    File,
)
from database.models.opportunity.form import FileField


def get_response_data(
    response: OpportunityFormResponse,
    form: OpportunityForm,
) -> tuple[dict[str, Any], tempfile.TemporaryDirectory[str]]:
    directory = tempfile.TemporaryDirectory()
    values = {}
    for name, field in form.fields.items():
        if not isinstance(field, FileField):
            values[name] = response.data[name]
            continue
        file: File | None = File.objects.with_id(response.data[name])
        assert file is not None
        values[name] = file.download_to_file(minio_client, directory.name, name)
    return values, directory
