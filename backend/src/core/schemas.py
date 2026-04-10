from pydantic import BaseModel, Field


class MessageResponse(BaseModel):
    message: str


# Books
class UpdateProgressRequest(BaseModel):
    chapter_index: int
    chapter_offset: int


class ToggleStarRequest(BaseModel):
    starred: bool


class MarkFinishedRequest(BaseModel):
    finished: bool


class BatchDeleteBooksRequest(BaseModel):
    book_ids: list[int]
    physical: bool = True


class BatchDeleteBooksResponse(BaseModel):
    message: str
    success_count: int
    failed_count: int
    failed_book_ids: list[int] = Field(default_factory=list)


# Chapters
class ChapterMetadata(BaseModel):
    id: int | None
    book_id: int
    title: str
    order_index: int
    # content is excluded intentionally


# Scan
class ScanResponse(BaseModel):
    message: str
    files_scanned: int = 0
    files_added: int = 0
    files_updated: int = 0
