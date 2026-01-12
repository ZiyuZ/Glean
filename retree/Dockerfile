# Retree - 书库文件相似度分析工具

FROM python:3.14-slim

LABEL maintainer="Retree" \
      description="书库文件相似度分析工具"

WORKDIR /app

# 复制依赖文件
COPY pyproject.toml .

# 安装 Python 依赖（CPU 版本 torch）
RUN pip install --no-cache-dir \
    torch==2.9.1 --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir \
    chardet>=5.2.0 \
    httpx>=0.28.1 \
    numpy>=2.0.0 \
    opencc-python-reimplemented>=0.1.7 \
    rich>=13.0.0 \
    sentence-transformers>=3.0.0 \
    typer>=0.12.0

# 复制应用代码
COPY app/ ./

# 设置环境变量
ENV RETREE_BOOKS_ROOT=/data/books \
    RETREE_DATA_ROOT=/data/retree \
    HF_HOME=/data/models \
    PYTHONUNBUFFERED=1

# 数据卷挂载点
VOLUME ["/data/books", "/data/retree", "/data/models"]

# 入口点
ENTRYPOINT ["python", "main.py"]

# 默认命令（显示帮助）
CMD ["--help"]
