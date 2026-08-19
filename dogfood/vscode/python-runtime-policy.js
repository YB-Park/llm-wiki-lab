'use strict';

function defaultPythonNames(platform) {
  return platform === 'win32'
    ? ['python', 'py', 'python3']
    : ['python3', 'python'];
}

module.exports = { defaultPythonNames };
