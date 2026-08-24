'use strict';

const vscode = require('vscode');
const memoryRead = require('./memory-read-service');
const queryPlane = require('./query-plane');
const workspaceActivation = require('./workspace-activation');

const COMMAND = 'llmWiki.configureAiAnswersFriendly';

function firstWorkspaceFolder() {
  const folders = vscode.workspace.workspaceFolders || [];
  if (!folders.length) throw new Error('Open a trusted workspace before configuring AI-assisted memory answers.');
  if (folders.length !== 1) throw new Error('LLM Wiki currently supports one workspace folder at a time.');
  return folders[0];
}

function currentOptIn(folder) {
  return workspaceActivation.readWorkspaceOptIn(memoryRead.wikiRoot(folder));
}

async function customLimits() {
  const rawDaily = await vscode.window.showInputBox({
    title: 'AI-assisted memory answers: daily attempts',
    prompt: 'Maximum model-backed memory-answer attempts allowed per day in this workspace.',
    value: '15',
    ignoreFocusOut: true,
    validateInput: (value) => {
      const number = Number(value);
      return Number.isInteger(number) && number >= 1 && number <= 100 ? undefined : 'Enter an integer from 1 to 100.';
    },
  });
  if (rawDaily === undefined) return undefined;

  const rawCredits = await vscode.window.showInputBox({
    title: 'AI-assisted memory answers: per-answer AI credit guard',
    prompt: 'Copilot soft maximum AI credits for each memory answer. This is a provider usage guard, not an exact bill.',
    value: '30',
    ignoreFocusOut: true,
    validateInput: (value) => {
      const number = Number(value);
      return Number.isInteger(number) && number >= 1 && number <= 100 ? undefined : 'Enter an integer from 1 to 100.';
    },
  });
  if (rawCredits === undefined) return undefined;
  return { dailyCallLimit: Number(rawDaily), maxAiCredits: Number(rawCredits), label: 'Custom' };
}

async function chooseLimits() {
  const picked = await vscode.window.showQuickPick([
    {
      label: 'Light',
      description: '5 AI memory answers/day · 20 credits/answer',
      detail: 'Good for occasional questions where local search is usually enough.',
      dailyCallLimit: 5,
      maxAiCredits: 20,
    },
    {
      label: 'Regular',
      description: '15/day · 30 credits/answer',
      detail: 'A balanced starting point for normal project work.',
      dailyCallLimit: 15,
      maxAiCredits: 30,
    },
    {
      label: 'Frequent',
      description: '40/day · 50 credits/answer',
      detail: 'For memory-heavy work; still locally bounded and revocable.',
      dailyCallLimit: 40,
      maxAiCredits: 50,
    },
    {
      label: 'Custom…',
      description: 'Choose both limits yourself',
      custom: true,
    },
  ], {
    title: 'How often should AI-assisted memory answers be available?',
    placeHolder: 'Nothing is selected automatically',
    ignoreFocusOut: true,
  });
  if (!picked) return undefined;
  if (picked.custom) return customLimits();
  return {
    dailyCallLimit: picked.dailyCallLimit,
    maxAiCredits: picked.maxAiCredits,
    label: picked.label,
  };
}

async function configureAiAnswers(context) {
  const folder = firstWorkspaceFolder();
  const current = queryPlane.queryGrant(context, folder);

  if (current) {
    const picked = await vscode.window.showQuickPick([
      {
        label: 'Change usage limits',
        description: `Currently ${current.dailyCallLimit}/day · ${current.maxAiCredits} credits/answer`,
        action: 'change',
      },
      {
        label: 'Turn off AI-assisted memory answers',
        description: 'Local saved memory remains available to deterministic Agent tools',
        action: 'disable',
      },
    ], {
      title: 'AI-assisted memory answers are on',
      placeHolder: 'Choose what you want to change',
      ignoreFocusOut: true,
    });
    if (!picked) return undefined;
    if (picked.action === 'disable') {
      const confirmed = await vscode.window.showWarningMessage(
        'Turn off AI-assisted memory answers for this workspace?',
        { modal: true, detail: 'This stops future model-backed memory answers. Saved project memory is not deleted.' },
        'Turn Off'
      );
      if (confirmed !== 'Turn Off') return undefined;
      await context.workspaceState.update(queryPlane.grantKey(folder), undefined);
      vscode.window.showInformationMessage('AI-assisted memory answers are off.');
      return false;
    }
  } else {
    const optIn = currentOptIn(folder);
    if (!optIn) throw new Error('query_plane_workspace_not_enabled');
    const confirmed = await vscode.window.showWarningMessage(
      'Turn on AI-assisted memory answers?',
      {
        modal: true,
        detail: 'When a memory question needs deeper reasoning, LLM Wiki may send a bounded set of already-saved evidence to GitHub Copilot using gpt-5.6-luna. This is read-only, locally limited, and revocable. Other-project memory still requires its own separate workspace access.',
      },
      'Choose Limits'
    );
    if (confirmed !== 'Choose Limits') return undefined;
  }

  const limits = await chooseLimits();
  if (!limits) return undefined;
  const optIn = currentOptIn(folder);
  if (!optIn) throw new Error('query_plane_workspace_not_enabled');

  const previous = context.workspaceState.get(queryPlane.grantKey(folder));
  const grant = {
    version: queryPlane.GRANT_VERSION,
    enabled: true,
    provider: 'github_copilot',
    model: queryPlane.MODEL,
    scope: 'current_store',
    evidenceExposure: 'retrieved_admitted_memory_only',
    workspaceEnabledAt: optIn.enabled_at,
    workspaceEpoch: workspaceActivation.workspaceEpoch(optIn),
    dailyCallLimit: limits.dailyCallLimit,
    maxAiCredits: limits.maxAiCredits,
  };

  await context.workspaceState.update(queryPlane.grantKey(folder), grant);
  const validated = queryPlane.queryGrant(context, folder);
  if (!validated) {
    await context.workspaceState.update(queryPlane.grantKey(folder), previous);
    throw new Error('AI-assisted memory-answer settings did not satisfy the current Query Plane grant contract. No new grant was kept.');
  }

  vscode.window.showInformationMessage(
    `AI-assisted memory answers are on: ${limits.dailyCallLimit}/day · ${limits.maxAiCredits} credits/answer.`
  );
  return true;
}

function registerProductQueryConfig(context) {
  context.subscriptions.push(vscode.commands.registerCommand(COMMAND, () => configureAiAnswers(context)));
}

module.exports = {
  COMMAND,
  chooseLimits,
  configureAiAnswers,
  registerProductQueryConfig,
};
