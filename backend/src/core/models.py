from sqlmodel import Field, Relationship, SQLModel

__version__ = 'v4'


class Meta(SQLModel, table=True):
    __tablename__ = '__meta'

    key: str = Field(primary_key=True)
    value: str


class Book(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hash_id: str = Field(index=True)  # 文件内容哈希（不做唯一约束）
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
    order_index: int  # 阅读顺序章节编号，从 0 起连续（与解析器内部行键无关）
    body: str  # 解析入库的正文（批量替换规则请用外部工具如 retree 预处理）

    book: Book = Relationship(back_populates='chapters')
