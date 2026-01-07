set dotenv-load := true

# 默认列出所有可用命令
default:
    @just --list

# --- 后端命令 (FastAPI + UV) ---

# 使用 ruff 自动修复代码格式
[group('backend')]
lint-be:
    cd backend && uv tool run ruff format && uv tool run ruff check --fix

# 启动开发服务器 (带热重载)
[group('backend')]
dev-be:
    cd backend && uv run fastapi dev src/main.py

# 以生产模式启动服务器
[group('backend')]
run-be:
    cd backend && uv run fastapi run src/main.py

# 安装后端依赖
[group('backend')]
install-be:
    cd backend && uv sync

# --- 前端命令 (Bun + Vite) ---

# 使用 eslint 自动修复代码格式
[group('frontend')]
lint-fe:
    cd frontend && bun run lint

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

# 前后端同时启动
[parallel]
dev: dev-be dev-fe

# 格式化前后端代码
lint: lint-be lint-fe
    
# 安装前后端依赖
install: install-be install-fe

# 提代码前的准备：格式化前后端代码并尝试构建前端
check: lint
    cd frontend && bun run build

# --- 项目管理 ---

# 统一更新前后端版本号 (支持: patch, minor, major)
# 使用示例: just bump minor
[group('project')]
bump increment='patch':
    @echo "Bumping backend version..."
    cd backend && uv version --bump {{increment}}
    @echo "Bumping frontend version..."
    cd frontend && bun pm version {{increment}}