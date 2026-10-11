#!/usr/bin/env python3
"""peelz-stack fork patch: multi-harness + pi-subagents support.

Base: cursor/plugins pstack (Cursor-only wording).
This script bakes in:
  1. The pstack settings file convention (~/.cursor/rules/pstack-models.mdc in
     Cursor, ~/.agents/pstack-models.md in every other harness).
  2. Subagent-tool mappings for Claude Code / OpenCode / Codex / Pi, including
     Pi's `subagent` tool from the pi-subagents extension (one child per
     {agent, task} call; parallel fan-out via one workflow script with
     runs.run / runs.all; `model` option per child; `worktree: true`).

Idempotent: a patch whose target text is already applied is skipped.
Run from the repo root:  python3 tools/peelz-patch.py
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SETTINGS = (
    "the pstack settings file (`~/.cursor/rules/pstack-models.mdc` in Cursor, "
    "`~/.agents/pstack-models.md` in other harnesses)"
)

SUBAGENT_TOOLS = (
    "`Agent` in Claude Code (`subagent_type: general-purpose`), "
    "`task` in OpenCode (`subagent_type: general`), "
    "`spawn_agent` in Codex, "
    "`subagent` in Pi with the pi-subagents extension"
)

def harness_para(role, spawn_hint, fallback_role="role"):
    return (
        f"\n\n**Other harnesses.** `Task` means your subagent tool: {SUBAGENT_TOOLS} "
        f"({role} per `{{agent, task}}` call, `model` option set per the role line; "
        f"{spawn_hint} via one workflow script that fans out via `runs.all`). "
        "Keep the prompt and the model. Drop parameters your tool doesn't have. "
        f"If your harness has no subagent tool, run each {fallback_role} yourself, one after another."
    )

REVIEWER = harness_para("one reviewer", "spawn all reviewers", "reviewer")
INVESTIGATOR = harness_para("one investigator", "spawn all investigators", "investigator")

SWARM_HARNESS = (
    "\n\n**Other harnesses.** These parameters belong to Cursor's `Task` tool, and "
    '`environment: "cloud"` runs a Cursor cloud agent. In another harness, use its '
    f"subagent tool: {SUBAGENT_TOOLS} (one worker per `{{agent, task}}` call with the "
    "step 4 model; spawn all workers in parallel with one workflow script that fans "
    "out via `runs.all`; `worktree: true` gives each worker its own worktree). Workers "
    "run locally there, so give each one its own worktree or output path. Keep the "
    "brief and the model. Drop parameters your tool doesn't have. If your harness has "
    "no subagent tool, run the workers yourself, one after another."
)

# (file, old, new) — exact substring replacements, applied in order.
PATCHES = [
    # ── architect ──────────────────────────────────────────────────────────
    ("skills/architect/SKILL.md",
     "Take the runners from the `architect runners` line in the `pstack-models.mdc` rule, in place of the `arena runners` line. If the rule or that line is missing,",
     f"Take the runners from the `architect runners` line in {SETTINGS}, in place of the `arena runners` line. If the file or that line is missing,"),

    # ── arena ──────────────────────────────────────────────────────────────
    ("skills/arena/SKILL.md",
     "Use the `arena runners` line in `~/.cursor/rules/pstack-models.mdc`. If the rule or that line is missing, default to one each on",
     f"Use the `arena runners` line in {SETTINGS}. If the file or that line is missing, default to one each on"),
    ("skills/arena/SKILL.md",
     "If the Task tool rejects a configured entry, run that seat on its family's default and say so.",
     "If your subagent tool rejects a configured entry, run that seat on its family's default and say so."),
    ("skills/arena/SKILL.md",
     "choose one model from the `arena cross-judge pool` line in `~/.cursor/rules/pstack-models.mdc`. If the rule or that line is missing, choose from",
     f"choose one model from the `arena cross-judge pool` line in {SETTINGS}. If the file or that line is missing, choose from"),
    ("skills/arena/SKILL.md",
     "instructions to produce the artifact and a short rationale naming the alternatives it considered and what it rejected.",
     "instructions to produce the artifact and a short rationale naming the alternatives it considered and what it rejected."
     "\n\n**Other harnesses.** `run_in_background: true` means your harness's async spawn. In Pi with the "
     "pi-subagents extension, launch all candidates in one workflow script that fans out via `runs.all`, "
     "each candidate on its own `{agent, task}` call with its own output path. Keep the brief and the "
     "model. Drop parameters your tool doesn't have."),

    # ── how ────────────────────────────────────────────────────────────────
    ("skills/how/SKILL.md",
     "Every spawn is a Task subagent with `subagent_type: generalPurpose` and `readonly: true`. Explorers use the `how explorer` line in the `pstack-models.mdc` rule (default `grok-4.7-xhigh-fast`), and every explainer uses the `how explainer` line (default `claude-opus-5-5-xhigh`). Set `model` to that line's value, or to the default if the rule or the line is missing. Leave `model` unset when the value is `auto` or `inherit-parent`. If the Task tool rejects a slug, use the default and say so. If it rejects the default, use the closest valid slug of the same family from its error message.",
     "Every spawn is a subagent with `subagent_type: generalPurpose` and `readonly: true`. Explorers use "
     f"the `how explorer` line in {SETTINGS} (default `grok-4.7-xhigh-fast`), and every explainer uses "
     "the `how explainer` line (default `claude-opus-5-5-xhigh`). Set `model` to that line's value, or to "
     "the default if the file or the line is missing. Leave `model` unset when the value is `auto` or "
     "`inherit-parent`. If your subagent tool rejects a slug, use the default and say so. If it rejects "
     "the default, use the closest valid slug of the same family from its error message."
     "\n\n**Other harnesses.** `Task` means your subagent tool: " + SUBAGENT_TOOLS +
     " (one role per `{agent, task}` call, `model` option set per the role line; run the explorers in "
     "parallel via one workflow script that fans out via `runs.all`). Keep the prompt and the model. "
     "Drop parameters your tool doesn't have. If your harness has no subagent tool, run each role "
     "yourself, one after another."),

    # ── interrogate ────────────────────────────────────────────────────────
    ("skills/interrogate/SKILL.md",
     "Launch all reviewers in a single message with the Task tool, one per entry on the `interrogate reviewers` line in `~/.cursor/rules/pstack-models.mdc`, labeled Reviewer A, B, and so on to match the entry count. If the rule or that line is missing, use the table defaults.",
     "Launch all reviewers in a single message with your subagent tool, one per entry on the "
     f"`interrogate reviewers` line in {SETTINGS}, labeled Reviewer A, B, and so on to match the entry "
     "count. If the file or that line is missing, use the table defaults."),
    ("skills/interrogate/SKILL.md",
     "Omit `model` for an `auto` or `inherit-parent` entry, so that reviewer runs on the parent model.",
     "Omit `model` for an `auto` or `inherit-parent` entry, so that reviewer runs on the parent model."
     + REVIEWER),
    ("skills/interrogate/SKILL.md",
     "If the Task tool rejects a configured entry, run that reviewer on its family's table default and say so.",
     "If your subagent tool rejects a configured entry, run that reviewer on its family's table default and say so."),

    # ── poteto-help ────────────────────────────────────────────────────────
    ("skills/poteto-help/SKILL.md",
     "- No `~/.cursor/rules/pstack-models.mdc` means `/setup-pstack` hasn't run for this user, so every role uses its default model.",
     f"- No {SETTINGS} means `/setup-pstack` hasn't run for this user, so every role uses its default model."),
    ("skills/poteto-help/SKILL.md",
     'To get the same style from a subagent of your own, spawn it with `subagent_type: "poteto-agent"`.',
     'To get the same style from a subagent of your own, spawn it with `subagent_type: "poteto-agent"`. '
     "Where `poteto-agent` isn't registered as a subagent type, spawn a general subagent whose prompt "
     'starts with: "Read `agents/poteto-agent.md` in full before any work." Then give the task.'),

    # ── reflect ────────────────────────────────────────────────────────────
    ("skills/reflect/SKILL.md",
     "One message, three `Task` calls, `subagent_type: generalPurpose`, agent mode (`readonly: false`). Reviewers need MCP access to look up the tickets, chat threads, and observability traces the transcript references, and readonly strips MCPs.",
     "One message, three subagent calls, `subagent_type: generalPurpose`, agent mode (`readonly: false`). "
     "Reviewers need MCP access to look up the tickets, chat threads, and observability traces the "
     "transcript references, and readonly strips MCPs." + REVIEWER),
    ("skills/reflect/SKILL.md",
     "Each reviewer and the synthesizer name a role line in the `pstack-models.mdc` rule and a default. Set `model` to that line's value, or to the default if the rule or the line is missing. Leave `model` unset when the value is `auto` or `inherit-parent`. If the Task tool rejects a slug, use the default and say so. If it rejects the default, use the closest valid slug of the same family from its error message.",
     "Each reviewer and the synthesizer name a role line in " + SETTINGS + " and a default. Set `model` to "
     "that line's value, or to the default if the file or the line is missing. Leave `model` unset when "
     "the value is `auto` or `inherit-parent`. If your subagent tool rejects a slug, use the default and "
     "say so. If it rejects the default, use the closest valid slug of the same family from its error message."),
    ("skills/reflect/SKILL.md",
     "One `Task` call, `subagent_type: generalPurpose`,",
     "One subagent call, `subagent_type: generalPurpose`,"),

    # ── setup-pstack ───────────────────────────────────────────────────────
    ("skills/setup-pstack/SKILL.md",
     "Write `~/.cursor/rules/pstack-models.mdc`, an always-applied rule that sets pstack's model per role.",
     "Write pstack's model settings. **Cursor:** `~/.cursor/rules/pstack-models.mdc`, an always-applied "
     "rule. **Every other harness** (Claude Code, Codex, Pi, OpenCode, and others): "
     "`~/.agents/pstack-models.md`. These harnesses don't load Cursor rules, so pstack skills read this "
     "file when they pick a model."),
    ("skills/setup-pstack/SKILL.md",
     "Enumerate the model slugs you can pass to a `Task` subagent in this session. That is the dependable source. If Cursor also exposes a models API or CLI that lists the user's entitled models, prefer it for completeness.",
     "Enumerate the model slugs you can pass to a subagent in this session (Cursor `Task`, Claude Code "
     "`Agent`, OpenCode `task`, Codex `spawn_agent`, Pi `subagent` from the pi-subagents extension). That "
     "is the dependable source. If your harness also has a command that lists the user's models, prefer "
     "it for completeness (for example `opencode models` or `pi --list-models`)."),
    ("skills/setup-pstack/SKILL.md",
     "If `~/.cursor/rules/pstack-models.mdc` already exists, read it",
     "If the settings file already exists (check both `~/.cursor/rules/pstack-models.mdc` and "
     "`~/.agents/pstack-models.md`; use the one that exists), read it"),
    ("skills/setup-pstack/SKILL.md",
     "Write `~/.cursor/rules/pstack-models.mdc` with `alwaysApply: true`, a `# budget` line with the chosen label and its target effort,",
     "Write the settings file — in Cursor, `~/.cursor/rules/pstack-models.mdc` with `alwaysApply: true`; "
     "elsewhere, `~/.agents/pstack-models.md` without the frontmatter — with a `# budget` line with the "
     "chosen label and its target effort,"),
    ("skills/setup-pstack/SKILL.md",
     "omit Task `model`",
     "omit the subagent `model`"),

    # ── swarm ──────────────────────────────────────────────────────────────
    ("skills/swarm/SKILL.md",
     "Pick the worker model from the `swarm workers` line in `~/.cursor/rules/pstack-models.mdc`. If the rule or that line is missing, use `grok-4.7-xhigh-fast`. For `auto` or `inherit-parent`, omit `model` so the workers run on the parent model. If the Task tool rejects a slug, use the default and say so.",
     "Pick the worker model from the `swarm workers` line in " + SETTINGS + ". If the file or that line "
     "is missing, use `grok-4.7-xhigh-fast`. For `auto` or `inherit-parent`, omit `model` so the workers "
     "run on the parent model. If your subagent tool rejects a slug, use the default and say so."),
    ("skills/swarm/SKILL.md",
     'Use `environment: "local"` only when the worker needs access to something on the user\'s computer.',
     'Use `environment: "local"` only when the worker needs access to something on the user\'s computer.'
     + SWARM_HARNESS),

    # ── why ────────────────────────────────────────────────────────────────
    ("skills/why/SKILL.md",
     "Each spawn below names a role line in the `pstack-models.mdc` rule and a default. Set `model` to that line's value, or to the default if the rule or the line is missing. Leave `model` unset when the value is `auto` or `inherit-parent`. If the Task tool rejects a slug, use the default and say so. If it rejects the default, use the closest valid slug of the same family from its error message.",
     "Each spawn below names a role line in " + SETTINGS + " and a default. Set `model` to that line's "
     "value, or to the default if the file or the line is missing. Leave `model` unset when the value is "
     "`auto` or `inherit-parent`. If your subagent tool rejects a slug, use the default and say so. If it "
     "rejects the default, use the closest valid slug of the same family from its error message."),
    ("skills/why/SKILL.md",
     "Before spawning investigators, list the available MCPs from the Cursor environment. Use the available-tools map when present. Otherwise inspect the `mcps/` directory Cursor exposes for enabled MCP servers.",
     "Before spawning investigators, list the MCP servers connected to your harness. In Cursor, use the "
     "available-tools map when present, or inspect the `mcps/` directory it exposes. In other harnesses, "
     "MCP tools usually appear in your tool list with the server name in the tool name (for example "
     "`mcp__<server>__<tool>`)."),
    ("skills/why/SKILL.md",
     "Spawn one investigator per category that has a matching MCP, all in a single message so they run concurrently, each owning exactly one tool or MCP. Don't ask one agent to cover multiple MCPs. `model`: the `why investigators` line, default `grok-4.7-xhigh-fast`.",
     "Spawn one investigator per category that has a matching MCP, all in a single message so they run "
     "concurrently, each owning exactly one tool or MCP. Don't ask one agent to cover multiple MCPs. "
     "`model`: the `why investigators` line, default `grok-4.7-xhigh-fast`." + INVESTIGATOR),

    # ── no-comments ────────────────────────────────────────────────────────
    ("skills/no-comments/SKILL.md",
     '1. Spawn `Task` with `subagent_type: "Comment Sicko"`. Pass the scope. Do not restate its rules.',
     '1. Spawn `Task` with `subagent_type: "Comment Sicko"`. Pass the scope. Do not restate its rules. '
     "Outside Cursor with the pstack plugin, spawn a general subagent instead and start its prompt with: "
     '"Read `agents/comment-sicko.md` in full before any work." Then pass the scope. If your harness has '
     "no subagent tool, run that prompt yourself in a fresh pass over the scope."),

    # ── poteto-mode: Harness section (ported, adapted to this repo) ───────
    ("skills/poteto-mode/SKILL.md",
     "- **Worktree and simulator cleanup.** Reclaim local disk by pruning merged or abandoned git worktrees and stale iOS simulators",
     "- **Worktree and simulator cleanup.** Reclaim local disk by pruning merged or abandoned git worktrees and stale iOS simulators"),  # sentinel check below uses tail append instead
]

HARNESS_SECTION = """

