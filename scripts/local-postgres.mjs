import EmbeddedPostgres from 'embedded-postgres';
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { randomBytes } from 'node:crypto';
import { resolve } from 'node:path';

// Development only. No OS service or account is installed. Bind to loopback.
const root = resolve(import.meta.dirname, '..');
const runtime = resolve(root, '.runtime');
mkdirSync(runtime, { recursive: true });
const secretPath = resolve(runtime, 'postgres-password');
const password = existsSync(secretPath) ? readFileSync(secretPath, 'utf8') : randomBytes(24).toString('hex');
if (!existsSync(secretPath)) writeFileSync(secretPath, password, { mode: 0o600 });
const databaseDir = resolve(runtime, 'postgres');
const pg = new EmbeddedPostgres({ databaseDir, user: 'soleline', password, port: 55432, persistent: true, authMethod: 'scram-sha-256', postgresFlags: ['-h', '127.0.0.1'], onLog: () => {}, onError: message => console.error(String(message)) });
if (!existsSync(resolve(databaseDir, 'PG_VERSION'))) await pg.initialise();
await pg.start();
const client = pg.getPgClient();
await client.connect();
const result = await client.query("SELECT 1 FROM pg_database WHERE datname = 'soleline'");
if (!result.rowCount) await client.query('CREATE DATABASE soleline');
await client.end();
writeFileSync(resolve(runtime, 'database-url'), `postgresql://soleline:${password}@127.0.0.1:55432/soleline`, { mode: 0o600 });
console.log('Local PostgreSQL ready on 127.0.0.1:55432. Connection URL is in .runtime/database-url (ignored by Git). Ctrl+C stops it.');
let closing = false;
async function stop() { if (closing) return; closing = true; await pg.stop(); process.exit(0); }
process.on('SIGINT', stop); process.on('SIGTERM', stop);
setInterval(() => {}, 60_000);
