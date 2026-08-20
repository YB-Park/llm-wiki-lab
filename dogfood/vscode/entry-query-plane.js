'use strict';

const base = require('./entry');
const { registerQueryPlane } = require('./query-plane');

async function activate(context) {
  await base.activate(context);
  registerQueryPlane(context);
}

function deactivate() {
  return base.deactivate();
}

module.exports = { activate, deactivate };
