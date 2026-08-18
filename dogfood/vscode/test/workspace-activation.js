'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const activation = require('../workspace-activation');

const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'llm-wiki-workspace-opt-in-'));
const root = path.join(temp, '.wiki-lab');

try {
  assert.equal(activation.isCoreInitialized(root), false);
  assert.equal(activation.isWorkspaceEnabled(root), false);
  assert.throws(() => activation.enableWorkspace(root), /before the local Wiki store is initialized/);

  fs.mkdirSync(root, { recursive: true });
  fs.writeFileSync(path.join(root, 'config.json'), '{}\n');
  fs.writeFileSync(path.join(root, 'manifest.jsonl'), '');

  assert.equal(activation.isCoreInitialized(root), true);
  assert.equal(activation.isWorkspaceEnabled(root), false, 'core files alone must not imply user opt-in');

  const enabled = activation.enableWorkspace(root);
  assert.equal(enabled.format, activation.WORKSPACE_OPT_IN_FORMAT);
  assert.equal(enabled.enabled, true);
  assert.equal(activation.isWorkspaceEnabled(root), true);
  assert.equal(activation.readWorkspaceOptIn(root).enabled, true);

  assert.equal(activation.disableWorkspace(root), true);
  assert.equal(activation.isWorkspaceEnabled(root), false);
  assert.equal(activation.isCoreInitialized(root), true, 'disable must preserve Wiki data');
  assert.equal(activation.disableWorkspace(root), false);

  console.log('WORKSPACE-ACTIVATION PASS explicitOptIn=yes disablePreservesData=yes');
} finally {
  fs.rmSync(temp, { recursive: true, force: true });
}
