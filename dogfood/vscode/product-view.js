'use strict';

const vscode = require('vscode');
const memoryRead = require('./memory-read-service');
const personalLibrary = require('./personal-wiki-library');
const productActions = require('./product-actions');
const productQueryConfig = require('./product-query-config');
const remoteAttach = require('./remote-attach');
const remoteMemory = require('./remote-memory');
const { queryGrant } = require('./query-plane');
const workspaceActivation = require('./workspace-activation');

const VIEW_ID = 'llmWiki.overview';
const WORKSPACE_ELIGIBLE_CONTEXT = 'llmWiki.workspaceEligible';
const REFRESH_COMMAND = 'llmWiki.refreshOverview';
const OPEN_CHAT_COMMAND = 'llmWiki.openAgentChat';
const CONNECT_PERSONAL_WIKI_COMMAND = 'llmWiki.connectPersonalWiki';
const REFRESH_PERSONAL_WIKI_COMMAND = 'llmWiki.refreshPersonalWiki';
const CONFIGURE_SUMMARIES_FROM_OVERVIEW = 'llmWiki.overview.configureAiSummaries';
const CONFIGURE_ANSWERS_FROM_OVERVIEW = 'llmWiki.overview.configureAiAnswers';
const CONFIGURE_OTHER_PROJECTS_FROM_OVERVIEW = 'llmWiki.overview.configureOtherProjects';

function firstEligibleFolder() {
  const folders = vscode.workspace.workspaceFolders || [];
  if (folders.length !== 1 || !vscode.workspace.isTrusted) return undefined;
  return folders[0];
}

function enabledState(context, folder) {
  const root = memoryRead.wikiRoot(folder);
  const workspaceEnabled = workspaceActivation.isWorkspaceEnabled(root);
  const maintenanceOn = vscode.workspace.getConfiguration('llmWiki').get('agentWikiMaintenanceEnabled', false) === true;
  const query = workspaceEnabled ? queryGrant(context, folder) : undefined;
  const libraryAccess = workspaceEnabled ? Boolean(personalLibrary.libraryGrant(context, folder, root)) : false;

  let stores = [];
  let libraryCatalogReady = true;
  try {
    stores = personalLibrary.registeredStores(context);
  } catch (_) {
    libraryCatalogReady = false;
  }

  let remote;
  try {
    remote = remoteMemory.status(context, folder);
  } catch (_) {
    remote = { configured: true, writable: false, mode: 'offline_read_only', refreshPending: false, corrupt: true };
  }

  return {
    workspaceEnabled,
    maintenanceOn,
    queryOn: Boolean(query),
    libraryAccess,
    libraryCatalogReady,
    stores,
    remote,
  };
}

function statusIcon(on) {
  return new vscode.ThemeIcon(on ? 'check' : 'circle-slash');
}

function node(label, options = {}) {
  return {
    label,
    description: options.description || '',
    tooltip: options.tooltip || '',
    iconPath: options.iconPath,
    command: options.command,
    collapsibleState: options.collapsibleState === undefined
      ? vscode.TreeItemCollapsibleState.None
      : options.collapsibleState,
    kind: options.kind || 'leaf',
  };
}

