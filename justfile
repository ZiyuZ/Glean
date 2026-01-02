set dotenv-load := true

# 默认列出所有可用命令
default:
    @just --list

# --- 后端命令 (FastAPI + UV) ---

# 使用 ruff 自动修复代码格式
[group('backend')]
lint:
    cd backend && uv tool run ruff format && uv tool run ruff check --fix

# 启动开发服务器 (带热重载)
[group('backend')]
dev-be:
    cd backend && uv run fastapi dev main.py

# 以生产模式启动服务器
[group('backend')]
run-be:
    cd backend && uv run fastapi run main.py

# 安装后端依赖
[group('backend')]
install-be:
    cd backend && uv sync

# --- 前端命令 (Bun + Vite) ---

# 启动前端开发环境
[group('frontend')]
dev-fe:
    cd frontend && bun run dev

# 构建前端生产版本
[group('frontend')]
build-fe:
    cd frontend && bun run build

# 预览构建后的前端
[group('frontend')]
preview-fe:
    cd frontend && bun run preview

# 安装前端依赖
[group('frontend')]
install-fe:
    cd frontend && bun install

# --- 组合命令 ---

# 一键启动开发全家桶 (前后端同时启动)
dev:
    @echo "🚀 启动 FastAPI (dev模式) 和 Vite..."
    just -j 2 dev-be dev-fe

# 一键安装所有依赖
install: install-be install-fe

# 提代码前的准备：格式化后端代码并尝试构建前端
check: lint
    cd frontend && bun run build