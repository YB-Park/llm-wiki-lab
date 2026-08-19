from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(rel, old, new):
    path = ROOT / rel
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"missing patch marker in {rel}: {old[:120]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def replace_all(rel, old, new):
    path = ROOT / rel
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"missing patch marker in {rel}: {old[:120]!r}")
    path.write_text(text.replace(old, new), encoding="utf-8")


AGENT = "dogfood/vscode/agent-tools.js"
ENTRY = "dogfood/vscode/entry.js"
PACKAGE = "dogfood/vscode/package.json"
STATIC = "dogfood/vscode/test/static.js"
RUNTIME = "dogfood/vscode/test/integration/agent-tools-runtime.test.js"
E020 = "experiments/E020-synthetic-agent-ux/score_contract.py"
README = "dogfood/vscode/README.md"
AUDIT = "docs/13-vscode-release-ux-audit.md"

# P2: exact same current bytes are a no-op reuse, not a second authority mutation.
replace_once(AGENT, "const path = require('node:path');\n", "const path = require('node:path');\nconst crypto = require('node:crypto');\n")

replace_once(
    AGENT,
    """  if (\n    saved\n    && saved.continueToday === true\n    && saved.day === usage.day\n    && Number(saved.threshold) === threshold\n  ) {\n    budget.softGuardAcknowledged = true;\n    return { allowed: true, status: 'SOFT_GUARD_ACKNOWLEDGED', budget };\n  }\n\n  let continued = true;\n  if (context.extensionMode !== vscode.ExtensionMode.Test) {\n    const choice = await vscode.window.showWarningMessage(\n      'Continue AI summaries for the rest of today?',\n      {\n        modal: true,\n        detail: `LLM Wiki has reserved ${usage.reservedCalls} model-backed AI-summary call${usage.reservedCalls === 1 ? '' : 's'} today. Your saved source is already safe. This choice affects only optional AI summaries; the ${threshold}-call setting is a reminder, not a hard cap.`,\n      },\n      'Continue Today'\n    );\n    continued = choice === 'Continue Today';\n  }\n  if (!continued) {\n    return { allowed: false, status: 'SKIPPED_SOFT_GUARD_DECLINED', budget };\n  }\n\n  await context.workspaceState.update(key, {\n    day: usage.day,\n    threshold,\n    continueToday: true,\n  });\n  budget.softGuardAcknowledged = true;\n  return { allowed: true, status: 'SOFT_GUARD_ACKNOWLEDGED', budget };\n""",
    """  if (\n    saved\n    && saved.day === usage.day\n    && Number(saved.threshold) === threshold\n  ) {\n    if (saved.pauseToday === true) {\n      budget.softGuardPaused = true;\n      return { allowed: false, status: 'SKIPPED_SOFT_GUARD_PAUSED', budget };\n    }\n    if (saved.continueToday === true) {\n      budget.softGuardAcknowledged = true;\n      return { allowed: true, status: 'SOFT_GUARD_ACKNOWLEDGED', budget };\n    }\n  }\n\n  let choice = 'Continue Today';\n  if (context.extensionMode !== vscode.ExtensionMode.Test) {\n    choice = await vscode.window.showWarningMessage(\n      'Continue AI summaries for the rest of today?',\n      {\n        modal: true,\n        detail: `LLM Wiki has reserved ${usage.reservedCalls} model-backed AI-summary call${usage.reservedCalls === 1 ? '' : 's'} today. Your saved source is already safe. This choice affects only optional AI summaries; the ${threshold}-call setting is a reminder, not a hard cap.`,\n      },\n      'Continue Today',\n      'Pause AI Summaries Today'\n    );\n  }\n  if (choice === 'Pause AI Summaries Today') {\n    await context.workspaceState.update(key, { day: usage.day, threshold, pauseToday: true });\n    budget.softGuardPaused = true;\n    return { allowed: false, status: 'SKIPPED_SOFT_GUARD_PAUSED', budget };\n  }\n  if (choice !== 'Continue Today') {\n    return { allowed: false, status: 'SKIPPED_SOFT_GUARD_DECLINED', budget };\n  }\n\n  await context.workspaceState.update(key, {\n    day: usage.day,\n    threshold,\n    continueToday: true,\n  });\n  budget.softGuardAcknowledged = true;\n  return { allowed: true, status: 'SOFT_GUARD_ACKNOWLEDGED', budget };\n""",
)

