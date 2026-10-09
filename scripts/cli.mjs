import { preflight, discover, execute, reconcile, evidence, finalize, exportEvidence } from './runtime.mjs';
import { redact } from '../server/lib.mjs';
const command = process.argv[2];
const grep = process.argv.find(a => a.startsWith('--grep='))?.split('=').slice(1).join('=') ?? '@smoke';
try {
  if (command === 'preflight') await preflight();
  else if (command === 'discover') discover(grep);
  else if (command === 'execute') execute(grep);
  else if (command === 'reconcile') await reconcile();
  else if (command === 'evidence') evidence();
  else if (command === 'finalize') finalize();
  else if (command === 'export') exportEvidence();
  else throw new Error('Unknown CLI action');
} catch (error) { console.error(redact(error.message)); process.exitCode = error.exitCode || 1; }
