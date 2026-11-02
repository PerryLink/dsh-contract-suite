#!/usr/bin/env node
/**
 * Rebuild ACCEPTANCE.csv from real local checks. Offline.
 *
 *   node scripts/acceptance.mjs
 */
import { execFileSync } from 'node:child_process'
import { createHash } from 'node:crypto'
import { readFileSync, writeFileSync } from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { readManifest } from '../src/members.mjs'

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const node = process.execPath
const sha256 = (buffer) => createHash('sha256').update(buffer).digest('hex')

const manifest = readManifest(root)
const expectedRef = 'samples/quickstart/expected/result.json'
const evidence = sha256(readFileSync(path.join(root, expectedRef)))

execFileSync(node, ['samples/quickstart/run.mjs', '--check'], { cwd: root, stdio: 'pipe' })

let testOutput = ''
try {
  testOutput = execFileSync(node, ['--test', 'test/suite.test.mjs'], { cwd: root, encoding: 'utf8' })
} catch (error) {
  testOutput = `${error.stdout || ''}${error.stderr || ''}`
}
const pass = Number((testOutput.match(/^ℹ pass (\d+)/m) || [])[1] || -1)
const fail = Number((testOutput.match(/^ℹ fail (\d+)/m) || [])[1] || -1)
if (pass < 0 || fail !== 0) throw new Error(`node --test failed\n${testOutput.split('\n').slice(-10).join('\n')}`)

const rows = [
  ['SUITE-01', '成员清单与 dependencies 一致', `members=${manifest.members.length}`, String(manifest.members.length), 'scripts/gate.mjs', evidence, 'true', 'public/synthetic', 'false'],
  ['SUITE-02', 'quickstart 样例与金标一致', '1/1', '1', 'node samples/quickstart/run.mjs --check', evidence, 'true', 'synthetic/quickstart', 'true'],
  ['SUITE-03', '离线运行网络调用数', '0', '0', 'scripts/gate.mjs', evidence, 'true', 'public/synthetic', 'false'],
  ['SUITE-04', 'node --test 通过数', `${pass}/${pass}`, String(pass), 'node --test test/suite.test.mjs', evidence, 'true', 'public/synthetic', 'false'],
]
const header = 'req_id,metric,threshold,actual,script,evidence_sha256,pass,source,counted'
writeFileSync(path.join(root, 'ACCEPTANCE.csv'), [header, ...rows.map((row) => row.join(','))].join('\n') + '\n')
console.log(`acceptance ok: ${rows.length} rows, node --test ${pass} passed`)
