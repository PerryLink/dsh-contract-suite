import assert from 'node:assert/strict'
import { execFileSync } from 'node:child_process'
import { mkdir, mkdtemp, readFile, rm, writeFile } from 'node:fs/promises'
import { existsSync, readFileSync, readdirSync } from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { test } from 'node:test'
import { fileURLToPath } from 'node:url'
import { inspectMembers, readManifest } from '../src/members.mjs'

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const pkg = JSON.parse(readFileSync(path.join(root, 'package.json'), 'utf8'))

function walk(dir, out = []) {
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name)
    if (entry.isDirectory()) walk(full, out)
    else out.push(full)
  }
  return out
}

async function fixture(files) {
  const dir = await mkdtemp(path.join(os.tmpdir(), 'dsh-suite-fixture-'))
  for (const [rel, value] of Object.entries(files)) {
    const full = path.join(dir, rel)
    await mkdir(path.dirname(full), { recursive: true })
    await writeFile(full, typeof value === 'string' ? value : `${JSON.stringify(value, null, 2)}\n`)
  }
  return dir
}

test('manifest members match package dependencies', () => {
  const manifest = readManifest(root)
  const deps = Object.keys(pkg.dependencies || {}).sort()
  assert.deepEqual(manifest.members.map((member) => member.id).sort(), deps)
})

test('package ships samples, src and a complete offline demo', () => {
  for (const entry of ['samples', 'src']) assert.ok(pkg.files.includes(entry), `files[] lacks ${entry}`)
  const demo = pkg.dsh.demo
  assert.equal(demo.network, false)
  assert.deepEqual(demo.external, [])
  assert.ok(existsSync(path.join(root, demo.sample)))
  assert.ok(existsSync(path.join(root, demo.expect)))
  assert.ok(existsSync(path.join(root, demo.screenshot)))
})

test('quickstart --json matches the golden file', () => {
  const stdout = execFileSync(process.execPath, ['samples/quickstart/run.mjs', '--json'], { cwd: root, encoding: 'utf8' })
  const actual = JSON.parse(stdout)
  const expected = JSON.parse(readFileSync(path.join(root, pkg.dsh.demo.expect), 'utf8'))
  assert.deepEqual(actual, expected)
})

test('quickstart --check exits 0', () => {
  execFileSync(process.execPath, ['samples/quickstart/run.mjs', '--check'], { cwd: root, stdio: 'pipe' })
})

test('src and samples contain no network calls', () => {
  const network = /(^|[^\w.])(fetch\s*\(|axios|http\.request|https\.request|net\.connect|new WebSocket|undici)/
  for (const dir of ['src', 'samples']) {
    for (const file of walk(path.join(root, dir))) {
      assert.ok(!network.test(readFileSync(file, 'utf8')), `network call in ${path.relative(root, file)}`)
    }
  }
})

test('missing package.json raises E_SUITE_MANIFEST_MISSING', async () => {
  const dir = await fixture({})
  try {
    assert.throws(() => readManifest(dir), /E_SUITE_MANIFEST_MISSING/)
  } finally {
    await rm(dir, { recursive: true, force: true })
  }
})

test('patch without a dependency raises E_SUITE_PATCH_MISMATCH', async () => {
  const dir = await fixture({
    'package.json': {
      name: 'fixture-suite',
      version: '1.0.0',
      dsh: { bundle: { patch: './cordis.patch.yml' } },
      dependencies: { alpha: '1.0.0', beta: '1.0.0' },
    },
    'cordis.patch.yml': '- insert:\n    - id: alpha\n      name: alpha\n',
  })
  try {
    assert.throws(() => readManifest(dir), /E_SUITE_PATCH_MISMATCH/)
  } finally {
    await rm(dir, { recursive: true, force: true })
  }
})

test('installed member at another version raises E_SUITE_VERSION_MISMATCH', async () => {
  const dir = await fixture({
    'package.json': {
      name: 'fixture-suite',
      version: '1.0.0',
      dsh: { bundle: { patch: './cordis.patch.yml' } },
      dependencies: { alpha: '1.0.0' },
    },
    'cordis.patch.yml': '- insert:\n    - id: alpha\n      name: alpha\n',
    'node_modules/alpha/package.json': { name: 'alpha', version: '9.9.9' },
  })
  try {
    assert.throws(() => inspectMembers(dir), /E_SUITE_VERSION_MISMATCH/)
  } finally {
    await rm(dir, { recursive: true, force: true })
  }
})
