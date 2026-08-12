const vscode = require('vscode');

const PREFLIGHT_PROMPT = `This is a non-scored infrastructure test for a synthetic knowledge-maintenance harness.
Do not use tools or outside knowledge.

Synthetic evidence:
- Note P1: Project Zephyr uses a Cedar datastore and cache TTL of 12 minutes.
- Note P2: On 2026-07-01, Zephyr changed its cache TTL from 12 minutes to 7 minutes. Cedar did not change.
- Note P3: The exact export marker is ZPHR9. This marker is unrelated to the cache change.

Return JSON only, exactly in this shape:
{
  "current_store": "...",
  "current_cache_ttl_minutes": 0,
  "historical_cache_ttl_minutes": 0,
  "export_marker": "...",
  "change_kind": "temporal_change"
}`;

function modelLine(model) {
  return [
    `name=${model.name}`,
    `id=${model.id}`,
    `family=${model.family}`,
    `version=${model.version}`,
    `maxIn=${model.maxInputTokens}`,
  ].join(' ');
}

function extractJsonObject(text) {
  const stripped = text.trim().replace(/^```(?:json)?\s*/i, '').replace(/\s*```$/, '');
  const start = stripped.indexOf('{');
  const end = stripped.lastIndexOf('}');
  if (start < 0 || end < start) {
    throw new Error('response does not contain a JSON object');
  }
  return JSON.parse(stripped.slice(start, end + 1));
}

function validateAnswer(payload) {
  const expected = {
    current_store: 'Cedar',
    current_cache_ttl_minutes: 7,
    historical_cache_ttl_minutes: 12,
    export_marker: 'ZPHR9',
    change_kind: 'temporal_change',
  };
  const mismatches = [];
  for (const [key, value] of Object.entries(expected)) {
    if (payload[key] !== value) {
      mismatches.push(`${key}:${JSON.stringify(payload[key])}`);
    }
  }
  return mismatches;
}

async function selectLuna(models) {
  const candidates = models.filter((model) => {
    const haystack = `${model.name} ${model.id} ${model.family} ${model.version}`.toLowerCase();
    return haystack.includes('luna');
  });

  if (candidates.length === 0) {
    return undefined;
  }
  if (candidates.length === 1) {
    return candidates[0];
  }

  const picked = await vscode.window.showQuickPick(
    candidates.map((model) => ({
      label: model.name,
      description: model.id,
      detail: `family=${model.family} version=${model.version} maxInputTokens=${model.maxInputTokens}`,
      model,
    })),
    { title: 'Select the Luna model for the non-scored E007 preflight' }
  );
  return picked && picked.model;
}

async function readTextResponse(response) {
  let text = '';
  for await (const chunk of response.text) {
    text += chunk;
  }
  return text;
}

function activate(context) {
  const output = vscode.window.createOutputChannel('LLM Wiki Lab E007');
  context.subscriptions.push(output);

  context.subscriptions.push(
    vscode.commands.registerCommand('llmWikiLab.e007.listCopilotModels', async () => {
      output.clear();
      output.show(true);
      try {
        const models = await vscode.lm.selectChatModels({ vendor: 'copilot' });
        output.appendLine('COPILOT-MODEL-CATALOG-v0');
        output.appendLine(`count=${models.length}`);
        for (const model of models) {
          output.appendLine(modelLine(model));
        }
      } catch (error) {
        output.appendLine('COPILOT-MODEL-CATALOG-v0');
        output.appendLine(`ERROR ${error && error.message ? error.message : String(error)}`);
      }
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('llmWikiLab.e007.preflightLuna', async () => {
      output.clear();
      output.show(true);

      try {
        const models = await vscode.lm.selectChatModels({ vendor: 'copilot' });
        const model = await selectLuna(models);
        if (!model) {
          output.appendLine('VSCODE-PREFLIGHT-HANDOFF-v0');
          output.appendLine('status=NO_LUNA_MODEL');
          output.appendLine(`copilot_models=${models.length}`);
          output.appendLine('Run "LLM Wiki Lab: List Copilot Models" and transfer only the Luna-looking model line if present.');
          return;
        }

        const message = vscode.LanguageModelChatMessage.User(PREFLIGHT_PROMPT);
        const inputTokens = await model.countTokens(message);
        const started = Date.now();
        const response = await model.sendRequest(
          [message],
          {
            justification: 'Run the user-initiated non-scored E007 synthetic model preflight. No workspace or corporate data is sent.',
            tools: [],
          },
          new vscode.CancellationTokenSource().token
        );
        const text = await readTextResponse(response);
        const wallSeconds = (Date.now() - started) / 1000;
        const outputTokens = await model.countTokens(text);

        let status = 'PASS';
        let mismatchText = '-';
        try {
          const payload = extractJsonObject(text);
          const mismatches = validateAnswer(payload);
          if (mismatches.length) {
            status = 'CONTRACT_FAIL';
            mismatchText = mismatches.join(',');
          }
        } catch (error) {
          status = 'PARSE_FAIL';
          mismatchText = error && error.message ? error.message : String(error);
        }

        output.appendLine('VSCODE-PREFLIGHT-HANDOFF-v0');
        output.appendLine(`status=${status} ${modelLine(model)}`);
        output.appendLine(`prompt_tokens=${inputTokens} response_tokens=${outputTokens} wall_s=${wallSeconds.toFixed(2)}`);
        output.appendLine(`mismatch=${mismatchText}`);
        output.appendLine('billing=not_exposed_by_vscode_lm_api');
      } catch (error) {
        output.appendLine('VSCODE-PREFLIGHT-HANDOFF-v0');
        if (error instanceof vscode.LanguageModelError) {
          output.appendLine(`status=LM_ERROR code=${error.code || '?'} message=${error.message}`);
        } else {
          output.appendLine(`status=ERROR message=${error && error.message ? error.message : String(error)}`);
        }
      }
    })
  );
}

function deactivate() {}

module.exports = { activate, deactivate };
