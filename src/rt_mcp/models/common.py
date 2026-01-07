"""Common Pydantic models for RT REST2 API."""

from pydantic import BaseModel, Field


class Hyperlink(BaseModel):
    """RT hypermedia link following HATEOAS principles."""

    ref: str = Field(..., description="Link relationship")
    type: str = Field(..., description="Media type")
    _url: str = Field(..., description="URL endpoint")


class PaginatedResponse(BaseModel):
    """Standard RT pagination response structure."""

    count: int = Field(..., description="Number of items in current page")
    page: int = Field(..., description="Current page number")
    pages: int = Field(..., description="Total number of pages")
    per_page: int = Field(..., description="Items per page")
    total: int = Field(..., description="Total number of items")
    items: list[dict] = Field(default_factory=list, description="Items on current page")


class RTObject(BaseModel):
    """Base model for RT objects with common fields."""

    id: int | str = Field(..., description="Object ID")
    type: str = Field(..., description="Object type")
    _hyperlinks: list[Hyperlink] = Field(
        default_factory=list, description="Related resource links"
    )


class CustomField(BaseModel):
    """Custom field value in RT."""

    name: str = Field(..., description="Custom field name")
    values: list[str] | str | None = Field(
        None, description="Custom field value(s)"
    )
