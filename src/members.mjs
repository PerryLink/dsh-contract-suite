/**
 * Offline suite-member inspector.
 *
 * A suite is install-only: it has no tools of its own. This module is the one
 * piece of runtime logic, shared by the quickstart sample and the release gate.
 * It reads `package.json` + `cordis.patch.yml`, then checks every member named in
 * the patch. When a member is already installed under `node_modules/`, its real
 * version is used and compared with the suite pin; otherwise the manifest pin is
 * reported. No network access, no writes.
 */
import { existsSync, readFileSync } from 'node:fs'
import path from 'node:path'

export class SuiteError extends Error {
  constructor(code, message, next) {
    super(`${message}（${code}）｜下一步：${next}`)
    this.name = 'SuiteError'
    this.code = code
    this.next = next
  }
}

function readJson(filePath, label) {
  let text
  try {
    text = readFileSync(filePath, 'utf8')
  } catch {
    throw new SuiteError(
      'E_SUITE_MANIFEST_MISSING',
      `读不到${label}（${path.basename(filePath)}）`,
      '确认套件 tarball 完整，或在包根目录重新安装套件',
    )
  }
  try {
    return JSON.parse(text)
  } catch {
    throw new SuiteError(
      'E_SUITE_MANIFEST_MISSING',
      `${label}不是合法 JSON，套件读不出成员清单`,
      '重新安装套件，或用 npm 重新下载 tarball',
    )
  }
}

/**
 * Parse the small `- insert:` shape used by cordis.patch.yml. Every member must
 * carry both `id:` and `name:` and the two must match; anything else means the
 * patch no longer describes the dependency set.
 */
function parsePatch(text) {
  const members = []
  let current = null
  for (const line of text.replace(/\r\n/g, '\n').split('\n')) {
    const id = line.match(/^\s*-\s+id:\s*([^\s#]+)\s*$/)
    if (id) {
      current = { id: id[1], name: null }
      members.push(current)
      continue
    }
    const name = line.match(/^\s+name:\s*([^\s#]+)\s*$/)
    if (name && current) current.name = name[1]
  }
  return members
}

export function readManifest(rootDir) {
  const pkgPath = path.join(rootDir, 'package.json')
  if (!existsSync(pkgPath)) {
    throw new SuiteError(
      'E_SUITE_MANIFEST_MISSING',
      '找不到套件清单 package.json',
      '在套件包根目录运行命令，或重新安装套件',
    )
  }
  const pkg = readJson(pkgPath, '套件清单')
  const patchRef = pkg.dsh?.bundle?.patch
  if (!patchRef) {
    throw new SuiteError(
      'E_SUITE_MANIFEST_MISSING',
      'package.json 缺少 dsh.bundle.patch，套件不知道要装哪些成员',
      '恢复 dsh.bundle.patch 字段后重新打包发布',
    )
  }
  const patchPath = path.resolve(rootDir, patchRef)
  if (!existsSync(patchPath)) {
    throw new SuiteError(
      'E_SUITE_MANIFEST_MISSING',
      `找不到成员清单 ${patchRef}`,
      '确认发布物包含 cordis.patch.yml，或重新安装套件',
    )
  }
  const members = parsePatch(readFileSync(patchPath, 'utf8'))
  if (members.length === 0) {
    throw new SuiteError(
      'E_SUITE_PATCH_MISMATCH',
      'cordis.patch.yml 里没有任何成员',
      '按 package.json 的 dependencies 补回成员行后重新发布',
    )
  }
  const seen = new Set()
  for (const member of members) {
    if (seen.has(member.id)) {
      throw new SuiteError(
        'E_SUITE_PATCH_MISMATCH',
        `cordis.patch.yml 重复列出成员 ${member.id}`,
        '每个成员只保留一条 id/name 行',
      )
    }
    seen.add(member.id)
    if (member.name !== member.id) {
      throw new SuiteError(
        'E_SUITE_PATCH_MISMATCH',
        `cordis.patch.yml 的 ${member.id} 缺少匹配的 name 行`,
        '让 id 与 name 两行保持同名后重新发布',
      )
    }
  }
  const deps = pkg.dependencies && typeof pkg.dependencies === 'object' ? pkg.dependencies : {}
  const depIds = Object.keys(deps)
  const missingInPatch = depIds.filter((id) => !seen.has(id))
  const missingInDeps = [...seen].filter((id) => !(id in deps))
  if (missingInPatch.length > 0 || missingInDeps.length > 0) {
    const pieces = []
    if (missingInPatch.length > 0) pieces.push(`dependencies 有但 patch 没有：${missingInPatch.join(', ')}`)
    if (missingInDeps.length > 0) pieces.push(`patch 有但 dependencies 没有：${missingInDeps.join(', ')}`)
    throw new SuiteError(
      'E_SUITE_PATCH_MISMATCH',
      `cordis.patch.yml 与 dependencies 不一致（${pieces.join('；')}）`,
      '让两处成员列表完全一致后重新打包发布',
    )
  }
  return {
    name: pkg.name,
    version: pkg.version,
    patch: patchRef,
    members: members.map(({ id }) => ({ id, version: deps[id] })),
  }
}

/**
 * Resolve every member. A member installed at exactly the pinned version is
 * reported from `node_modules`; otherwise the dependency pin is the answer.
 * Any installed-but-different version is a hard failure because a suite promises
 * one fixed member set.
 */
export function inspectMembers(rootDir = process.cwd()) {
  const manifest = readManifest(rootDir)
  const members = manifest.members.map(({ id, version: pin }) => {
    const installedPkg = path.join(rootDir, 'node_modules', id, 'package.json')
    if (!existsSync(installedPkg)) {
      return { id, version: pin, pin, source: 'manifest' }
    }
    const installed = readJson(installedPkg, `已安装成员 ${id} 的清单`)
    if (installed.name !== id) {
      throw new SuiteError(
        'E_SUITE_VERSION_MISMATCH',
        `node_modules 里的 ${id} 实际是 ${String(installed.name)}`,
        '删除 node_modules 后重新安装套件，避免同名目录被占用',
      )
    }
    if (installed.version !== pin) {
      throw new SuiteError(
        'E_SUITE_VERSION_MISMATCH',
        `成员 ${id} 已安装 ${String(installed.version)}，套件固定 ${pin}`,
        '删除 node_modules 后重新安装套件，不要单独升级成员包',
      )
    }
    return { id, version: installed.version, pin, source: 'node_modules' }
  })
  return { name: manifest.name, version: manifest.version, members }
}

export function readProfile(rootDir, sampleRef) {
  const samplePath = path.resolve(rootDir, sampleRef)
  if (!existsSync(samplePath)) {
    throw new SuiteError(
      'E_SUITE_MANIFEST_MISSING',
      `找不到 quickstart 输入样例 ${sampleRef}`,
      '确认发布物包含 samples/quickstart/input/，或重新安装套件',
    )
  }
  const profile = readJson(samplePath, 'quickstart 样例')
  if (!Array.isArray(profile.rows)) {
    throw new SuiteError(
      'E_SUITE_MANIFEST_MISSING',
      'quickstart 样例缺少 rows 数组，读不出安装后的成员行',
      '恢复 samples/quickstart/input/profile.json 后重跑',
    )
  }
  return profile
}