function remoteNode(state) {
  const remote = state.remote;
  if (!remote || !remote.configured) {
    return node('Personal Wiki', {
      description: 'Not connected',
      tooltip: 'Connect over your existing non-interactive SSH setup. You can create a new independent remote Project Memory or explicitly choose an existing Personal Wiki project to continue on this PC.',
      iconPath: new vscode.ThemeIcon('remote'),
      command: { command: CONNECT_PERSONAL_WIKI_COMMAND, title: 'Connect Personal Wiki' },
    });
  }
  if (remote.corrupt) {
    return node('Personal Wiki', {
      description: 'Needs attention · read only',
      tooltip: 'The host-local Personal Wiki connection record could not be validated. Project Memory writes are blocked.',
      iconPath: new vscode.ThemeIcon('warning'),
      command: { command: REFRESH_PERSONAL_WIKI_COMMAND, title: 'Refresh Personal Wiki' },
    });
  }
  if (remote.refreshPending) {
    return node('Personal Wiki', {
      description: 'Refresh pending · read only',
      tooltip: 'A remote write was committed, but the local verified copy did not refresh. Reads use the last verified copy and may be stale. Refresh before any further Project Memory write.',
      iconPath: new vscode.ThemeIcon('warning'),
      command: { command: REFRESH_PERSONAL_WIKI_COMMAND, title: 'Refresh Personal Wiki' },
    });
  }
  if (remote.writable) {
    return node('Personal Wiki', {
      description: 'Connected · read/write',
      tooltip: 'This workspace writes only its exact remote project store. Reads use the last verified local copy. Click to refresh it explicitly.',
      iconPath: new vscode.ThemeIcon('cloud'),
      command: { command: REFRESH_PERSONAL_WIKI_COMMAND, title: 'Refresh Personal Wiki' },
    });
  }
  return node('Personal Wiki', {
    description: 'Offline · read only',
    tooltip: 'The remote authority is unavailable or unverified. Reads use the last verified local copy and may be stale; all Project Memory writes are blocked.',
    iconPath: new vscode.ThemeIcon('debug-disconnect'),
    command: { command: REFRESH_PERSONAL_WIKI_COMMAND, title: 'Refresh Personal Wiki' },
  });
}

class LlmWikiOverviewProvider {
  constructor(context) {
    this.context = context;
    this._onDidChangeTreeData = new vscode.EventEmitter();
    this.onDidChangeTreeData = this._onDidChangeTreeData.event;
  }

  refresh() {
    void this.updateWorkspaceContext();
    this._onDidChangeTreeData.fire(undefined);
  }

  async updateWorkspaceContext() {
    const folder = firstEligibleFolder();
    await vscode.commands.executeCommand('setContext', WORKSPACE_ELIGIBLE_CONTEXT, Boolean(folder));
    if (folder) await remoteMemory.setContexts(this.context, folder);
  }

  getTreeItem(element) {
    const item = new vscode.TreeItem(element.label, element.collapsibleState);
    item.description = element.description;
    item.tooltip = element.tooltip || element.label;
    item.iconPath = element.iconPath;
    item.command = element.command;
    if (element.kind === 'store') item.contextValue = 'llmWiki.otherProjectMemory';
    return item;
  }

