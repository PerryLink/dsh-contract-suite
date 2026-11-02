/**
 * Install smoke check used by CI: the published member versions must exist and
 * the suite manifest must agree with cordis.patch.yml. This is the only script
 * that touches the registry; the packaged quickstart stays offline.
 */
import { execFileSync } from 'node:child_process'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { readManifest } from '../src/members.mjs'

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const manifest = readManifest(root)

for (const member of manifest.members) {
  execFileSync('npm', ['view', `${member.id}@${member.version}`, 'version', '--registry=https://registry.npmjs.org'], {
    stdio: 'ignore',
  })
}
console.log(`suite ok: ${manifest.members.length} members`)
