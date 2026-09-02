'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const policy = require('../remote-project-policy');

function freshRoot() {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'llm-wiki-remote-attach-'));
  fs.writeFileSync(path.join(root, 'config.json'), '{}\n');
  fs.writeFileSync(path.join(root, 'manifest.jsonl'), '');
  fs.mkdirSync(path.join(root, 'raw'));
  fs.writeFileSync(path.join(root, 'workspace-opt-in.json'), '{}\n');
  return root;
}

{
  const root = freshRoot();
  try {
    assert.equal(policy.assertFreshLocalMemory(root), true);
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
}

{
  const root = freshRoot();
  try {
    fs.writeFileSync(path.join(root, '.writer.lock'), Buffer.from([0]));
    assert.equal(policy.assertFreshLocalMemory(root), true);
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
}

for (const mutate of [
  (root) => fs.writeFileSync(path.join(root, 'manifest.jsonl'), '{"event":"ingest"}\n'),
  (root) => fs.writeFileSync(path.join(root, 'raw', 'obj.txt'), 'remembered'),
  (root) => fs.writeFileSync(path.join(root, 'topics.json'), '{"topics":[]}\n'),
  (root) => fs.mkdirSync(path.join(root, 'human-knowledge')),
  (root) => fs.writeFileSync(path.join(root, 'agent-state.json'), '{}\n'),
]) {
  const root = freshRoot();
  try {
    mutate(root);
    assert.throws(() => policy.assertFreshLocalMemory(root), /remote_attach_requires_empty_local_memory/);
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
}

{
  const root = freshRoot();
  const outside = fs.mkdtempSync(path.join(os.tmpdir(), 'llm-wiki-remote-attach-outside-'));
  try {
    fs.rmSync(path.join(root, 'raw'), { recursive: true, force: true });
    fs.symlinkSync(outside, path.join(root, 'raw'), 'dir');
    assert.throws(() => policy.assertFreshLocalMemory(root), /remote_attach_requires_initialized_empty_local_memory/);
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
    fs.rmSync(outside, { recursive: true, force: true });
  }
}

{
  const root = freshRoot();
  const outside = path.join(root, 'outside-lock');
  try {
    fs.writeFileSync(outside, 'x');
    fs.symlinkSync(outside, path.join(root, '.writer.lock'));
    assert.throws(() => policy.assertFreshLocalMemory(root), /remote_attach_requires_initialized_empty_local_memory/);
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
}

{
  const root = freshRoot();
  try {
    fs.rmSync(path.join(root, 'workspace-opt-in.json'));
    assert.throws(() => policy.assertFreshLocalMemory(root), /remote_attach_requires_initialized_empty_local_memory/);
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
}

assert.equal(policy.authorityCacheKey('wiki-host'), policy.authorityCacheKey('wiki-host'));
assert.notEqual(policy.authorityCacheKey('wiki-host-a'), policy.authorityCacheKey('wiki-host-b'));
assert.match(policy.authorityCacheKey('wiki-host'), /^[0-9a-f]{24}$/);

console.log('REMOTE-PROJECT-POLICY PASS empty-only-attach=yes safe-writer-lock-retry=yes symlink-failclosed=yes authority-cache-key=opaque');
