'use strict';

const fs = require('node:fs');
const path = require('node:path');
const vscode = require('vscode');
const library = require('./personal-wiki-library');
const memoryRead = require('./memory-read-service');
const remoteLibrary = require('./remote-library');
const remoteMemory = require('./remote-memory');

const COMMAND = 'llmWiki.configurePersonalWikiLibrary';

function firstWorkspaceFolder() {
  const folders = vscode.workspace.workspaceFolders || [];
  if (!folders.length) throw new Error('Open a trusted VS Code workspace/folder before managing other project memories.');
  if (folders.length !== 1) throw new Error('LLM Wiki currently supports one workspace folder at a time. Open the project as a single-folder workspace before using project memory.');
  return folders[0];
}

function testOptions(context, options) {
  return context.extensionMode === vscode.ExtensionMode.Test && options && typeof options === 'object' ? options : {};
}

function looksLikeStore(root) {
  return fs.existsSync(path.join(root, 'config.json')) && fs.existsSync(path.join(root, 'manifest.jsonl'));
}

function detectStoreFromSelection(selected) {
  const chosen = path.resolve(selected);
  if (path.basename(chosen) === '.wiki-lab' && looksLikeStore(chosen)) {
    return { root: chosen, projectRoot: path.dirname(chosen) };
  }
  const conventional = path.join(chosen, '.wiki-lab');
  if (looksLikeStore(conventional)) {
    return { root: conventional, projectRoot: chosen };
  }
  if (looksLikeStore(chosen)) {
    return { root: chosen, projectRoot: path.dirname(chosen) };
  }
  return undefined;
}

