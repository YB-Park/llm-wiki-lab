'use strict';

const path = require('node:path');
const { execFile } = require('node:child_process');
const { promisify } = require('node:util');

const execFileAsync = promisify(execFile);

function isInside(parent, child) {
  const relative = path.relative(parent, child);
  return relative === '' || (!relative.startsWith(`..${path.sep}`) && relative !== '..' && !path.isAbsolute(relative));
}

async function gitOk(args, cwd) {
  try {
    await execFileAsync('git', args, {
      cwd,
      windowsHide: true,
      timeout: 10000,
      maxBuffer: 1024 * 1024,
    });
    return true;
  } catch (_) {
    return false;
  }
}

async function classifyGitSafety(workspacePath, wikiPath) {
  const inGit = await gitOk(['rev-parse', '--is-inside-work-tree'], workspacePath);
  if (!inGit) return 'NOT_GIT';

  if (!isInside(workspacePath, wikiPath)) return 'PROTECTED';

  let relative = path.relative(workspacePath, wikiPath);
  if (!relative) return 'UNPROTECTED';
  relative = relative.split(path.sep).join('/');
  const ignored = await gitOk(['check-ignore', '-q', '--', `${relative}/`], workspacePath);
  return ignored ? 'PROTECTED' : 'UNPROTECTED';
}

module.exports = { classifyGitSafety, isInside };
