from __future__ import annotations

import argparse
import json
import sys

from app.config import ConfigError, load_config
from app.formatting import format_human
from app.models import RunOutput
from app.search.cooperative import CooperativeRunner
from app.search.mgrep_runner import MgrepError, MgrepRunner
from app.search.serena_runner import SerenaError, SerenaRunner


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Elasticsearch source exploration demo")
    parser.add_argument("--mode", choices=["mgrep", "serena", "cooperative"], required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument("--json", action="store_true", dest="json_mode")
    parser.add_argument("--top-k", type=int, default=5)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        cfg = load_config()
    except ConfigError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2

    mgrep_runner = MgrepRunner(repo_path=cfg.repo_path, command_template=cfg.mgrep_command_template)
    serena_runner = SerenaRunner(repo_path=cfg.repo_path, command_template=cfg.serena_command_template)

    try:
        output = run_mode(
            mode=args.mode,
            query=args.query,
            top_k=max(args.top_k, 1),
            repo_path=str(cfg.repo_path),
            mgrep_runner=mgrep_runner,
            serena_runner=serena_runner,
        )
    except (MgrepError, SerenaError) as exc:
        print(f"Runtime error: {exc}", file=sys.stderr)
        return 3

    if args.json_mode:
        print(json.dumps(output.to_dict(), indent=2))
    else:
        print(format_human(output))

    return 0


def run_mode(
    mode: str,
    query: str,
    top_k: int,
    repo_path: str,
    mgrep_runner: MgrepRunner,
    serena_runner: SerenaRunner,
) -> RunOutput:
    if mode == "mgrep":
        mgrep_results = mgrep_runner.search(query=query, top_k=top_k)
        return RunOutput(
            mode=mode,
            query=query,
            repo_path=repo_path,
            mgrep_results=mgrep_results,
            summary=f"mgrep returned {len(mgrep_results)} results.",
        )

    if mode == "serena":
        serena_results = serena_runner.search(query=query, top_k=top_k)
        return RunOutput(
            mode=mode,
            query=query,
            repo_path=repo_path,
            serena_results=serena_results,
            summary=f"Serena returned {len(serena_results)} results.",
        )

    coop = CooperativeRunner(mgrep_runner=mgrep_runner, serena_runner=serena_runner)
    mgrep_results, serena_results, summary = coop.search(query=query, top_k=top_k)
    return RunOutput(
        mode=mode,
        query=query,
        repo_path=repo_path,
        mgrep_results=mgrep_results,
        serena_results=serena_results,
        summary=summary,
    )


if __name__ == "__main__":
    raise SystemExit(main())
