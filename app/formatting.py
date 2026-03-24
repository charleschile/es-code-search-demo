from __future__ import annotations

from app.models import RunOutput, SearchResult


def _format_results_block(title: str, results: list[SearchResult]) -> str:
    lines: list[str] = [title]
    if not results:
        lines.append("  (no results)")
        return "\n".join(lines)

    for i, result in enumerate(results, start=1):
        location = result.file_path or "(no file parsed)"
        if result.line is not None:
            location = f"{location}:{result.line}"
        lines.append(f"  {i}. {location}")
        lines.append(f"     {result.snippet}")
    return "\n".join(lines)


def format_human(output: RunOutput) -> str:
    chunks = [
        "=== Elasticsearch Code Search Demo ===",
        f"Mode: {output.mode}",
        f"Query: {output.query}",
        f"Repo: {output.repo_path}",
        "",
        _format_results_block("mgrep results:", output.mgrep_results),
        "",
        _format_results_block("Serena results:", output.serena_results),
        "",
        f"Summary: {output.summary}",
    ]
    return "\n".join(chunks)
