"""标题标准化插件 - 基于 LLM"""

import json
import re

import httpx
from config import LLM_MODEL, LLM_TIMEOUT, OLLAMA_URL, TITLE_PROMPT_TEMPLATE
from rich.progress import Progress
from scanner import MetadataManager


class TitleStandardizer:
    """基于 LLM 的标题标准化工具"""

    def __init__(
        self,
        ollama_url: str = OLLAMA_URL,
        model: str = LLM_MODEL,
        timeout: int = LLM_TIMEOUT,
    ):
        self.ollama_url = ollama_url
        self.model = model
        self.client = httpx.Client(timeout=timeout)

    def _make_prompt(self, filename: str) -> str:
        return TITLE_PROMPT_TEMPLATE.replace('{{filename}}', filename)

    def _parse_response(self, response_text: str) -> str | None:
        """解析 LLM 返回的 JSON"""
        # 尝试直接解析
        try:
            data = json.loads(response_text)
            return data.get('standardized', '').strip()
        except json.JSONDecodeError:
            pass

        # 尝试提取 JSON 块
        match = re.search(r'\{[^}]+\}', response_text)
        if match:
            try:
                data = json.loads(match.group())
                return data.get('standardized', '').strip()
            except json.JSONDecodeError:
                pass

        return None

    def standardize(self, filename: str) -> str | None:
        """标准化单个文件名"""
        prompt = self._make_prompt(filename)
        payload = {'model': self.model, 'prompt': prompt, 'stream': False}

        try:
            resp = self.client.post(self.ollama_url, json=payload)
            resp.raise_for_status()
            response_text = resp.json().get('response', '')
            return self._parse_response(response_text)
        except Exception as e:
            print(f'[错误] 处理 "{filename}" 失败: {e}')
            return None

    def run(self, manager: MetadataManager, overwrite: bool = False) -> int:
        """批量标准化，更新元信息

        Args:
            manager: 元信息管理器（需要先 load）
            overwrite: 是否覆盖已有的标准化标题

        Returns:
            成功处理的数量
        """
        paths = manager.list_paths()
        success_count = 0

        with Progress() as progress:
            task = progress.add_task('[green]标准化标题...', total=len(paths))

            for rel_path in paths:
                meta = manager.get(rel_path)
                if meta is None:
                    progress.advance(task)
                    continue

                # 跳过已处理的
                if meta.standardized_title and not overwrite:
                    progress.advance(task)
                    continue

                progress.update(task, description=f'[green]{meta.title[:20]}...')

                result = self.standardize(meta.title)
                if result:
                    manager.update(rel_path, standardized_title=result)
                    success_count += 1

                progress.advance(task)

        print(f'标准化完成，成功处理 {success_count}/{len(paths)} 个文件')
        return success_count


if __name__ == '__main__':
    # 1. 加载元信息
    manager = MetadataManager()
    metadata = manager.load()

    if not metadata:
        print('请先运行 scanner.py 扫描文件')
        exit(1)

    # 2. 运行标题标准化
    standardizer = TitleStandardizer()
    standardizer.run(manager)

    # 3. 保存更新后的元信息
    manager.save()
