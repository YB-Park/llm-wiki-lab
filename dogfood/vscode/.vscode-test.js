'use strict';

const path = require('node:path');
const { defineConfig } = require('@vscode/test-cli');

module.exports = defineConfig({
  label: 'runtime',
  files: 'test/integration/**/*.test.js',
  version: 'stable',
  workspaceFolder: path.resolve(__dirname, '../..'),
  extensionDevelopmentPath: __dirname,
  mocha: {
    ui: 'tdd',
    timeout: 30000,
    color: true,
  },
  launchArgs: [
    '--disable-extensions',
    '--disable-telemetry',
    '--disable-extension-update-checks'
  ],
});
