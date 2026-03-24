# Elasticsearch Code Search CLI Demo (mgrep + Serena)

## What this demo does

This is a small terminal-only Python project for exploring a local `elastic/elasticsearch` source tree in three modes:

1. **mgrep-only** (broad semantic recall from natural language)
2. **Serena-only** (symbol/source-oriented inspection)
3. **cooperative** (mgrep first, Serena second)

No frontend, no database, and no Docker are used.

## Short implementation plan (v1)

1. Implement config + validation for `ELASTICSEARCH_REPO_PATH`.
2. Implement mgrep integration first via subprocess.
3. Implement Serena integration as a thin, explicit subprocess adapter.
4. Implement cooperative mode as a simple two-step pipeline:
   - mgrep broad recall
   - Serena refinement with candidate file context
5. Add JSON/human output formatting, helper scripts, and smoke tests.

## Serena integration assumptions

To avoid fabricating Serena APIs, this demo **does not hardcode Serena subcommands**.

Instead, it requires:

- `SERENA_COMMAND_TEMPLATE` environment variable pointing to your working local Serena command.
- The template can use these placeholders:
  - `{query}`
  - `{top_k}`
  - `{repo_path}`

Example (replace with your real local Serena invocation):

```bash
export SERENA_COMMAND_TEMPLATE='serena your-real-subcommand --repo "{repo_path}" --query "{query}" --top-k {top_k}'
```

If Serena is not configured, Serena/cooperative modes fail with actionable error messages while mgrep mode still works.

## What each mode demonstrates

- **mgrep mode**: natural language to file/snippet candidates.
- **Serena mode**: local Serena-driven source/symbol findings.
- **cooperative mode**: mgrep candidate files are passed as context into Serena for focused refinement.

## Prerequisites (macOS)

- macOS terminal (zsh/bash)
- Python 3.11+
- `uv`
- Local clone of `elastic/elasticsearch`
- `mgrep` installed + authenticated
- Mixedbread credentials configured for mgrep as needed
- Local Serena setup available (command template configured)

## Set `ELASTICSEARCH_REPO_PATH`

```bash
export ELASTICSEARCH_REPO_PATH="$HOME/src/elasticsearch"
```

## Verify mgrep is available

```bash
command -v mgrep
mgrep --help || true
```

## Run `mgrep watch` (if needed)

If your repo is not indexed yet, run this from your Elasticsearch repo:

```bash
cd "$ELASTICSEARCH_REPO_PATH"
mgrep watch
```

## Configure/start Serena locally

Because Serena setups vary, this demo uses `SERENA_COMMAND_TEMPLATE`.

1. Start/configure Serena as required by your local environment.
2. Export a working command template:

```bash
export SERENA_COMMAND_TEMPLATE='YOUR_WORKING_SERENA_COMMAND_WITH_{query}_{top_k}_{repo_path}'
```

3. Test manually once before using the CLI.

## Install and run

### Environment check

```bash
./scripts/check_env.sh
```

### mgrep mode

```bash
python -m app.cli --mode mgrep --query "Where are thread pools defined?"
```

### Serena mode

```bash
python -m app.cli --mode serena --query "Where is the request circuit breaker implemented?"
```

### Cooperative mode

```bash
python -m app.cli --mode cooperative --query "Where does Elasticsearch reject execution when pools are saturated?"
```

### Additional sample query

```bash
python -m app.cli --mode cooperative --query "What files and symbols are related to shard allocation deciders?"
```

## JSON mode usage

```bash
python -m app.cli --mode cooperative --query "Where are thread pools defined?" --json --top-k 8
```

JSON shape:

```json
{
  "mode": "...",
  "query": "...",
  "repo_path": "...",
  "mgrep_results": [],
  "serena_results": [],
  "summary": "..."
}
```

## Troubleshooting

### 1) Missing repo path

Error mentions `ELASTICSEARCH_REPO_PATH is not set`.

Fix:

```bash
export ELASTICSEARCH_REPO_PATH="/absolute/path/to/elasticsearch"
```

### 2) mgrep not found

Error mentions command not found.

Fix:

- Install mgrep and ensure it is on `PATH`.
- Re-open shell or update shell profile.

### 3) mgrep not authenticated / not indexed

Error indicates mgrep command failed.

Fix:

- Verify auth/login for your mgrep setup.
- Run `mgrep watch` inside `ELASTICSEARCH_REPO_PATH`.

### 4) Serena not running / not configured

Error mentions `SERENA_COMMAND_TEMPLATE` missing or command failure.

Fix:

- Start/configure Serena per your local install.
- Set `SERENA_COMMAND_TEMPLATE` to a known-good invocation.

### 5) Serena integration limitations

This v1 intentionally keeps Serena integration as a thin adapter for portability.

- Output parsing is line-oriented and best-effort.
- Different Serena output formats may need a small parser tweak in `app/search/serena_runner.py`.

## Known limitations

- CLI output parsing for mgrep/Serena is generic and may not perfectly capture all output formats.
- Serena mode depends on user-provided command template due to local setup variability.
- Cooperative mode is intentionally simple (single mgrep pass + single Serena pass).

## Project layout

```text
pyproject.toml
README.md
app/
  __init__.py
  cli.py
  config.py
  models.py
  formatting.py
  search/
    __init__.py
    mgrep_runner.py
    serena_runner.py
    cooperative.py
scripts/
  run_demo.sh
  check_env.sh
tests/
  test_smoke.py
```
