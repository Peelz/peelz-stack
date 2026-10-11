# peelz-stack

Own fork of [pstack](https://github.com/cursor/plugins/tree/main/pstack)
(Cursor's agent skill suite: poteto-mode, arena, swarm, interrogate, why, how,
reflect, no-comments, architect, and the principle-* library).

## Why this fork exists

Upstream is Cursor-only. This fork bakes in multi-harness support so the skills
run unchanged in Pi (with the pi-subagents extension), Claude Code, OpenCode,
and Codex — and so `npx skills add` updates can never clobber the patches.

## The peelz delta (commit 2)

- **Settings file convention.** Cursor keeps `~/.cursor/rules/pstack-models.mdc`;
  every other harness reads `~/.agents/pstack-models.md`. All skills that pick a
  per-role model now resolve both paths.
- **Subagent-tool mappings.** Every skill that spawns subagents maps Cursor's
  `Task` to the harness's own tool, including Pi's `subagent`
  (one child per `{agent, task}` call; parallel fan-out via one workflow script
  with `runs.run`/`runs.all`; per-child `model`; `worktree: true`).
- **poteto-mode Harness section.** Ported harness mapping: subagents,
  `poteto-agent` fallback, transcript locations per harness, skill folders.
- **Agent fallbacks.** Where Cursor registers `poteto-agent` / `Comment Sicko`
  as subagent types, other harnesses spawn a general subagent whose prompt
  starts with "Read `agents/poteto-agent.md` (or `agents/comment-sicko.md`) in
  full before any work."
- `tools/peelz-patch.py` — the full patch table. Idempotent; re-run after
  merging upstream changes: `python3 tools/peelz-patch.py`

## Syncing upstream

```bash
git remote add upstream https://github.com/cursor/plugins.git
# sparse-fetch just pstack/ and merge, then:
python3 tools/peelz-patch.py   # re-apply the delta on any new wording
```

## Live wiring (Pi)

`~/.pi/agent/skills/<name>` symlinks point into `skills/<name>` here, so Pi
loads this fork directly. Model choices live outside the repo at
`~/.agents/pstack-models.md` (see `skills/setup-pstack`).
