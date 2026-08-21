'use strict';

const path = require('node:path');
const vscode = require('vscode');
const library = require('./personal-wiki-library');
const memoryRead = require('./memory-read-service');

const COMMAND = 'llmWiki.configurePersonalWikiLibrary';

function firstWorkspaceFolder() {
  const folders = vscode.workspace.workspaceFolders || [];
  if (!folders.length) throw new Error('Open a trusted VS Code workspace/folder before configuring Personal Wiki Library.');
  if (folders.length !== 1) throw new Error('LLM Wiki currently supports one workspace folder at a time. Open the project as a single-folder workspace before using project memory.');
  return folders[0];
}

function testOptions(context, options) {
  return context.extensionMode === vscode.ExtensionMode.Test && options && typeof options === 'object' ? options : {};
}

async function registerExternalStore(context, folder, options = {}) {
  const test = testOptions(context, options);
  let root = String(test.root || '').trim();
  if (!root) {
    const picked = await vscode.window.showOpenDialog({
      canSelectFiles: false,
      canSelectFolders: true,
      canSelectMany: false,
      openLabel: 'Select LLM Wiki Store',
      title: 'Select the external project LLM Wiki store folder (usually .wiki-lab)',
    });
    if (!picked || picked.length !== 1) return undefined;
    root = picked[0].fsPath;
  }

  const parentLabel = path.basename(root) === '.wiki-lab' ? path.basename(path.dirname(root)) : path.basename(root);
  let displayName = String(test.displayName || '').trim();
  if (!displayName) {
    displayName = await vscode.window.showInputBox({
      title: 'Personal Wiki Library: Project name',
      prompt: 'Logical project name shown in scoped Wiki results. This is metadata, not authority identity.',
      value: parentLabel,
      ignoreFocusOut: true,
      validateInput: (value) => {
        const text = String(value || '').trim();
        if (!text) return 'A project name is required.';
        if (text.length > 120) return 'Use 120 characters or fewer.';
        return undefined;
      },
    });
    if (displayName === undefined) return undefined;
    displayName = displayName.trim();
  }

  let aliases = Array.isArray(test.aliases) ? test.aliases.map(String) : undefined;
  if (!aliases) {
    const aliasText = await vscode.window.showInputBox({
      title: 'Personal Wiki Library: Optional aliases',
      prompt: 'Comma-separated names that may explicitly select this store. Ambiguous aliases fail closed.',
      placeHolder: 'project-a, legacy-name',
      ignoreFocusOut: true,
    });
    if (aliasText === undefined) return undefined;
    aliases = aliasText.split(',').map((item) => item.trim()).filter(Boolean);
  }

  const confirmed = context.extensionMode === vscode.ExtensionMode.Test
    ? true
    : await vscode.window.showWarningMessage(
      `Register “${displayName}” as a read-only Personal Wiki source?`,
      {
        modal: true,
        detail: 'Registration allows this local project store to be selected only by an explicit named-store request. Its admitted evidence may be returned to the current Agent and, only when both current Query Reasoning and current-workspace library access are separately enabled, bounded evidence may be sent to exact gpt-5.6-luna. Registration does not authorize writes, sync, ambient library search, or cross-project maintenance.',
      },
      'Register Read-only Store'
    );
  if (confirmed !== true && confirmed !== 'Register Read-only Store') return undefined;

  const row = await library.registerStore(context, {
    root,
    currentRoot: memoryRead.wikiRoot(folder),
    displayName,
    aliases,
  });
  if (context.extensionMode !== vscode.ExtensionMode.Test) {
    vscode.window.showInformationMessage(`Registered “${row.displayName}” as a read-only Personal Wiki source. Named-store access for this workspace is a separate setting.`);
  }
  return row;
}

async function configurePersonalWikiLibrary(context, options = {}) {
  const folder = firstWorkspaceFolder();
  const currentRoot = memoryRead.wikiRoot(folder);
  const grant = library.libraryGrant(context, folder, currentRoot);
  const stores = library.registeredStores(context);
  const test = testOptions(context, options);
  let action = String(test.action || '').trim();
  if (!action) {
    const choice = await vscode.window.showQuickPick([
      {
        label: '$(add) Register read-only project store',
        description: 'Add another local LLM Wiki store with explicit external-read/model-exposure disclosure',
        action: 'register',
      },
      {
        label: grant ? '$(circle-slash) Disable named-store access for this workspace' : '$(key) Enable named-store access for this workspace',
        description: grant ? 'Revokes this workspace library grant; registrations remain' : 'Allows explicit named-store requests only; no ambient library search',
        action: grant ? 'disable' : 'enable',
      },
      ...(stores.length ? [{
        label: '$(trash) Remove registered project store',
        description: 'Remove a read-only registration; canonical project data is untouched',
        action: 'remove',
      }] : []),
    ], {
      title: 'LLM Wiki: Configure Personal Wiki Library',
      placeHolder: `${stores.length} registered read-only store${stores.length === 1 ? '' : 's'}; named-store access ${grant ? 'ON' : 'OFF'} for this workspace`,
      ignoreFocusOut: true,
    });
    if (!choice) return undefined;
    action = choice.action;
  }

  if (action === 'register') return registerExternalStore(context, folder, test);
  if (action === 'enable') {
    const approved = context.extensionMode === vscode.ExtensionMode.Test
      ? true
      : await vscode.window.showWarningMessage(
        'Enable named-store Personal Wiki access for this workspace?',
        {
          modal: true,
          detail: 'This workspace may explicitly select a registered read-only project store by its exact name/alias. Ordinary project questions stay current-store-only. This grant does not widen the existing current_store Query Reasoning grant, does not enable ambient all-project search, and becomes stale if project memory is disabled and re-enabled.',
        },
        'Enable Named-store Access'
      );
    if (approved !== true && approved !== 'Enable Named-store Access') return undefined;
    await library.setLibraryAccess(context, folder, currentRoot, true);
    return true;
  }
  if (action === 'disable') {
    await library.setLibraryAccess(context, folder, currentRoot, false);
    return false;
  }
  if (action === 'remove') {
    let storeId = String(test.storeId || '').trim();
    let displayName = '';
    if (!storeId) {
      const selected = await vscode.window.showQuickPick(
        stores.map((row) => ({ label: row.displayName, description: row.storeId, storeId: row.storeId })),
        { title: 'Remove a Personal Wiki registration', ignoreFocusOut: true }
      );
      if (!selected) return undefined;
      storeId = selected.storeId;
      displayName = selected.label;
    } else {
      displayName = (stores.find((row) => row.storeId === storeId) || {}).displayName || 'registered project';
    }
    const approved = context.extensionMode === vscode.ExtensionMode.Test
      ? true
      : await vscode.window.showWarningMessage(
        `Remove “${displayName}” from Personal Wiki Library?`,
        { modal: true, detail: 'Only the local registration is removed. The project Wiki store and its canonical evidence are not modified.' },
        'Remove Registration'
      );
    if (approved !== true && approved !== 'Remove Registration') return undefined;
    return library.removeStore(context, storeId);
  }
  throw new Error('library_configuration_action_invalid');
}

function registerPersonalWikiLibraryCommand(context) {
  context.subscriptions.push(vscode.commands.registerCommand(COMMAND, (options) => configurePersonalWikiLibrary(context, options || {})));
}

module.exports = {
  COMMAND,
  configurePersonalWikiLibrary,
  registerPersonalWikiLibraryCommand,
};