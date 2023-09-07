from datetime import datetime

from pydantic import BaseModel


class ObjSchema(BaseModel):
    class Config:
        json_encoders = {datetime: lambda v: v.strftime("%Y-%m-%dT%H:%M:%SZ")}
        arbitrary_types_allowed = True
        allow_population_by_field_name = True
        use_enum_values = True
        validate_assignment = True
        orm_mode = True