  getChildren(element) {
    const folder = firstEligibleFolder();
    if (!folder) return [];

    const state = enabledState(this.context, folder);
    if (!state.workspaceEnabled) return [];

    if (element && element.kind === 'stores') {
      return state.stores.map((store) => node(store.displayName, {
        description: 'Read only',
        tooltip: 'This project can be consulted only when you explicitly name it and this workspace has access.',
        iconPath: new vscode.ThemeIcon('folder'),
        kind: 'store',
      }));
    }

    if (element) return [];

    let otherProjectDescription;
    let otherProjectTooltip;
    let otherProjectIcon;
    if (!state.libraryCatalogReady) {
      otherProjectDescription = 'Needs attention';
      otherProjectTooltip = 'The local other-project memory catalog could not be read. Use Check Setup and Health for technical details.';
      otherProjectIcon = new vscode.ThemeIcon('warning');
    } else if (!state.stores.length) {
      otherProjectDescription = 'None added';
      otherProjectTooltip = 'Add another local project so you can explicitly consult its memory read-only.';
      otherProjectIcon = new vscode.ThemeIcon('folder');
    } else if (!state.libraryAccess) {
      otherProjectDescription = `${state.stores.length} added · access off`;
      otherProjectTooltip = 'Projects are added, but this workspace is not allowed to consult them yet.';
      otherProjectIcon = new vscode.ThemeIcon('circle-slash');
    } else if (!state.queryOn) {
      otherProjectDescription = `${state.stores.length} added · AI answers off`;
      otherProjectTooltip = 'Other-project access is allowed. Turn on AI-assisted memory answers to consult an explicitly named project.';
      otherProjectIcon = new vscode.ThemeIcon('circle-slash');
    } else {
      otherProjectDescription = `${state.stores.length} added · ready`;
      otherProjectTooltip = 'Explicitly named other projects can be consulted read-only from Agent chat.';
      otherProjectIcon = new vscode.ThemeIcon('check');
    }

    return [
      node('Ask Agent with project memory', {
        description: 'Open chat',
        tooltip: 'Continue normal work in Agent chat. LLM Wiki memory tools are available there.',
        iconPath: new vscode.ThemeIcon('comment-discussion'),
        command: { command: OPEN_CHAT_COMMAND, title: 'Open Agent Chat' },
      }),
      node('Remember active file', {
        description: state.remote && state.remote.configured && !state.remote.writable ? 'Unavailable while read only' : 'Save to project memory',
        tooltip: state.remote && state.remote.configured && !state.remote.writable
          ? 'Personal Wiki is read only. Refresh the remote authority before saving anything to Project Memory.'
          : 'Save the currently open local project file through the same guarded source-admission path used by Agent chat.',
        iconPath: new vscode.ThemeIcon('save'),
        command: { command: productActions.REMEMBER_COMMAND, title: 'Remember Active File' },
      }),
      node('Review saved-file changes', {
        description: state.remote && state.remote.configured && !state.remote.writable ? 'Unavailable while read only' : 'Resolve what changed',
        tooltip: state.remote && state.remote.configured && !state.remote.writable
          ? 'Personal Wiki is read only. Refresh the remote authority before recording a file-history decision.'
          : 'Review a newer saved revision and describe its meaning in plain language. Verified old/new evidence is shown before the final decision is recorded.',
        iconPath: new vscode.ThemeIcon('diff'),
        command: { command: productActions.REVIEW_CHANGES_COMMAND, title: 'Review Saved-file Changes' },
      }),
      node('Project memory', {
        description: 'On',
        tooltip: 'This workspace is allowed to use its project memory in Agent conversations.',
        iconPath: statusIcon(true),
      }),
      remoteNode(state),
      node('AI summaries', {
        description: state.maintenanceOn ? 'On' : 'Off',
        tooltip: state.maintenanceOn
          ? 'Optional AI summaries are enabled for explicitly saved sources. Click to change this setting.'
          : 'Optional AI summaries are off. Project memory still works without them. Click to change this setting.',
        iconPath: statusIcon(state.maintenanceOn),
        command: { command: CONFIGURE_SUMMARIES_FROM_OVERVIEW, title: 'Configure AI Summaries' },
      }),
      node('AI-assisted memory answers', {
        description: state.queryOn ? 'On' : 'Off',
        tooltip: state.queryOn
          ? 'Bounded saved memory may be sent to GitHub Copilot for read-only memory reasoning. Click to change access or limits.'
          : 'AI-assisted memory reasoning is off. Deterministic memory search/read still works. Click to choose an explicit usage level.',
        iconPath: statusIcon(state.queryOn),
        command: { command: CONFIGURE_ANSWERS_FROM_OVERVIEW, title: 'Configure AI-assisted Memory Answers' },
      }),
      node('Other project memories', {
        description: otherProjectDescription,
        tooltip: `${otherProjectTooltip} Click to manage projects; use the disclosure arrow to inspect registered names.`,
        iconPath: otherProjectIcon,
        command: { command: CONFIGURE_OTHER_PROJECTS_FROM_OVERVIEW, title: 'Manage Other Project Memories' },
        collapsibleState: state.libraryCatalogReady && state.stores.length
          ? vscode.TreeItemCollapsibleState.Collapsed
          : vscode.TreeItemCollapsibleState.None,
        kind: 'stores',
      }),
    ];
  }

  dispose() {
    this._onDidChangeTreeData.dispose();
  }
}

