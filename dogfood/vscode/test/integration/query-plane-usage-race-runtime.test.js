'use strict';

const assert = require('node:assert/strict');
const queryPlane = require('../../query-plane');

function delayedStateStore(delayMs = 25) {
  const values = new Map();
  return {
    get(key, fallback) { return values.has(key) ? values.get(key) : fallback; },
    async update(key, value) {
      await new Promise((resolve) => setTimeout(resolve, delayMs));
      if (value === undefined) values.delete(key); else values.set(key, value);
    },
  };
}

function folder(name) {
  return { uri: { toString: () => `file:///usage-race/${name}` } };
}

suite('LLM Wiki Query Plane usage reservation', () => {
  test('concurrent reservations cannot exceed the user-chosen daily call cap', async () => {
    const context = { workspaceState: delayedStateStore() };
    const target = folder('cap-one');
    const grant = { dailyCallLimit: 1, maxAiCredits: 1 };

    const results = await Promise.all([
      queryPlane.reserveQueryCall(context, target, grant),
      queryPlane.reserveQueryCall(context, target, grant),
    ]);

    assert.equal(results.filter((row) => row.allowed).length, 1);
    assert.equal(results.filter((row) => !row.allowed).length, 1);
    assert.equal(queryPlane.queryUsage(context, target).reservedCalls, 1);
  });

  test('serialization preserves exact cap under a larger concurrent burst', async () => {
    const context = { workspaceState: delayedStateStore(10) };
    const target = folder('cap-two');
    const grant = { dailyCallLimit: 2, maxAiCredits: 3 };

    const results = await Promise.all(Array.from({ length: 5 }, () => (
      queryPlane.reserveQueryCall(context, target, grant)
    )));

    assert.equal(results.filter((row) => row.allowed).length, 2);
    assert.equal(results.filter((row) => !row.allowed).length, 3);
    assert.equal(queryPlane.queryUsage(context, target).reservedCalls, 2);
    assert.deepEqual(
      results.filter((row) => row.allowed).map((row) => row.reservedCalls).sort((a, b) => a - b),
      [1, 2]
    );
  });
});
