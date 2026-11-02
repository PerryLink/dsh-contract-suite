#!/usr/bin/env node
/**
 * dsh-contract-suite quickstart — offline demonstration of what a one-command
 * install gives you: every member named in `cordis.patch.yml` resolves, and the
 * synthetic profile dump has one enabled row per member at the pinned version.
 *
 *   node samples/quickstart/run.mjs            # human-readable + golden check
 *   node samples/quickstart/run.mjs --json     # golden result on stdout
 *   node samples/quickstart/run.mjs --check    # same as default, explicit
 *
 * The golden file `expected/result.json` is the stdout of `--json`, so it is a
 * real run, not hand-written. This script never touches the network and writes
 * no files.
 */
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { inspectMembers, readProfile, SuiteError } from '../../src/members.mjs'

const here = path.dirname(fileURLToPath(import.meta.url))
const root = path.resolve(here, '..', '..')
const pkg = JSON.parse(readFileSync(path.join(root, 'package.json'), 'utf8'))
const demo = pkg.dsh?.demo || {}
const sampleRef = demo.sample || 'samples/quickstart/input/profile.json'
const expectedRef = demo.expect || 'samples/quickstart/expected/result.json'
const mode = process.argv.includes('--json') ? 'json' : process.argv.includes('--check') ? 'check' : 'summary'

function buildResult() {
  const suite = inspectMembers(root)
  const profile = readProfile(root, sampleRef)
  const rows = new Map(profile.rows.map((row) => [row.id, row]))
  const missing = []
  const members = suite.members.map((member) => {
    const row = rows.get(member.id)
    if (!row) {
      missing.push(member.id)
      return { id: member.id, version: member.version, pin: member.pin, profile_row: 'missing' }
    }
    if (row.version !== member.pin) {
      throw new SuiteError(
        'E_SUITE_VERSION_MISMATCH',
        `profile 中 ${member.id} 的版本 ${String(row.version)} 与套件固定 ${member.pin} 不一致`,
        '重新生成 profile dump，或删除该行后重新安装套件',
      )
    }
    return {
      id: member.id,
      version: member.version,
      pin: member.pin,
      profile_row: row.enabled === false ? 'disabled' : 'enabled',
    }
  })
  const enabled = members.filter((member) => member.profile_row === 'enabled').length
  return {
    suite: suite.name,
    version: suite.version,
    sample: sampleRef,
    network: false,
    profile: {
      name: String(profile.profile ?? 'unknown'),
      kind: String(profile.kind ?? 'synthetic'),
      rows: members.length,
      enabled,
      missing: missing.length,
    },
    members,
    summary: { members: members.length, resolved: members.length, ok: missing.length === 0 },
  }
}

function readExpected() {
  return JSON.parse(readFileSync(path.join(root, expectedRef), 'utf8'))
}

function printSummary(result) {
  console.log(`${result.suite} quickstart (offline)`)
  console.log(`suite:    ${result.suite} ${result.version}`)
  console.log(
    `profile:  ${result.profile.name} (${result.profile.kind}, ${result.profile.enabled}/${result.profile.rows} rows enabled)`,
  )
  console.log(`members:  ${result.summary.resolved}/${result.summary.members} resolved`)
  for (const member of result.members) {
    const source = member.profile_row === 'enabled' ? '[manifest pin]' : `[${member.profile_row}]`
    console.log(
      `  ${member.id.padEnd(20)} ${member.version.padEnd(16)} ${source.padEnd(17)} profile=${member.profile_row}`,
    )
  }
  console.log(`network:  false (no fetch, no registry call)`)
}

function main() {
  const result = buildResult()
  if (mode === 'json') {
    process.stdout.write(`${JSON.stringify(result, null, 2)}\n`)
    if (!result.summary.ok) process.exitCode = 1
    return
  }
  printSummary(result)
  if (!result.summary.ok) {
    console.error(`quickstart failed: profile is missing member rows (${result.profile.missing})`)
    process.exitCode = 1
    return
  }
  try {
    assert.deepStrictEqual(result, readExpected())
    console.log(`golden:   ${expectedRef} matches`)
    console.log('quickstart ok')
  } catch {
    console.error(`quickstart failed: output does not match ${expectedRef}`)
    console.error('run `node samples/quickstart/run.mjs --json` and diff it against the golden file')
    process.exitCode = 1
  }
}

try {
  main()
} catch (error) {
  if (error instanceof SuiteError) console.error(`quickstart failed: ${error.message}`)
  else console.error(`quickstart failed: ${error instanceof Error ? error.message : String(error)}`)
  process.exitCode = 1
}
