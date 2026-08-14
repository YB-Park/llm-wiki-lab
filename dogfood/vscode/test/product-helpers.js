'use strict';

const assert = require('node:assert/strict');
const path = require('node:path');
const {
  locatorForRow,
  parseIngestReceipt,
  resolveWorkspaceRelative,
  sha256,
  workspaceRelativePath,
} = require('../product-helpers');

const digest = 'a'.repeat(64);
const receipt = parseIngestReceipt(`INGEST source=src-abc object=obj-${digest} sha256=${digest} bytes=7 duplicateObject=no name="note.md"\n`);
assert.deepEqual(receipt, { sourceId: 'src-abc', sha256: digest });
assert.equal(parseIngestReceipt('CALIBRATION ingest=baseline'), undefined);

const root = path.resolve('/tmp/workspace');
assert.equal(workspaceRelativePath(root, path.join(root, 'docs', 'note.md')), 'docs/note.md');
assert.equal(workspaceRelativePath(root, path.resolve(root, '..', 'outside.md')), undefined);
assert.equal(resolveWorkspaceRelative(root, 'docs/note.md'), path.join(root, 'docs', 'note.md'));
assert.equal(resolveWorkspaceRelative(root, '../outside.md'), undefined);
assert.equal(resolveWorkspaceRelative(root, '/absolute/file.md'), undefined);
assert.equal(sha256(Buffer.from('abc')), 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad');

const map = {
  'src-one': { relativePath: 'one/README.md', sha256: digest },
  'src-two': { relativePath: 'two/README.md', sha256: 'b'.repeat(64) },
};
assert.deepEqual(
  locatorForRow(map, { source_ids: ['src-two', 'src-one'], sha256: digest }),
  { sourceId: 'src-one', relativePath: 'one/README.md', sha256: digest }
);
assert.equal(locatorForRow(map, { source_id: 'src-two', sha256: digest }), undefined);

console.log('product-helpers tests: PASS');