replace_once(
    AGENT,
    """function dirtyOpenDocumentFor(filePath) {\n  const target = path.resolve(filePath);\n  return vscode.workspace.textDocuments.find((document) => (\n    document.uri.scheme === 'file'\n    && path.resolve(document.uri.fsPath) === target\n    && document.isDirty\n  ));\n}\n\n""",
    """function dirtyOpenDocumentFor(filePath) {\n  const target = path.resolve(filePath);\n  return vscode.workspace.textDocuments.find((document) => (\n    document.uri.scheme === 'file'\n    && path.resolve(document.uri.fsPath) === target\n    && document.isDirty\n  ));\n}\n\nfunction fileSha256(filePath) {\n  return crypto.createHash('sha256').update(fs.readFileSync(filePath)).digest('hex');\n}\n\nasync function findExactCurrentRememberedSource(context, folder, target, digest) {\n  if (!isWikiInitialized(folder)) return undefined;\n  const locators = await durableSourceLocators(context, folder);\n  const matchingSourceIds = new Set(\n    Object.entries(locators)\n      .filter(([, locator]) => locator && locator.relative_path === target.relativePath && locator.sha256 === digest)\n      .map(([sourceId]) => sourceId)\n  );\n  if (!matchingSourceIds.size) return undefined;\n\n  const topics = parseTopics(await runCli(context, folder, ['topic', 'list']));\n  for (const topic of topics) {\n    const rows = parseJsonLines(await runCli(context, folder, ['source', 'list', '--topic', topic.id, '--json']));\n    const row = rows.find((candidate) => matchingSourceIds.has(candidate.source_id) && candidate.sha256 === digest);\n    if (row) return { sourceId: row.source_id, sha256: digest, topic };\n  }\n  return undefined;\n}\n\n""",
)

for old, new in [
    ("`Searching current LLM Wiki memory for “${query.slice(0, 80)}”`", "`Searching project memory for “${query.slice(0, 80)}”`"),
    ("`Reading verified LLM Wiki evidence ${sourceId}`", "`Reading saved project evidence ${sourceId}`"),
    ("`Preparing explicit LLM Wiki admission for ${requested || 'the active editor file'}`", "`Preparing to save ${requested || 'the active editor file'} to project memory`"),
    ("`Preparing human-gated Wiki lineage decision ${id}`", "`Preparing a saved-file history decision ${id}`"),
    ("'Preparing explicit Human Knowledge memory for user confirmation'", "'Preparing your project knowledge for confirmation'"),
]:
    replace_once(AGENT, old, new)

replace_once(
    AGENT,
    """    if (dirtyOpenDocumentFor(target.filePath)) {\n      throw new Error('LLM Wiki will not auto-save a dirty editor. Save the file explicitly, then ask to remember it again. No Wiki mutation occurred.');\n    }\n\n    const dailySoftGuard = maintenanceDailyCallLimit();\n""",
    """    if (dirtyOpenDocumentFor(target.filePath)) {\n      throw new Error('LLM Wiki will not auto-save a dirty editor. Save the file explicitly, then ask to remember it again. No Wiki mutation occurred.');\n    }\n\n    const digest = fileSha256(target.filePath);\n    const existing = await findExactCurrentRememberedSource(this.context, folder, target, digest);\n    if (existing) {\n      const pendingRows = await openPendingLineageRows(this.context, folder);\n      const pending = pendingRows.find((row) => (\n        row.workspace_file === target.relativePath\n        && (row.successor_source_id === existing.sourceId || row.predecessor_source_ids.includes(existing.sourceId))\n      ));\n      let maintenance = {\n        status: pending ? 'SKIPPED_PENDING_LINEAGE_DECISION' : 'SKIPPED_NO_WORKSPACE_GRANT',\n        modelCalls: 0, model: '', policy: '', budget: await maintenanceUsage(this.context, folder),\n      };\n      if (!pending) {\n        try {\n          maintenance = await maintainSource(this.context, folder, existing.sourceId, existing.topic.id);\n        } catch (_) {\n          maintenance = {\n            status: 'FAILED_AFTER_RAW_REUSE', modelCalls: 'unknown', model: AGENT_WIKI_MODEL, policy: '',\n            failureCode: 'UNCLASSIFIED_MAINTENANCE_FAILURE', stage: 'unknown', modelCallAttempted: 'unknown',\n            budget: await maintenanceUsage(this.context, folder),\n          };\n        }\n      }\n      const usage = await maintenanceUsage(this.context, folder);\n      const text = [\n        'LLM_WIKI_REMEMBER_RESULT v4',\n        'authority=existing_source_reuse',\n        'canonical_mutation=none',\n        'raw_admission=reused_existing',\n        `source_id=${existing.sourceId}`,\n        `sha256=${existing.sha256}`,\n        `workspace_file_json=${jsonData(target.relativePath)}`,\n        `topic_id=${existing.topic.id}`,\n        `topic_json=${jsonData(existing.topic.label)}`,\n        `model_calls=${maintenance.modelCalls}`,\n        `derived_agent_wiki_maintenance=${maintenance.status}`,\n        `maintenance_failure_code=${maintenance.failureCode || ''}`,\n        `maintenance_stage=${maintenance.stage || ''}`,\n        `maintenance_model_call_attempted=${maintenance.modelCallAttempted || ''}`,\n        `maintenance_daily_soft_guard=${maintenanceDailyCallLimit()}`,\n        `maintenance_soft_guard_acknowledged=${maintenance.budget && maintenance.budget.softGuardAcknowledged === true ? 'yes' : 'no'}`,\n        `maintenance_soft_guard_paused=${maintenance.budget && maintenance.budget.softGuardPaused === true ? 'yes' : 'no'}`,\n        `maintenance_reserved_today=${usage.reservedCalls}`,\n        `pending_lineage_decision=${pending ? 'yes' : 'no'}`,\n        pending ? `pending_decision_id=${pending.id}` : 'pending_decision_id=',\n        '',\n        pending\n          ? 'This exact file content was already saved. No new evidence was admitted, and AI-summary maintenance remains paused until the existing file-history decision is resolved.'\n          : 'This exact file content was already present as current project evidence, so LLM Wiki reused it without asking for another source-admission confirmation.',\n      ].join('\\n');\n      return new vscode.LanguageModelToolResult([new vscode.LanguageModelTextPart(text)]);\n    }\n\n    const dailySoftGuard = maintenanceDailyCallLimit();\n""",
)