async function runRemoteAction(context, provider, action) {
  const folder = firstEligibleFolder();
  if (!folder) throw new Error('Open and trust exactly one workspace folder first.');
  try {
    const result = await action(folder);
    provider.refresh();
    return result;
  } catch (error) {
    provider.refresh();
    const detail = error && error.message ? String(error.message) : String(error);
    if (detail.startsWith('REMOTE_WRITE_COMMITTED_REFRESH_PENDING')) {
      await vscode.window.showWarningMessage('Personal Wiki saved the remote change, but the local verified copy could not refresh. Project Memory is read only until Refresh Personal Wiki succeeds.');
    } else if (detail.startsWith('REMOTE_OFFLINE_READ_ONLY') || detail.includes('remote_ssh_') || detail.includes('remote_process_')) {
      await vscode.window.showWarningMessage('Personal Wiki is unavailable. The last verified local copy remains readable, but Project Memory writes are blocked.');
    } else if (detail.includes('remote_attach_requires_empty_local_memory')) {
      await vscode.window.showWarningMessage('Use Existing Project Memory is available only before this PC has its own saved Project Memory. LLM Wiki will not merge or overwrite independent local memory.');
    } else {
      await vscode.window.showErrorMessage('LLM Wiki could not complete the Personal Wiki action. Use Check Setup and Health for local diagnostics.');
    }
    return undefined;
  }
}

function registerProductView(context) {
  productActions.registerProductActions(context);
  productQueryConfig.registerProductQueryConfig(context);
  const provider = new LlmWikiOverviewProvider(context);
  const tree = vscode.window.createTreeView(VIEW_ID, { treeDataProvider: provider });

  const runAndRefresh = async (command) => {
    await vscode.commands.executeCommand(command);
    provider.refresh();
  };

  context.subscriptions.push(provider, tree);
  context.subscriptions.push(vscode.commands.registerCommand(REFRESH_COMMAND, () => provider.refresh()));
  context.subscriptions.push(vscode.commands.registerCommand(OPEN_CHAT_COMMAND, () => (
    vscode.commands.executeCommand('workbench.action.chat.open')
  )));
  context.subscriptions.push(vscode.commands.registerCommand(
    CONNECT_PERSONAL_WIKI_COMMAND,
    () => runRemoteAction(context, provider, (folder) => remoteAttach.chooseConnection(
      context,
      folder,
      () => remoteMemory.connect(context, folder)
    ))
  ));
  context.subscriptions.push(vscode.commands.registerCommand(
    REFRESH_PERSONAL_WIKI_COMMAND,
    () => runRemoteAction(context, provider, (folder) => remoteMemory.refreshReplica(context, folder))
  ));
  context.subscriptions.push(vscode.commands.registerCommand(
    CONFIGURE_SUMMARIES_FROM_OVERVIEW,
    () => runAndRefresh('llmWiki.configureAgentWikiMaintenance')
  ));
  context.subscriptions.push(vscode.commands.registerCommand(
    CONFIGURE_ANSWERS_FROM_OVERVIEW,
    () => runAndRefresh(productQueryConfig.COMMAND)
  ));
  context.subscriptions.push(vscode.commands.registerCommand(
    CONFIGURE_OTHER_PROJECTS_FROM_OVERVIEW,
    () => runAndRefresh('llmWiki.configurePersonalWikiLibrary')
  ));

  context.subscriptions.push(tree.onDidChangeVisibility((event) => {
    if (event.visible) provider.refresh();
  }));
  context.subscriptions.push(vscode.workspace.onDidChangeWorkspaceFolders(() => provider.refresh()));
  context.subscriptions.push(vscode.workspace.onDidChangeConfiguration((event) => {
    if (
      event.affectsConfiguration('llmWiki.workspaceDirectory')
      || event.affectsConfiguration('llmWiki.agentWikiMaintenanceEnabled')
    ) {
      provider.refresh();
    }
  }));

  provider.refresh();
  return provider;
}

module.exports = {
  CONNECT_PERSONAL_WIKI_COMMAND,
  OPEN_CHAT_COMMAND,
  REFRESH_COMMAND,
  REFRESH_PERSONAL_WIKI_COMMAND,
  VIEW_ID,
  WORKSPACE_ELIGIBLE_CONTEXT,
  LlmWikiOverviewProvider,
  registerProductView,
};