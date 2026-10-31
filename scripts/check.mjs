import { readFileSync } from 'node:fs'
import { execFileSync } from 'node:child_process'

const pkg = JSON.parse(readFileSync('package.json', 'utf8'))
if (!pkg.dsh?.bundle?.patch) throw new Error('missing dsh.bundle.patch')
const patch = readFileSync(pkg.dsh.bundle.patch, 'utf8')
for (const [dep, version] of Object.entries(pkg.dependencies || {})) {
  if (!patch.includes(`id: ${dep}`) || !patch.includes(`name: ${dep}`)) {
    throw new Error(`patch missing member ${dep}`)
  }
  execFileSync('npm', ['view', `${dep}@${version}`, 'version', '--registry=https://registry.npmjs.org'], { stdio: 'ignore' })
}
console.log(`suite ok: ${Object.keys(pkg.dependencies || {}).length} members`)