replace_all(
    AGENT,
    "`maintenance_soft_guard_acknowledged=${maintenance.budget && maintenance.budget.softGuardAcknowledged === true ? 'yes' : 'no'}`,\n      `maintenance_reserved_today=${usage.reservedCalls}`",
    "`maintenance_soft_guard_acknowledged=${maintenance.budget && maintenance.budget.softGuardAcknowledged === true ? 'yes' : 'no'}`,\n      `maintenance_soft_guard_paused=${maintenance.budget && maintenance.budget.softGuardPaused === true ? 'yes' : 'no'}`,\n      `maintenance_reserved_today=${usage.reservedCalls}`",
)

# P1: native VS Code Issue Reporter with bounded diagnostics only.
replace_once(
    ENTRY,
    "async function commandBoundary(label, fn) {\n",
    """async function reportIssue(context) {\n  const folders = vscode.workspace.workspaceFolders || [];\n  const lines = [\n    'LLM Wiki diagnostic metadata',\n    'No project evidence, prompts, source text, local paths, usernames, hostnames, or environment variables are included.',\n    `extension_version=${String((context.extension && context.extension.packageJSON && context.extension.packageJSON.version) || 'unknown')}`,\n    `vscode_version=${vscode.version}`,\n    `platform=${process.platform}`,\n    `workspace_folder_mode=${folders.length === 1 ? 'single' : (folders.length === 0 ? 'none' : 'multi')}`,\n  ];\n  if (folders.length === 1) {\n    const folder = folders[0];\n    const root = wikiRoot(folder);\n    const runtime = await resolvePythonRuntime(folder);\n    const copilotReady = await executableAvailable('copilot', ['--version'], folder.uri.fsPath);\n    const gitSafety = await classifyGitSafety(folder.uri.fsPath, root);\n    lines.push(`project_memory=${workspaceActivation.isWorkspaceEnabled(root) ? 'on' : (workspaceActivation.isCoreInitialized(root) ? 'off' : 'not_set_up')}`);\n    lines.push(`python_runtime=${runtime ? 'found' : 'missing'}`);\n    lines.push(`python_runtime_source=${runtime ? runtime.source : 'none'}`);\n    lines.push(`git_privacy=${gitSafety}`);\n    lines.push(`ai_summaries=${configuration().get('agentWikiMaintenanceEnabled', false) === true ? 'on' : 'off'}`);\n    lines.push(`copilot_cli_executable=${copilotReady ? 'found' : 'not_found'}`);\n  }\n  lines.push('ai_summary_model_call_readiness=not_verified_by_this_report');\n  await vscode.commands.executeCommand('vscode.openIssueReporter', {\n    extensionId: context.extension.id,\n    data: lines.join('\\n'),\n  });\n}\n\nasync function commandBoundary(label, fn) {\n""",
)
replace_once(
    ENTRY,
    "  context.subscriptions.push(vscode.commands.registerCommand('llmWiki.doctor', () => commandBoundary('Check Setup and Health', () => doctor(context))));\n",
    "  context.subscriptions.push(vscode.commands.registerCommand('llmWiki.doctor', () => commandBoundary('Check Setup and Health', () => doctor(context))));\n  context.subscriptions.push(vscode.commands.registerCommand('llmWiki.reportIssue', () => commandBoundary('Report an Issue', () => reportIssue(context))));\n",
)

