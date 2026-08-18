'use strict';

const assert = require('node:assert/strict');
const { defaultPythonNames } = require('../python-runtime-policy');

assert.deepEqual(defaultPythonNames('win32'), ['python', 'py', 'python3']);
assert.deepEqual(defaultPythonNames('darwin'), ['python3', 'python']);
assert.deepEqual(defaultPythonNames('linux'), ['python3', 'python']);

console.log('PYTHON-RUNTIME-POLICY-TEST PASS win32=python,py,python3 unix=python3,python');