## Harness

pstack was written for Cursor. In another harness (Claude Code, Codex, Pi, OpenCode, and others), read
Cursor-specific instructions in this skill, its playbooks, and the routed skills through these mappings.
If you can't tell which harness you are, check which of the paths below exist.

- **Subagents.** `Task` means your subagent tool: `Agent` in Claude Code (`subagent_type: general-purpose`),
  `task` in OpenCode (`subagent_type: general`), `spawn_agent` in Codex, `subagent` in Pi with the
  pi-subagents extension (one child per `{agent, task}` call; parallel steps via one workflow script with
  `runs.run`/`runs.all`; the `model` option sets the child's model; `worktree: true` isolates a child in its
  own worktree). Drop parameters your tool doesn't have. `environment: "cloud"` means a Cursor cloud agent.
  Elsewhere, run that agent locally in its own worktree. If your harness has no subagent tool (Pi without
  the pi-subagents extension included), do each delegated step yourself, one after another.
- **`poteto-agent`.** Where it isn't registered as a subagent, spawn a general subagent whose prompt starts
  with: "Read `agents/poteto-agent.md` in full before any work." Then give the task.
- **Transcripts.** Read only the active workspace's sessions, never other projects'. Cursor: the
  `agent-transcripts/` directory the system prompt names. Claude Code: `~/.claude/projects/<slug>/*.jsonl`,
  where `<slug>` is the workspace path with every character that isn't a letter or digit turned into "-".
  Pi: `~/.pi/agent/sessions/--<slug>--/*.jsonl`, where `<slug>` is the workspace path with the leading slash
  dropped and each "/" turned into "-". Codex: `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl`, keeping files
  whose first line has `payload.cwd` equal to the workspace path. OpenCode:
  `~/.local/share/opencode/storage/`.
