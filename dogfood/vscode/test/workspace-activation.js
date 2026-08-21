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

  const first = activation.enableWorkspace(root);
  assert.equal(first.format, activation.WORKSPACE_OPT_IN_FORMAT);
  assert.equal(first.enabled, true);
  assert.match(first.epoch_id, activation.EPOCH_ID_RE, 'workspace authority epoch must be a random UUID');
  assert.equal(activation.isWorkspaceEnabled(root), true);
  assert.equal(activation.readWorkspaceOptIn(root).enabled, true);
  if (process.platform !== 'win32') {
    assert.equal(fs.statSync(activation.markerPath(root)).mode & 0o777, 0o600, 'workspace opt-in marker must remain private');
  }

  assert.equal(activation.disableWorkspace(root), true);
  assert.equal(activation.isWorkspaceEnabled(root), false);
  assert.equal(activation.isCoreInitialized(root), true, 'disable must preserve Wiki data');

  const second = activation.enableWorkspace(root);
  assert.match(second.epoch_id, activation.EPOCH_ID_RE);
  assert.notEqual(
    activation.workspaceEpoch(first),
    activation.workspaceEpoch(second),
    'disable/re-enable must mint a fresh authority epoch even inside one timestamp tick'
  );
  assert.equal(activation.disableWorkspace(root), true);
  assert.equal(activation.disableWorkspace(root), false);

  console.log('WORKSPACE-ACTIVATION PASS explicitOptIn=yes privateMarker=yes freshEpoch=yes disablePreservesData=yes');
} finally {
  fs.rmSync(temp, { recursive: true, force: true });
}
