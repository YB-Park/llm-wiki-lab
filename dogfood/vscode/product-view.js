'use strict';

const vscode = require('vscode');
const memoryRead = require('./memory-read-service');
const personalLibrary = require('./personal-wiki-library');
const { queryGrant } = require('./query-plane');
const workspaceActivation = require('./workspace-activation');

const VIEW_ID = 'llmWiki.overview';
const WORKSPACE_ELIGIBLE_CONTEXT = 'llmWiki.workspaceEligible';
const REFRESH_COMMAND = 'llmWiki.refreshOverview';
const OPEN_CHAT_COMMAND = 'llmWiki.openAgentChat';
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

  return {
    workspaceEnabled,
    maintenanceOn,
    queryOn: Boolean(query),
    libraryAccess,
    libraryCatalogReady,
    stores,
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
    await vscode.commands.executeCommand('setContext', WORKSPACE_ELIGIBLE_CONTEXT, Boolean(firstEligibleFolder()));
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
        tooltip: 'Available only when this project is explicitly named in Agent chat and this workspace has the required access.',
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
      otherProjectTooltip = 'No other project memories are registered on this machine.';
      otherProjectIcon = new vscode.ThemeIcon('folder');
    } else if (!state.libraryAccess) {
      otherProjectDescription = `${state.stores.length} added · access off`;
      otherProjectTooltip = 'Other project memories are registered, but this workspace is not allowed to use them.';
      otherProjectIcon = new vscode.ThemeIcon('circle-slash');
    } else if (!state.queryOn) {
      otherProjectDescription = `${state.stores.length} added · AI answers off`;
      otherProjectTooltip = 'Other project access is allowed, but AI-assisted memory answers are off. External project consultation remains unavailable.';
      otherProjectIcon = new vscode.ThemeIcon('circle-slash');
    } else {
      otherProjectDescription = `${state.stores.length} added · ready`;
      otherProjectTooltip = 'Explicitly named other project memories can be consulted read-only from Agent chat.';
      otherProjectIcon = new vscode.ThemeIcon('check');
    }

    return [
      node('Project memory', {
        description: 'On',
        tooltip: 'This workspace is allowed to use its local project memory in Agent conversations.',
        iconPath: statusIcon(true),
      }),
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
          ? 'Bounded saved memory may be sent to GitHub Copilot for read-only memory reasoning under this workspace grant. Click to change access.'
          : 'AI-assisted memory reasoning is off. Deterministic local memory search/read can still be used by the Agent. Click to configure it.',
        iconPath: statusIcon(state.queryOn),
        command: { command: CONFIGURE_ANSWERS_FROM_OVERVIEW, title: 'Configure AI-assisted Memory Answers' },
      }),
      node('Other project memories', {
        description: otherProjectDescription,
        tooltip: `${otherProjectTooltip} Click to manage other project memories; use the disclosure arrow to inspect registered names.`,
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

function registerProductView(context) {
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
    CONFIGURE_SUMMARIES_FROM_OVERVIEW,
    () => runAndRefresh('llmWiki.configureAgentWikiMaintenance')
  ));
  context.subscriptions.push(vscode.commands.registerCommand(
    CONFIGURE_ANSWERS_FROM_OVERVIEW,
    () => runAndRefresh('llmWiki.configureQueryPlane')
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
  OPEN_CHAT_COMMAND,
  REFRESH_COMMAND,
  VIEW_ID,
  WORKSPACE_ELIGIBLE_CONTEXT,
  LlmWikiOverviewProvider,
  registerProductView,
};
