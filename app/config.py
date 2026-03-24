from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


class ConfigError(RuntimeError):
    """Raised when required runtime configuration is invalid."""


@dataclass(slots=True)
class AppConfig:
    repo_path: Path
    mgrep_command_template: str
    serena_command_template: str | None


def _looks_like_git_repo(path: Path) -> bool:
    return (path / ".git").exists() or (path / ".git" / "config").exists()


def load_config() -> AppConfig:
    repo = os.environ.get("ELASTICSEARCH_REPO_PATH")
    if not repo:
        raise ConfigError(
            "ELASTICSEARCH_REPO_PATH is not set. Export it to your elastic/elasticsearch clone path."
        )

    repo_path = Path(repo).expanduser().resolve()
    if not repo_path.exists() or not repo_path.is_dir():
        raise ConfigError(f"ELASTICSEARCH_REPO_PATH does not exist or is not a directory: {repo_path}")
    if not _looks_like_git_repo(repo_path):
        raise ConfigError(f"Path does not look like a git repo (missing .git): {repo_path}")

    return AppConfig(
        repo_path=repo_path,
        mgrep_command_template=os.environ.get("MGREP_COMMAND_TEMPLATE", 'mgrep "{query}"'),
        serena_command_template=os.environ.get("SERENA_COMMAND_TEMPLATE"),
    )