# Manifest: release version + issue/reporter contribution; no extra Palette clutter.
replace_once(PACKAGE, '  "version": "0.1.15",', '  "version": "0.1.16",')
replace_once(PACKAGE, '    "onCommand:llmWiki.doctor",\n', '    "onCommand:llmWiki.doctor",\n    "onCommand:llmWiki.reportIssue",\n    "onIssueReporterOpened",\n')
replace_once(PACKAGE, '      { "command": "llmWiki.doctor", "title": "Check Setup and Health", "category": "LLM Wiki", "enablement": "isWorkspaceTrusted" },\n', '      { "command": "llmWiki.doctor", "title": "Check Setup and Health", "category": "LLM Wiki", "enablement": "isWorkspaceTrusted" },\n      { "command": "llmWiki.reportIssue", "title": "Report an Issue", "category": "LLM Wiki" },\n')
replace_once(PACKAGE, '        { "command": "llmWiki.doctor", "when": "isWorkspaceTrusted" },\n', '        { "command": "llmWiki.doctor", "when": "isWorkspaceTrusted" },\n        { "command": "llmWiki.reportIssue", "when": "false" },\n')
replace_once(
    PACKAGE,
    '        { "command": "llmWiki.experimentalDiscoverCopilotModels", "when": "false" }\n      ]\n    },\n    "languageModelTools": [',
    '        { "command": "llmWiki.experimentalDiscoverCopilotModels", "when": "false" }\n      ],\n      "issue/reporter": [\n        { "command": "llmWiki.reportIssue" }\n      ]\n    },\n    "languageModelTools": [',
)

# Static release contract.
replace_once(STATIC, "  'llmWiki.experimentalDiscoverCopilotModels',\n])", "  'llmWiki.reportIssue', 'llmWiki.experimentalDiscoverCopilotModels',\n])")
replace_once(STATIC, "assert.equal(commands.size, 18, 'STATIC-BOUNDARY command-count');", "assert.equal(commands.size, 19, 'STATIC-BOUNDARY command-count');")
replace_once(STATIC, "assert.equal(manifest.version, '0.1.15', 'STATIC-BOUNDARY version');", "assert.equal(manifest.version, '0.1.16', 'STATIC-BOUNDARY version');")
replace_once(
    STATIC,
    "must('doctor-model-readiness-unverified', entry.includes('AI-summary model-call readiness: NOT VERIFIED'));\n",
    "must('doctor-model-readiness-unverified', entry.includes('AI-summary model-call readiness: NOT VERIFIED'));\nmust('issue-reporter-command', entry.includes(\"registerCommand('llmWiki.reportIssue'\"));\nmust('issue-reporter-native', entry.includes(\"executeCommand('vscode.openIssueReporter'\"));\nmust('issue-reporter-bounded', entry.includes('No project evidence, prompts, source text, local paths, usernames, hostnames, or environment variables are included.'));\nconst issueReporterRows = manifest.contributes.menus['issue/reporter'] || [];\nassert.deepEqual(issueReporterRows.map((row) => row.command), ['llmWiki.reportIssue'], 'STATIC-BOUNDARY native-issue-reporter');\n",
)
replace_once(
    STATIC,
    "must('register-lineage-tool', agentTools.includes('vscode.lm.registerTool(RESOLVE_LINEAGE_TOOL'));\n",
    "must('register-lineage-tool', agentTools.includes('vscode.lm.registerTool(RESOLVE_LINEAGE_TOOL'));\nmust('same-bytes-reuse-before-confirm', agentTools.indexOf('findExactCurrentRememberedSource') < agentTools.indexOf(\"'Save this file to project memory?'\"));\nmust('same-bytes-reuse-result', agentTools.includes('raw_admission=reused_existing') && agentTools.includes('authority=existing_source_reuse'));\nmust('soft-guard-pause-today', agentTools.includes('Pause AI Summaries Today') && agentTools.includes('SKIPPED_SOFT_GUARD_PAUSED'));\n",
)

