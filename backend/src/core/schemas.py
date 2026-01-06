from pydantic import BaseModel


class MessageResponse(BaseModel):
    message: str


class ChapterMetadata(BaseModel):
    id: int | None
    book_id: int
    title: str
    order_index: int
    # content is excluded intentionally
