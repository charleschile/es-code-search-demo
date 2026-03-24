from __future__ import annotations

from dataclasses import dataclass

from app.models import SearchResult
from app.search.mgrep_runner import MgrepRunner
from app.search.serena_runner import SerenaRunner


@dataclass(slots=True)
class CooperativeRunner:
    mgrep_runner: MgrepRunner
    serena_runner: SerenaRunner

    def search(self, query: str, top_k: int) -> tuple[list[SearchResult], list[SearchResult], str]:
        mgrep_results = self.mgrep_runner.search(query=query, top_k=top_k)

        candidate_files = [r.file_path for r in mgrep_results if r.file_path][: max(1, min(5, top_k))]
        candidate_context = "\n".join(f"- {path}" for path in candidate_files)
        serena_query = (
            f"Question: {query}\n"
            "Candidate files from mgrep:\n"
            f"{candidate_context if candidate_context else '- (none extracted)'}\n"
            "Focus on symbols, references, and where logic is implemented."
        )

        serena_results = self.serena_runner.search(query=serena_query, top_k=top_k)
        summary = self._build_summary(query, mgrep_results, serena_results)
        return mgrep_results, serena_results, summary

    @staticmethod
    def _build_summary(
        query: str,
        mgrep_results: list[SearchResult],
        serena_results: list[SearchResult],
    ) -> str:
        m_paths = [r.file_path for r in mgrep_results if r.file_path]
        s_paths = [r.file_path for r in serena_results if r.file_path]
        return (
            f"For '{query}', mgrep provided {len(mgrep_results)} broad candidates "
            f"({len(set(m_paths))} files), then Serena provided {len(serena_results)} "
            f"deeper symbol-oriented findings ({len(set(s_paths))} files)."
        )