# Runtime regression: the second identical remember is no-op reuse and does not append canonical history.
replace_once(
    RUNTIME,
    """      const agentState = JSON.parse(fs.readFileSync(path.join(wikiRoot, 'agent-state.json'), 'utf8'));\n      const sourceId = field(text, 'source_id');\n      assert.equal(agentState.format, 'llm-wiki-agent-state-v0');\n      assert.equal(agentState.source_locators[sourceId].relative_path, 'runtime-dirty-remember.md');\n      assert.equal(agentState.maintenance_usage.reserved_calls, 0);\n""",
    """      const agentState = JSON.parse(fs.readFileSync(path.join(wikiRoot, 'agent-state.json'), 'utf8'));\n      const sourceId = field(text, 'source_id');\n      assert.equal(agentState.format, 'llm-wiki-agent-state-v0');\n      assert.equal(agentState.source_locators[sourceId].relative_path, 'runtime-dirty-remember.md');\n      assert.equal(agentState.maintenance_usage.reserved_calls, 0);\n\n      const manifestAfterAdmission = fs.readFileSync(path.join(wikiRoot, 'manifest.jsonl'), 'utf8');\n      const reused = toolText(await vscode.lm.invokeTool('llmWiki_rememberSource', {\n        input: { filePath: sourcePath }, toolInvocationToken: undefined,\n      }));\n      assert.match(reused, /authority=existing_source_reuse/);\n      assert.match(reused, /raw_admission=reused_existing/);\n      assert.match(reused, /canonical_mutation=none/);\n      assert.equal(field(reused, 'source_id'), sourceId);\n      assert.equal(fs.readFileSync(path.join(wikiRoot, 'manifest.jsonl'), 'utf8'), manifestAfterAdmission, 'same bytes reuse must not append canonical history');\n""",
)

# E020 stays 78 cases; strengthen the existing unchanged-source reuse mechanism marker only.
replace_once(E020, '    "maintenance_reuse": [(AGENT, "agent_wiki_model_call_not_authorized"), (AGENT, "preflightStdout")],\n', '    "maintenance_reuse": [(AGENT, "agent_wiki_model_call_not_authorized"), (AGENT, "preflightStdout")],\n    "exact_source_reuse": [(AGENT, "raw_admission=reused_existing"), (AGENT, "authority=existing_source_reuse")],\n')
replace_once(E020, '("S12", "same unchanged source reuses maintenance without spending again", "supported", ["maintenance_reuse"]),', '("S12", "same unchanged source reuses maintenance without spending again", "supported", ["maintenance_reuse", "exact_source_reuse"]),')
replace_once(E020, '    assert MANIFEST["version"] == "0.1.15"', '    assert MANIFEST["version"] == "0.1.16"')

# Release-facing docs.
replace_all(README, '0.1.15', '0.1.16')
audit_path = ROOT / AUDIT
audit = audit_path.read_text(encoding='utf-8')
final_note = """

## 0.1.16 P1/P2 release decisions

- Native VS Code Issue Reporter integration is included through `issue/reporter`; only bounded environment/readiness metadata is attached, never project evidence, prompts, source text, local paths, usernames, hostnames, or environment variables.
- New source bytes still require the product-owned source-admission confirmation. Explicit Agent chat intent alone is not treated as sufficient authority for a new durable evidence mutation in 0.1.16.
- Repeating an explicit remember request for the exact same current workspace file bytes is a no-op reuse: no new RAW admission, no canonical history append, and no second source-admission modal. Optional AI-summary reuse/maintenance still follows the existing workspace grant and spend guard.
- The daily AI-summary guard remains a soft guard. Users can choose `Continue Today` or `Pause AI Summaries Today`; an explicit pause is remembered only for that local day/threshold and does not alter Wiki knowledge.
- No dedicated Tree/View is added for 0.1.16. Normal Agent conversation remains primary; a permanent navigation UI remains evidence-gated.
- No separate global progress notification is added. Agent tool invocations already have contextual progress, and setup is kept synchronous/short; a new progress surface should require measured latency evidence.
"""
if '## 0.1.16 P1/P2 release decisions' not in audit:
    audit_path.write_text(audit.rstrip() + final_note + '\n', encoding='utf-8')

# Self-delete so this transport helper is not part of the release diff.
for rel in ['.github/ux-release-016-patch.py', '.github/workflows/ux-release-016-patch.yml']:
    try:
        (ROOT / rel).unlink()
    except FileNotFoundError:
        pass

print('0.1.16 atomic UX release patch applied')
