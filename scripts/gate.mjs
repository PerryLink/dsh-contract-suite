#!/usr/bin/env node
/**
 * Release gate for dsh-contract-suite. Offline: no registry call, no network.
 *
 *   node scripts/gate.mjs
 *
 * It validates the suite manifest, the packaged quickstart, the documentation
 * blocks required by Package Standard v1, the recorded evidence, then runs the
 * quickstart golden check and `node --test`.
 */
import { execFileSync } from 'node:child_process'
import { existsSync, readFileSync, readdirSync, statSync } from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { inspectMembers, readManifest } from '../src/members.mjs'

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const fails = []
const checks = []

function check(name, fn) {
  try {
    fn()
    checks.push(name)
  } catch (error) {
    fails.push(`${name}: ${error instanceof Error ? error.message : String(error)}`)
  }
}

function read(rel) {
  return readFileSync(path.join(root, rel), 'utf8')
}

function walk(dir, out = []) {
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name)
    if (entry.isDirectory()) walk(full, out)
    else out.push(full)
  }
  return out
}

const pkg = JSON.parse(read('package.json'))
const readmeZh = read('README-zh.md')
const trouble = read('TROUBLESHOOTING.md')

check('manifest members match dependencies', () => {
  const manifest = readManifest(root)
  if (manifest.members.length !== Object.keys(pkg.dependencies || {}).length) throw new Error('member count differs')
  inspectMembers(root)
})

check('package files ship samples and src', () => {
  for (const entry of ['samples', 'src', 'TROUBLESHOOTING.md', 'screenshots.json']) {
    if (!pkg.files?.includes(entry)) throw new Error(`files[] lacks ${entry}`)
  }
})

check('dsh.demo is complete and offline', () => {
  const demo = pkg.dsh?.demo
  if (!demo) throw new Error('missing dsh.demo')
  for (const key of ['sample', 'prompt', 'expect', 'screenshot']) {
    if (!demo[key] || typeof demo[key] !== 'string') throw new Error(`dsh.demo.${key} missing`)
  }
  if (demo.network !== false) throw new Error('dsh.demo.network must be false')
  if (!Array.isArray(demo.external) || demo.external.length !== 0) throw new Error('dsh.demo.external must be []')
  if (!Array.isArray(demo.reads) || demo.reads.length === 0) throw new Error('dsh.demo.reads missing')
  if (!Array.isArray(demo.writes)) throw new Error('dsh.demo.writes must be an array')
  for (const rel of [demo.sample, demo.expect, demo.screenshot]) {
    if (!existsSync(path.join(root, rel))) throw new Error(`missing ${rel}`)
  }
})

check('quickstart input is synthetic and <= 500 KB', () => {
  const inputDir = path.join(root, 'samples/quickstart/input')
  if (!existsSync(inputDir)) throw new Error('missing samples/quickstart/input')
  const files = walk(inputDir)
  if (files.length === 0) throw new Error('input directory is empty')
  const bytes = files.reduce((sum, file) => sum + statSync(file).size, 0)
  if (bytes > 500 * 1024) throw new Error(`input is ${bytes} bytes, over 500 KB`)
})

check('README-zh has the eight blocks and demo prompt', () => {
  const required = ['一句话', '适合', '不适合', '输入', '输出', '示例', '权限', 'FAQ', '外部系统']
  for (const word of required) {
    if (!readmeZh.includes(word)) throw new Error(`README-zh lacks ${word}`)
  }
  if (!readmeZh.includes(`\`${pkg.version}\``)) throw new Error(`README-zh lacks version ${pkg.version}`)
  if (!readmeZh.includes(pkg.dsh.demo.prompt.slice(0, 12))) throw new Error('README-zh lacks the demo prompt')
  for (const label of ['读：', '写：', '联网：', '外部系统：']) {
    if (!readmeZh.includes(label)) throw new Error(`README-zh lacks permission line ${label}`)
  }
})

check('TROUBLESHOOTING lists at least three E_ codes', () => {
  const codes = new Set(trouble.match(/E_[A-Z][A-Z0-9_]{3,}/g) || [])
  if (codes.size < 3) throw new Error(`only ${codes.size} codes`)
  for (const label of ['**症状**', '**原因**', '**动作**']) {
    const count = (trouble.match(new RegExp(label.replace(/\*/g, '\\*'), 'g')) || []).length
    if (count < 3) throw new Error(`${label} appears ${count} times, need 3`)
  }
})

check('source and sample contain no network calls', () => {
  const network = /(^|[^\w.])(fetch\s*\(|axios|http\.request|https\.request|net\.connect|new WebSocket|undici)/
  for (const file of [...walk(path.join(root, 'src')), ...walk(path.join(root, 'samples'))]) {
    if (network.test(readFileSync(file, 'utf8'))) throw new Error(`network call in ${path.relative(root, file)}`)
  }
})

check('screenshots.json records command, date and hash', () => {
  const entries = JSON.parse(read('screenshots.json'))
  const quickstart = entries.find((entry) => entry.kind === 'quickstart')
  if (!quickstart) throw new Error('no quickstart screenshot entry')
  for (const key of ['path', 'command', 'run_at', 'output_sha256']) {
    if (!quickstart[key]) throw new Error(`quickstart entry lacks ${key}`)
  }
  if (!existsSync(path.join(root, quickstart.path))) throw new Error('screenshot file missing')
})

check('ACCEPTANCE.csv has an evidence row', () => {
  const lines = read('ACCEPTANCE.csv').trim().split('\n')
  if (!lines[0].includes('evidence_sha256')) throw new Error('header lacks evidence_sha256')
  const rows = lines.slice(1).filter((line) => line.trim() && !/^,|false$/i.test(line))
  if (rows.length === 0) throw new Error('no counted pass row')
})

check('quickstart golden check', () => {
  execFileSync(process.execPath, ['samples/quickstart/run.mjs', '--check'], { cwd: root, stdio: 'pipe' })
})

check('node --test', () => {
  try {
    execFileSync(process.execPath, ['--test', 'test/suite.test.mjs'], { cwd: root, stdio: 'pipe' })
  } catch (error) {
    const output = `${error.stdout || ''}${error.stderr || ''}`.trim().split('\n').slice(-8).join('\n')
    throw new Error(`tests failed\n${output}`)
  }
})

if (fails.length > 0) {
  console.error(`gate failed: ${fails.length} check(s)`)
  for (const fail of fails) console.error(`  - ${fail}`)
  process.exit(1)
}
console.log(`gate ok: ${checks.length} checks`)
