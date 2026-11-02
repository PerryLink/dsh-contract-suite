# 故障排查 — dsh-contract-suite

每条按「症状 / 原因 / 动作」写。报错原文的格式是 `<一句人话>（E_XXX）｜下一步：<一个动作>`；把 `E_XXX` 和那一行一起发到 issue 即可定位。不要把真实合同、条款清单或客户数据贴进 issue。

## 1. 装完少一个成员（E_SUITE_PATCH_MISMATCH）

- **症状**：`cordis.patch.yml 与 dependencies 不一致（dependencies 有但 patch 没有：dsh-legal-clause）（E_SUITE_PATCH_MISMATCH）｜下一步：让两处成员列表完全一致后重新打包发布`
- **原因**：升级时只改了 `package.json` 的 `dependencies`，忘了在 `cordis.patch.yml` 增加对应的 `id` / `name` 行；或者删成员时只删了一处。
- **动作**：在本包根目录跑 `node samples/quickstart/run.mjs`，按报错里列出的差异把 `cordis.patch.yml` 与 `dependencies` 对齐，重新打包后再安装。

## 2. 套件清单读不出来（E_SUITE_MANIFEST_MISSING）

- **症状**：`找不到套件清单 package.json（E_SUITE_MANIFEST_MISSING）｜下一步：在套件包根目录运行命令，或重新安装套件`
- **原因**：命令跑在了错误目录；tarball 解压不完整，`cordis.patch.yml` 或 `samples/` 没进包；`package.json` 被手工改坏成非法 JSON。
- **动作**：回到解压后的套件根目录（能看到 `package.json` 和 `cordis.patch.yml`）再跑；仍失败就删掉该 profile 下的套件目录，重新执行 `dsh plugin --profile <profile> add dsh-contract-suite`。

## 3. 成员版本对不上（E_SUITE_VERSION_MISMATCH）

- **症状**：`成员 dsh-legal-intake 已安装 0.1.0-alpha.11，套件固定 0.1.0-alpha.10（E_SUITE_VERSION_MISMATCH）｜下一步：删除 node_modules 后重新安装套件，不要单独升级成员包`
- **原因**：在同一个 profile 里单独升级过某个成员，或 `node_modules` 里残留了旧版本；suite 承诺的是固定的一组成员版本。
- **动作**：删除该 profile 下的 `node_modules`，重新安装 suite；如果确实需要新成员版本，等套件发布新的固定版本，不要只升成员。

## 还不行

```sh
node samples/quickstart/run.mjs --check     # 自带样例必须通过
node --test test/suite.test.mjs             # 8 项测试
```

仍失败时请在 <https://github.com/PerryLink/dsh-contract-suite/issues> 附上：包版本、Node 版本、最小合成输入、完整报错那一行。
