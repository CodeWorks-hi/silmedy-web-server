from pydantic import BaseModel, field_validator
from typing  import Literal, Optional, Union

class LoginPayload(BaseModel):
    role: Literal["doctor", "admin"]
    hospital_id: Union[str, int]
    password: str
    license_number: Optional[str] = None
    department:     Optional[str] = None

    # hospital_id에 숫자가 와도 str으로 캐스팅
    @field_validator("hospital_id", mode="before")
    @classmethod
    def cast_hospital_id_to_str(cls, v):
        return str(v)