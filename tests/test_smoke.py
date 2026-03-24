from __future__ import annotations

import json
from pathlib import Path

from app.cli import build_parser, run_mode
from app.models import SearchResult


class StubMgrep:
    def search(self, query: str, top_k: int) -> list[SearchResult]:
        return [SearchResult(source="mgrep", file_path="server/src/A.java", line=12, snippet=query)][:top_k]


class StubSerena:
    def search(self, query: str, top_k: int) -> list[SearchResult]:
        return [SearchResult(source="serena", file_path="server/src/B.java", line=34, snippet=query)][:top_k]


def test_parser_modes() -> None:
    parser = build_parser()
    args = parser.parse_args(["--mode", "mgrep", "--query", "q"])
    assert args.mode == "mgrep"
    assert args.query == "q"


def test_run_mode_mgrep() -> None:
    output = run_mode(
        mode="mgrep",
        query="Where are thread pools defined?",
        top_k=5,
        repo_path="/tmp/repo",
        mgrep_runner=StubMgrep(),
        serena_runner=StubSerena(),
    )
    assert output.mgrep_results
    assert output.serena_results == []


def test_run_mode_cooperative_json_shape() -> None:
    output = run_mode(
        mode="cooperative",
        query="Where is the request circuit breaker implemented?",
        top_k=5,
        repo_path=str(Path("/tmp/repo")),
        mgrep_runner=StubMgrep(),
        serena_runner=StubSerena(),
    )
    data = output.to_dict()
    payload = json.dumps(data)
    assert '"mode": "cooperative"' in payload
    assert data["mgrep_results"]
    assert data["serena_results"]
