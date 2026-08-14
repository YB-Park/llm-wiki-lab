'use strict';

const fs = require('node:fs');
const path = require('node:path');

const extensionRoot = path.resolve(__dirname, '..');
const dogfoodRoot = path.resolve(extensionRoot, '..');
const bundleRoot = path.join(extensionRoot, 'python');
const bundlePackage = path.join(bundleRoot, 'dogfood');
const sourcePackage = path.join(dogfoodRoot, 'llm_wiki');

fs.rmSync(bundleRoot, { recursive: true, force: true });
fs.mkdirSync(bundlePackage, { recursive: true });
fs.copyFileSync(path.join(dogfoodRoot, '__init__.py'), path.join(bundlePackage, '__init__.py'));
fs.cpSync(sourcePackage, path.join(bundlePackage, 'llm_wiki'), {
  recursive: true,
  filter: (source) => {
    const name = path.basename(source);
    return name !== '__pycache__' && !name.endsWith('.pyc');
  },
});

const cli = path.join(bundlePackage, 'llm_wiki', 'cli.py');
if (!fs.existsSync(cli)) {
  throw new Error(`bundled core missing expected CLI: ${cli}`);
}

console.log('VSIX-BUNDLE PASS sourceOfTruth=dogfood/llm_wiki generated=dogfood/vscode/python');
