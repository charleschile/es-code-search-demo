from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass(slots=True)
class SearchResult:
    source: str
    file_path: str | None
    line: int | None
    snippet: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(slots=True)
class RunOutput:
    mode: str
    query: str
    repo_path: str
    mgrep_results: list[SearchResult] = field(default_factory=list)
    serena_results: list[SearchResult] = field(default_factory=list)
    summary: str = ""

    def to_dict(self) -> dict:
        return {
            "mode": self.mode,
            "query": self.query,
            "repo_path": self.repo_path,
            "mgrep_results": [result.to_dict() for result in self.mgrep_results],
            "serena_results": [result.to_dict() for result in self.serena_results],
            "summary": self.summary,
        }
