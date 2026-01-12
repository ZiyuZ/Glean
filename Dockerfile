# ============================================
# Stage 1: 构建前端
# ============================================
# (locked at 2026-01-07)
# FROM oven/bun:1 AS frontend-builder
FROM oven/bun@sha256:e90cdbaf9ccdb3d4bd693aa335c3310a6004286a880f62f79b18f9b1312a8ec3 AS frontend-builder


WORKDIR /app

# 复制前端依赖文件
COPY frontend/package.json frontend/bun.lock ./

# 安装依赖
RUN bun install --frozen-lockfile

# 复制前端源代码
COPY frontend/ ./

# 构建前端
RUN bun run build

# ============================================
# Stage 2: 运行后端（包含前端静态文件）
# ============================================
# FROM ghcr.io/astral-sh/uv:python3.14-alpine AS runtime
FROM ghcr.io/astral-sh/uv@sha256:816fdce3387ed2142e37d2e56e1b1b97ccc1ea87731ba199dc8a25c04e4997c5 AS runtime

WORKDIR /app

# 安装系统依赖（用于健康检查）
RUN apk add --no-cache curl

# 复制后端依赖文件
COPY backend/pyproject.toml backend/uv.lock ./

# 安装 Python 依赖
RUN uv sync --frozen --no-dev

# 复制后端源代码
COPY backend/ ./

# 从 Stage 1 复制前端构建产物
COPY --from=frontend-builder /app/dist ./frontend/dist

# 暴露端口
EXPOSE 8000

# 设置环境变量（默认值，可通过 docker-compose 覆盖）
ENV PYTHONUNBUFFERED=1 \
    DATA_DIR=/app/data \
    APP_ENV=production

# 启动应用
CMD ["uv", "run", "fastapi", "run", "src/main.py", "--host", "0.0.0.0", "--port", "8000"]
