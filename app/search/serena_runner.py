from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import shlex
import subprocess

from app.models import SearchResult


class SerenaError(RuntimeError):
    """Raised when Serena integration is unavailable or fails."""


_LINE_PATTERN = re.compile(r"^(?P<path>[^:\s][^:]*?)(?::(?P<line>\d+))?[:\s-]+(?P<snippet>.+)$")


@dataclass(slots=True)
class SerenaRunner:
    repo_path: Path
    command_template: str | None

    def search(self, query: str, top_k: int) -> list[SearchResult]:
        if not self.command_template:
            raise SerenaError(
                "SERENA_COMMAND_TEMPLATE is not set. Configure it to a working local Serena command."
            )

        cmd = self._build_command(query=query, top_k=top_k)
        try:
            completed = subprocess.run(
                cmd,
                cwd=self.repo_path,
                check=False,
                capture_output=True,
                text=True,
            )
        except FileNotFoundError as exc:
            raise SerenaError(
                "Serena command not found. Check SERENA_COMMAND_TEMPLATE and PATH."
            ) from exc

        if completed.returncode != 0:
            stderr = completed.stderr.strip() or "(no stderr)"
            raise SerenaError(
                "Serena command failed. Ensure Serena is running/configured for local use. "
                f"stderr: {stderr}"
            )

        return self._parse_results(completed.stdout, top_k)

    def _build_command(self, query: str, top_k: int) -> list[str]:
        template = self.command_template.format(query=query, top_k=top_k, repo_path=str(self.repo_path))
        return shlex.split(template)

    def _parse_results(self, stdout: str, top_k: int) -> list[SearchResult]:
        results: list[SearchResult] = []
        for raw_line in stdout.splitlines():
            line = raw_line.strip()
            if not line:
                continue

            match = _LINE_PATTERN.match(line)
            if match:
                file_path = match.group("path")
                line_no = int(match.group("line")) if match.group("line") else None
                snippet = match.group("snippet").strip()
            else:
                file_path = None
                line_no = None
                snippet = line

            results.append(
                SearchResult(
                    source="serena",
                    file_path=file_path,
                    line=line_no,
                    snippet=snippet,
                )
            )
            if len(results) >= top_k:
                break

        return results
