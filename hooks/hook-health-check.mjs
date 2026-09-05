import fs from 'fs';
import path from 'path';
import { createRequire } from 'module';
import { fileURLToPath } from 'url';

const require = createRequire(import.meta.url);
const dispatch = require('./dispatch.js');
const hooksDir = path.dirname(fileURLToPath(import.meta.url));
const settingsPath = path.join(hooksDir, '..', 'settings.json');
const registeredTargets = dispatch.registeredTargets;

function main() {
  const issues = [];
  let manifest;
  let settings;
  try {
    manifest = dispatch.loadManifest();
    settings = JSON.parse(fs.readFileSync(settingsPath, 'utf8'));
  } catch (error) {
    console.error(`[HOOK HEALTH] configuration unreadable: ${error.message}`);
    return;
  }

  const registered = registeredTargets(settings);
  const declared = new Set(Object.keys(manifest.targets || {}));
  for (const target of registered) {
    if (!declared.has(target)) issues.push(`${target}:missing-manifest`);
  }
  for (const target of declared) {
    if (!registered.has(target)) issues.push(`${target}:not-registered`);
  }
  for (const target of registered) {
    const inspected = dispatch.inspectTarget(target);
    if (!inspected.applicable) continue;
    if (inspected.metadata?.implementation_status === 'pending') {
      issues.push(`${target}:pending`);
    } else if (inspected.error) {
      issues.push(`${target}:unresolved`);
    }
  }

  if (issues.length > 0) {
    console.error(`[HOOK HEALTH] ${issues.length} issue(s): ${issues.join(', ')}`);
  }
}

main();
