"""
Python程序设计课程学伴Agent实验协作 Crew 的中文自定义工具。

包含 3 个工具：
- 项目文件读取工具：读取 coding-mentor-agent 项目内的源码/文档
- 知识库检索工具：检索课程知识库中的概念/练习
- 部署命令生成工具：生成一键部署脚本片段
"""

from __future__ import annotations

from pathlib import Path
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


DEFAULT_PROJECT_ROOT = Path(
    __import__("os").environ.get("TARGET_PROJECT_ROOT", "../coding-mentor-agent")
)


def _resolve_project_root(project_root: str | None) -> Path:
    """根据输入解析项目根目录，缺省时回退到环境变量或默认值。"""
    if project_root:
        return Path(project_root).expanduser().resolve()
    return DEFAULT_PROJECT_ROOT.expanduser().resolve()


class 项目文件读取输入(BaseModel):
    """项目文件读取工具的入参。"""

    文件路径: str = Field(
        ...,
        description=(
            "相对项目根目录的相对路径，例如 "
            "'src/server/main.ts' 或 'kb/python-course-kb-practical-python'"
        ),
    )
    项目根目录: str = Field(
        default="",
        description=(
            "项目根目录的绝对/相对路径；留空时使用 .env 中的 TARGET_PROJECT_ROOT"
        ),
    )


class 项目文件读取工具(BaseTool):
    """读取 coding-mentor-agent 项目内的源码、配置或文档。"""

    name: str = "project_file_reader"
    description: str = (
        "项目文件读取工具：用于读取 coding-mentor-agent 项目中的文件内容"
        "（如 src/、kb/、package.json、Dockerfile 等）。"
        "输入项目根目录（可留空）与文件相对路径，返回文件内容；大文件会被自动截断到 4000 字符。"
    )
    args_schema: Type[BaseModel] = 项目文件读取输入

    def _run(self, 文件路径: str, 项目根目录: str = "") -> str:
        root = _resolve_project_root(项目根目录 or None)
        target = (root / 文件路径).resolve()
        try:
            target.relative_to(root)
        except ValueError:
            return f"错误：禁止访问项目根目录之外的路径：{target}"

        if not target.exists():
            return f"错误：文件不存在：{target}"
        if target.is_dir():
            entries = sorted(p.name + ("/" if p.is_dir() else "") for p in target.iterdir())
            return f"目录 {target} 下的内容：\n" + "\n".join(entries)

        try:
            content = target.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return f"错误：无法以 UTF-8 解码文件：{target}"
        if len(content) > 4000:
            return content[:4000] + "\n... (内容已截断)"
        return content


class 知识库检索输入(BaseModel):
    """知识库检索工具的入参。"""

    关键词: str = Field(..., description="概念名或关键词，如 '列表'、'字符串'、'函数'")
    单元目录: str = Field(
        default="",
        description="可选的单元目录名，如 '01-入门'；留空则在 wiki/ 全局检索",
    )
    项目根目录: str = Field(default="", description="项目根目录，留空使用默认值")


class 知识库检索工具(BaseTool):
    """在课程知识库中检索指定概念或练习。"""

    name: str = "kb_search"
    description: str = (
        "知识库检索工具：在 kb/python-course-kb-practical-python/wiki/ 目录下检索指定关键词，"
        "返回匹配的概念 (.md) 或练习文件的相对路径与摘要。"
        "主要用于分析课程知识库的字段结构与知识流转路径。"
    )
    args_schema: Type[BaseModel] = 知识库检索输入

    def _run(self, 关键词: str, 单元目录: str = "", 项目根目录: str = "") -> str:
        root = _resolve_project_root(项目根目录 or None)
        kb_root = root / "kb" / "python-course-kb-practical-python" / "wiki"
        if not kb_root.exists():
            return f"错误：未找到知识库目录：{kb_root}"

        if 单元目录:
            search_dir = kb_root / 单元目录
        else:
            search_dir = kb_root
        if not search_dir.exists():
            return f"错误：单元目录不存在：{search_dir}"

        matches: list[str] = []
        for path in search_dir.rglob("*.md"):
            if 关键词.lower() in path.name.lower():
                rel = path.relative_to(root).as_posix()
                try:
                    preview = path.read_text(encoding="utf-8")[:300]
                except UnicodeDecodeError:
                    preview = "(无法以 UTF-8 预览)"
                matches.append(f"## {rel}\n{preview}\n")

        if not matches:
            return f"在 {search_dir} 中未找到包含关键词 '{关键词}' 的 .md 文件。"

        return f"检索到 {len(matches)} 个匹配项：\n\n" + "\n---\n".join(matches)


class 部署命令生成输入(BaseModel):
    """部署命令生成工具的入参。"""

    阶段: str = Field(
        ...,
        description=(
            "部署阶段标识，可选值："
            "'环境检查'、'npm安装'、'构建沙箱镜像'、'启动服务'、'一键脚本'"
        ),
    )
    使用Ollama: bool = Field(
        default=False,
        description="是否使用本地 Ollama（qwen2.5:7b）作为 AI 后端",
    )


class 部署命令生成工具(BaseTool):
    """生成部署与沙箱测试相关的命令片段。"""

    name: str = "deploy_command_generator"
    description: str = (
        "部署命令生成工具：按指定阶段输出一键部署命令片段，"
        "支持 npm 镜像加速、Docker 沙箱镜像构建、npm start 启动等。"
    )
    args_schema: Type[BaseModel] = 部署命令生成输入

    def _run(self, 阶段: str, 使用Ollama: bool = False) -> str:
        commands: dict[str, str] = {
            "环境检查": (
                "# 环境检查\n"
                "node --version\n"
                "npm --version\n"
                "docker --version\n"
                "docker info\n"
                "python --version"
            ),
            "npm安装": (
                "# 切换国内 npm 镜像\n"
                "npm config set registry https://registry.npmmirror.com\n"
                "npm install"
            ),
            "构建沙箱镜像": (
                "docker build -t coding-mentor-python-runner:0.1.0 "
                "-f sandbox-runner.Dockerfile ."
            ),
            "启动服务": (
                "Copy-Item .env.example .env\n"
                "npm start"
            ),
            "一键脚本": (
                "$env:npm_config_registry='https://registry.npmmirror.com'\n"
                "npm install\n"
                "if (!(Test-Path .env)) { Copy-Item .env.example .env }\n"
                "docker build -t coding-mentor-python-runner:0.1.0 "
                "-f sandbox-runner.Dockerfile .\n"
                "npm start"
            ),
        }

        base = commands.get(阶段)
        if not base:
            return (
                f"错误：不支持的阶段 '{阶段}'，可选值为 "
                f"{list(commands.keys())}"
            )

        if 使用Ollama and 阶段 in {"启动服务", "一键脚本"}:
            base += (
                "\n\n# 追加 .env 中的 Ollama 配置（覆盖默认 AI 配置）\n"
                "(Get-Content .env) -replace '^AI_BASE_URL=.*', "
                "'AI_BASE_URL=http://127.0.0.1:11434/v1' | Set-Content .env\n"
                "(Get-Content .env) -replace '^AI_MODEL=.*', "
                "'AI_MODEL=qwen2.5:7b' | Set-Content .env\n"
                "(Get-Content .env) -replace '^AI_API_KEY=.*', "
                "'AI_API_KEY=ollama' | Set-Content .env"
            )
        return base