- **Skill folders.** Project: `.cursor/skills/` (Cursor), `.claude/skills/` (Claude Code), `.pi/skills/` (Pi),
  `.agents/skills/` (Codex, OpenCode, and others). User: `~/.cursor/skills/`, `~/.claude/skills/`,
  `~/.pi/agent/skills/`, `~/.codex/skills/`, `~/.agents/skills/`.
"""

# Section insertions: (file, anchor-substring at end of which block, text-to-append)
INSERTIONS = [
    ("skills/poteto-mode/SKILL.md", HARNESS_SECTION),  # appended at EOF
    ("skills/poteto-mode/playbooks/orchestrate.md", None),  # handled via PATCHES below
]

ORCHESTRATE_PATCHES = [
    ("skills/poteto-mode/playbooks/orchestrate.md",
     "Agents are spawned, resumed, and drained only through the Task tool.",
     "Agents are spawned, resumed, and drained only through the harness's subagent tool (`Task` in Cursor, "
     "`Agent` in Claude Code, `task` in OpenCode, `spawn_agent` in Codex, `subagent` in Pi with the "
     "pi-subagents extension)."),
    ("skills/poteto-mode/playbooks/orchestrate.md",
     "Run a unit's verifier on a different model family from its worker.",
     "Run a unit's verifier on a different model family from its worker. Outside Cursor, run workers "
     "locally in their own worktree or output path."),
]

ALL_PATCHES = [p for p in PATCHES if p[1] != p[2]] + ORCHESTRATE_PATCHES


def main() -> int:
    patched, skipped, failed = [], [], []
    for rel, old, new in ALL_PATCHES:
        path = ROOT / rel
        try:
            text = path.read_text()
        except FileNotFoundError:
            failed.append((rel, "file missing"))
            continue
        if new in text:
            skipped.append(rel)
            continue
        if old not in text:
            failed.append((rel, f"pattern not found: {old[:70]}..."))
            continue
        path.write_text(text.replace(old, new, 1))
        patched.append(rel)

    # EOF insertion: poteto-mode Harness section
    pm = ROOT / "skills/poteto-mode/SKILL.md"
    text = pm.read_text()
    if "## Harness" in text:
        skipped.append("skills/poteto-mode/SKILL.md (Harness section)")
    else:
        if not text.endswith("\n"):
            text += "\n"
        pm.write_text(text + HARNESS_SECTION)
        patched.append("skills/poteto-mode/SKILL.md (Harness section)")

    for rel, msg in failed:
        print(f"FAIL    {rel}: {msg}")
    for rel in skipped:
        print(f"skip    {rel} (already applied)")
    for rel in patched:
        print(f"patched {rel}")

    files = sorted({rel.split('/')[0] + '/' + rel.split('/')[1] for rel in patched})
    print(f"\n{len(patched)} patches applied, {len(skipped)} skipped, {len(failed)} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
