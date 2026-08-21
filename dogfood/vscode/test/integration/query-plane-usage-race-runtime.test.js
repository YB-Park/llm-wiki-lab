'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const queryPlane = require('../../query-plane');

function stateStore(initial = new Map()) {
  const values = new Map(initial);
  return {
    get(key, fallback) { return values.has(key) ? values.get(key) : fallback; },
    async update(key, value) {
      if (value === undefined) values.delete(key); else values.set(key, value);
    },
  };
}

function context(storageRoot, initial = new Map()) {
  return {
    globalStorageUri: { fsPath: storageRoot },
    workspaceState: stateStore(initial),
  };
}

function folder(name) {
  return { uri: { toString: () => `file:///usage-race/${name}` } };
}

suite('LLM Wiki Query Plane usage reservation', () => {
  let tmp;

  setup(() => {
    tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'llm-wiki-query-usage-runtime-'));
  });

  teardown(() => {
    fs.rmSync(tmp, { recursive: true, force: true });
  });

  test('independent extension contexts sharing global storage cannot exceed cap', async () => {
    const target = folder('cap-one');
    const grant = { dailyCallLimit: 1, maxAiCredits: 1 };
    const left = context(tmp);
    const right = context(tmp);

    const results = await Promise.all([
      queryPlane.reserveQueryCall(left, target, grant),
      queryPlane.reserveQueryCall(right, target, grant),
    ]);

    assert.equal(results.filter((row) => row.allowed).length, 1);
    assert.equal(results.filter((row) => !row.allowed).length, 1);
    assert.equal(queryPlane.queryUsage(left, target).reservedCalls, 1);
    assert.equal(queryPlane.queryUsage(right, target).reservedCalls, 1);
  });

  test('durable reservation preserves exact cap under a larger concurrent burst', async () => {
    const target = folder('cap-two');
    const grant = { dailyCallLimit: 2, maxAiCredits: 3 };
    const contexts = Array.from({ length: 5 }, () => context(tmp));

    const results = await Promise.all(contexts.map((item) => (
      queryPlane.reserveQueryCall(item, target, grant)
    )));

    assert.equal(results.filter((row) => row.allowed).length, 2);
    assert.equal(results.filter((row) => !row.allowed).length, 3);
    assert.equal(queryPlane.queryUsage(contexts[0], target).reservedCalls, 2);
  });

  test('legacy 0.1.17 workspace-state usage is a conservative upgrade floor', async () => {
    const target = folder('legacy');
    const day = queryPlane.queryUsage(context(tmp), target).day;
    const legacy = new Map([[queryPlane.usageKey(target, day), { reservedCalls: 2 }]]);
    const ctx = context(tmp, legacy);

    const blocked = await queryPlane.reserveQueryCall(ctx, target, { dailyCallLimit: 2, maxAiCredits: 1 });
    assert.equal(blocked.allowed, false);
    assert.equal(blocked.reservedCalls, 2);
    assert.equal(queryPlane.queryUsage(ctx, target).reservedCalls, 2);
  });

  test('missing durable usage storage blocks the model-attempt guard fail closed', async () => {
    const target = folder('no-storage');
    const ctx = { workspaceState: stateStore() };
    const result = await queryPlane.reserveQueryCall(ctx, target, { dailyCallLimit: 1, maxAiCredits: 1 });
    assert.equal(result.allowed, false);
    assert.equal(result.guardUnavailable, true);
    assert.match(String(result.failure && result.failure.message), /query_usage_storage_unavailable/);
  });
});
