'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { execFileSync } = require('node:child_process');
const { classifyGitSafety, isInside } = require('../git-safety');

function gitInit(root) {
  execFileSync('git', ['init', '-q'], { cwd: root, stdio: 'ignore' });
}

async function main() {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'llm-wiki-git-safety-'));
  try {
    const plain = path.join(root, 'plain');
    fs.mkdirSync(plain);
    assert.equal(await classifyGitSafety(plain, path.join(plain, '.wiki-lab')), 'NOT_GIT');

    const unprotected = path.join(root, 'unprotected');
    fs.mkdirSync(unprotected);
    gitInit(unprotected);
    assert.equal(await classifyGitSafety(unprotected, path.join(unprotected, '.wiki-lab')), 'UNPROTECTED');

    const protectedByIgnore = path.join(root, 'protected-ignore');
    fs.mkdirSync(protectedByIgnore);
    gitInit(protectedByIgnore);
    fs.writeFileSync(path.join(protectedByIgnore, '.gitignore'), '.wiki-lab/\n', 'utf8');
    assert.equal(await classifyGitSafety(protectedByIgnore, path.join(protectedByIgnore, '.wiki-lab')), 'PROTECTED');

    const protectedByLocalExclude = path.join(root, 'protected-exclude');
    fs.mkdirSync(protectedByLocalExclude);
    gitInit(protectedByLocalExclude);
    fs.appendFileSync(path.join(protectedByLocalExclude, '.git', 'info', 'exclude'), '\n.wiki-lab/\n', 'utf8');
    assert.equal(await classifyGitSafety(protectedByLocalExclude, path.join(protectedByLocalExclude, '.wiki-lab')), 'PROTECTED');

    const externalStore = path.join(root, 'external-store');
    fs.mkdirSync(externalStore);
    assert.equal(await classifyGitSafety(unprotected, externalStore), 'PROTECTED');

    assert.equal(isInside(unprotected, path.join(unprotected, '.wiki-lab')), true);
    assert.equal(isInside(unprotected, externalStore), false);

    console.log('GIT-SAFETY-TEST PASS cases=5 modelCalls=0 contentPrinted=no pathsPrinted=no');
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
}

main().catch((error) => {
  console.error(`GIT-SAFETY-TEST FAIL type=${error && error.name ? error.name : 'Error'}`);
  process.exitCode = 1;
});
