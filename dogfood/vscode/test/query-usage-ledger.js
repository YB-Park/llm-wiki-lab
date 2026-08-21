'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawn } = require('node:child_process');
const ledger = require('../query-usage-ledger');

function context(root) {
  return { globalStorageUri: { fsPath: root } };
}

function folder(uri) {
  return { uri: { toString: () => uri } };
}

function childReservation(modulePath, storageRoot, uri, day, limit) {
  const script = [
    "const ledger=require(process.argv[1]);",
    "const context={globalStorageUri:{fsPath:process.argv[2]}};",
    "const folder={uri:{toString:()=>process.argv[3]}};",
    "const row=ledger.reserveUsage(context,folder,process.argv[4],Number(process.argv[5]),0);",
    "process.stdout.write(JSON.stringify(row));",
  ].join('');
  return new Promise((resolve, reject) => {
    const child = spawn(process.execPath, ['-e', script, modulePath, storageRoot, uri, day, String(limit)], {
      stdio: ['ignore', 'pipe', 'pipe'],
      windowsHide: true,
    });
    const stdout = [];
    const stderr = [];
    child.stdout.on('data', (chunk) => stdout.push(chunk));
    child.stderr.on('data', (chunk) => stderr.push(chunk));
    child.on('error', reject);
    child.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(Buffer.concat(stderr).toString('utf8') || `child_exit_${code}`));
        return;
      }
      resolve(JSON.parse(Buffer.concat(stdout).toString('utf8')));
    });
  });
}

(async () => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'llm-wiki-query-usage-'));
  try {
    const modulePath = path.resolve(__dirname, '..', 'query-usage-ledger.js');
    const uri = 'file:///private/workspace/with-sensitive-name';
    const day = '2026-08-21';
    const ctx = context(tmp);
    const target = folder(uri);

    const directory = ledger.usageDirectory(ctx, target, day);
    assert.ok(directory.startsWith(tmp));
    assert.equal(directory.includes('private'), false, 'workspace URI must not appear in usage storage paths');
    assert.equal(directory.includes('sensitive-name'), false, 'workspace names must remain hash-only');
    assert.equal(fs.existsSync(directory), false, 'read-only path calculation must not create state');
    assert.deepEqual(ledger.readUsage(ctx, target, day), { day, reservedCalls: 0 });
    assert.equal(fs.existsSync(directory), false, 'readUsage must remain a zero-state-change diagnostic');

    const burst = await Promise.all(Array.from({ length: 9 }, () => (
      childReservation(modulePath, tmp, uri, day, 3)
    )));
    assert.equal(burst.filter((row) => row.allowed).length, 3, 'cross-process burst must not exceed cap=3');
    assert.equal(burst.filter((row) => !row.allowed).length, 6);
    assert.equal(ledger.readUsage(ctx, target, day).reservedCalls, 3);

    const legacyUri = 'file:///legacy-workspace';
    const legacyTarget = folder(legacyUri);
    const legacyDay = '2026-08-22';
    const blocked = ledger.reserveUsage(ctx, legacyTarget, legacyDay, 2, 2);
    assert.equal(blocked.allowed, false, 'legacy 0.1.17 usage must not be refunded during upgrade');
    assert.equal(blocked.reservedCalls, 2);
    const raised = ledger.reserveUsage(ctx, legacyTarget, legacyDay, 3, 2);
    assert.equal(raised.allowed, true);
    assert.equal(raised.reservedCalls, 3);

    const crashUri = 'file:///crash-conservative';
    const crashTarget = folder(crashUri);
    const crashDay = '2026-08-23';
    const crashDir = ledger.usageDirectory(ctx, crashTarget, crashDay);
    fs.mkdirSync(crashDir, { recursive: true });
    fs.writeFileSync(path.join(crashDir, 'slot-001.json'), '');
    assert.equal(
      ledger.readUsage(ctx, crashTarget, crashDay).reservedCalls,
      1,
      'a slot claimed before a crash must remain conservatively counted'
    );

    assert.throws(
      () => ledger.reserveUsage({ globalStorageUri: { fsPath: 'relative' } }, target, day, 1, 0),
      /query_usage_storage_unavailable/
    );

    console.log('query-usage-ledger tests: PASS crossProcessCap=yes legacyFloor=yes crashConservative=yes privacyHash=yes');
  } finally {
    fs.rmSync(tmp, { recursive: true, force: true });
  }
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
