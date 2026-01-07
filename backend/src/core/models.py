from sqlmodel import Field, Relationship, SQLModel

__version__ = 'v1'


class Book(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hash_id: str = Field(index=True, unique=True)  # 文件内容哈希
    title: str
    path: str  # 相对于 books_dir 的路径
    is_starred: bool = Field(default=False)
    last_read_time: float | None = None

    # 文件元数据（用于增量扫描）
    file_size: int  # 文件大小（字节）
    file_mtime: float  # 文件最后修改时间（Unix 时间戳）

    # 阅读进度
    chapter_index: int | None = None  # 当前阅读的章节索引（对应 Chapter.order_index）
    chapter_offset: int | None = None  # 在章节内的字符偏移量（用于恢复阅读位置）
    is_finished: bool = Field(default=False)  # 是否已读完

    # 关联章节（一对多）
    chapters: list['Chapter'] = Relationship(back_populates='book')


class Chapter(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    book_id: int = Field(foreign_key='book.id')
    title: str
    order_index: int  # 章节序号
    content: str  # 章节内容（UTF-8 编码的文本，不包含章节标题，已清洗）

    book: Book = Relationship(back_populates='chapters')
