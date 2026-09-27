from pydantic import BaseModel, ConfigDict


class RouteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    start_location: str
    end_location: str