async function registerExternalStore(context, folder, options = {}) {
  const test = testOptions(context, options);
  let root = String(test.root || '').trim();
  let projectRoot;

  if (root) {
    const detected = detectStoreFromSelection(root);
    if (detected) {
      root = detected.root;
      projectRoot = detected.projectRoot;
    } else {
      projectRoot = path.basename(root) === '.wiki-lab' ? path.dirname(root) : path.dirname(root);
    }
  } else {
    const picked = await vscode.window.showOpenDialog({
      canSelectFiles: false,
      canSelectFolders: true,
      canSelectMany: false,
      openLabel: 'Add Project',
      title: 'Choose another project that already uses LLM Wiki',
    });
    if (!picked || picked.length !== 1) return undefined;
    const detected = detectStoreFromSelection(picked[0].fsPath);
    if (!detected) {
      const choice = await vscode.window.showWarningMessage(
        'LLM Wiki project memory was not found in that project.',
        'Choose Another Project'
      );
      if (choice === 'Choose Another Project') return registerExternalStore(context, folder, options);
      return undefined;
    }
    root = detected.root;
    projectRoot = detected.projectRoot;
  }

  const derivedName = path.basename(projectRoot || path.dirname(root)) || 'Other Project';
  let displayName = String(test.displayName || '').trim() || derivedName;
  if (displayName.length > 120) displayName = displayName.slice(0, 120);
  const aliases = Array.isArray(test.aliases) ? test.aliases.map(String) : [];

  const confirmed = context.extensionMode === vscode.ExtensionMode.Test
    ? true
    : await vscode.window.showWarningMessage(
      `Add “${displayName}” as read-only project memory?`,
      {
        modal: true,
        detail: 'You can consult this project only when you explicitly name it. LLM Wiki will not write to it, merge it into a global memory, search every project automatically, or run cross-project maintenance.',
      },
      'Add Read-only Project'
    );
  if (confirmed !== true && confirmed !== 'Add Read-only Project') return undefined;

  const row = await library.registerStore(context, {
    root,
    currentRoot: memoryRead.wikiRoot(folder),
    displayName,
    aliases,
  });

  if (context.extensionMode !== vscode.ExtensionMode.Test) {
    const currentRoot = memoryRead.wikiRoot(folder);
    const existingGrant = library.libraryGrant(context, folder, currentRoot);
    if (!existingGrant) {
      const access = await vscode.window.showInformationMessage(
        `Added “${row.displayName}”. Allow this workspace to consult explicitly named added projects?`,
        'Allow Here',
        'Not Now'
      );
      if (access === 'Allow Here') {
        await library.setLibraryAccess(context, folder, currentRoot, true);
        vscode.window.showInformationMessage(`“${row.displayName}” is ready for this workspace when AI-assisted memory answers are enabled.`);
      }
    } else {
      vscode.window.showInformationMessage(`Added “${row.displayName}” as read-only project memory.`);
    }
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
  let remoteConnected = false;
  try { remoteConnected = remoteMemory.isConfigured(context, folder); } catch (_) { remoteConnected = false; }

  if (!action) {
    const choice = await vscode.window.showQuickPick([
      {
        label: '$(add) Add a project from this computer',
        description: 'Choose its project folder; LLM Wiki finds the local memory automatically',
        action: 'register',
      },
      ...(remoteConnected ? [{
        label: '$(cloud-download) Add or refresh a project from Personal Wiki',
        description: 'Choose one exact remote project; cache a verified read-only copy on this host',
        action: 'remote-register',
      }] : []),
      {
        label: grant ? '$(circle-slash) Stop using added projects here' : '$(key) Allow added projects in this workspace',
        description: grant
          ? 'Keeps the projects registered but revokes this workspace access'
          : 'Allows only projects you explicitly name; no all-project search',
        action: grant ? 'disable' : 'enable',
      },
      ...(stores.length ? [{
        label: '$(trash) Remove an added project',
        description: 'Removes only the local registration; the other project is untouched',
        action: 'remove',
      }] : []),
    ], {
      title: 'LLM Wiki: Other Project Memories',
      placeHolder: stores.length
        ? `${stores.length} project${stores.length === 1 ? '' : 's'} added · access ${grant ? 'on' : 'off'} in this workspace`
        : 'Add a project if you want Agent chat to consult its LLM Wiki memory explicitly',
      ignoreFocusOut: true,
    });
    if (!choice) return undefined;
    action = choice.action;
  }

  if (action === 'register') return registerExternalStore(context, folder, test);
  if (action === 'remote-register') return remoteLibrary.addRemoteProject(context, folder, test);

  if (action === 'enable') {
    const approved = context.extensionMode === vscode.ExtensionMode.Test
      ? true
      : await vscode.window.showWarningMessage(
        'Allow this workspace to consult added project memories?',
        {
          modal: true,
          detail: 'Only an explicitly named registered project can be consulted. Ordinary questions remain scoped to this project. This does not enable all-project search, external writes, or cross-project maintenance.',
        },
        'Allow Added Projects'
      );
    if (approved !== true && approved !== 'Allow Added Projects') return undefined;
    await library.setLibraryAccess(context, folder, currentRoot, true);
    if (context.extensionMode !== vscode.ExtensionMode.Test) vscode.window.showInformationMessage('Added project memories are allowed in this workspace.');
    return true;
  }

  if (action === 'disable') {
    await library.setLibraryAccess(context, folder, currentRoot, false);
    if (context.extensionMode !== vscode.ExtensionMode.Test) vscode.window.showInformationMessage('This workspace will no longer consult added project memories.');
    return false;
  }

  if (action === 'remove') {
    let storeId = String(test.storeId || '').trim();
    let displayName = '';
    if (!storeId) {
      const selected = await vscode.window.showQuickPick(
        stores.map((row) => ({
          label: row.displayName,
          description: 'Read-only project memory',
          storeId: row.storeId,
        })),
        { title: 'Remove an added project', ignoreFocusOut: true }
      );
      if (!selected) return undefined;
      storeId = selected.storeId;
      displayName = selected.label;
    } else {
      displayName = (stores.find((row) => row.storeId === storeId) || {}).displayName || 'added project';
    }
    const approved = context.extensionMode === vscode.ExtensionMode.Test
      ? true
      : await vscode.window.showWarningMessage(
        `Remove “${displayName}” from Other Project Memories?`,
        { modal: true, detail: 'Only this machine’s registration is removed. The other project and all of its memory remain untouched.' },
        'Remove Project'
      );
    if (approved !== true && approved !== 'Remove Project') return undefined;
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
  detectStoreFromSelection,
  registerExternalStore,
  registerPersonalWikiLibraryCommand,
};