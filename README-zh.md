<div align="center">

# dsh-contract-suite

> **官方仓库。** 本包唯一官方仓库，由 PerryLink 维护；其他账号下的同名仓库与本项目无关。Apache-2.0。

[![npm](https://img.shields.io/npm/v/dsh-contract-suite)](https://www.npmjs.com/package/dsh-contract-suite)
[![CI](https://github.com/PerryLink/dsh-contract-suite/actions/workflows/ci.yml/badge.svg)](https://github.com/PerryLink/dsh-contract-suite/actions)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE)
[![dsh-plugin](https://img.shields.io/badge/dsh--plugin-%E2%9C%93-green)](https://github.com/topics/dsh-plugin)
[![docs](https://img.shields.io/badge/docs-domain%20index-0b5fff)](https://perrylink.github.io/dsh-plugins/)
[![Gitee](https://img.shields.io/badge/Gitee-aggregate-c71d23?logo=gitee)](https://gitee.com/perrylink/dsh-plugins)
[![dshfind](https://dshfind.com/api/badge/PerryLink/dsh-contract-suite?metric=downloads)](https://dshfind.com/plugins/PerryLink/dsh-contract-suite?ref=badge)
[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)
[![Node](https://img.shields.io/badge/node-24.9%2B-brightgreen)](#)
[![npm downloads](https://img.shields.io/npm/dm/dsh-contract-suite)](https://www.npmjs.com/package/dsh-contract-suite)

**一键安装合同法务套件：法务需求收件与条款/playbook 审查。**

> **状态：alpha / 公开合成 / partial / not counted / 非 GA。** 不含客户证据、客户数据，也不作生产可用声明。

[English](README.md) · [简体中文](README-zh.md) · [Español](README-es.md) · [Português](README-pt.md) · [हिन्दी](README-hi.md)

```sh
dsh plugin --profile <profile> add dsh-contract-suite
```

</div>

> ⭐ 如果它帮到了你，点个 star 会让下一个人更容易找到它；没有任何功能被 star 解锁。

![Workflow diagram for dsh-contract-suite: local input, plugin, local output.](docs/assets/dsh-contract-suite-flow.svg)

*工作流：本地输入 → 插件 → 本地输出；不需要调用模型。*

## 安装

安装并验证：

```sh
dsh plugin --profile <profile> add dsh-contract-suite
dsh --profile <profile> --dump-config | grep dsh-contract-suite
```

卸载：

```sh
dsh plugin --profile <profile> remove dsh-contract-suite
```

## 它做什么

一键安装合同法务套件：法务需求收件与条款/playbook 审查。 在 DeepSeek Harness 本地运行；下表就是实际工具面，示例使用真实命令面。

输入和输出都留在本地，不上传。

## 成员

工具名和说明保留英文，以对应运行输出。

| 成员 | 版本 |
|---|---:|
| `dsh-legal-intake` | `0.1.0-alpha.2` |
| `dsh-legal-clause` | `0.1.0-alpha.4` |

## 快速开始

```sh
dsh plugin --profile <profile> add dsh-contract-suite
dsh --profile <profile> --dump-config | grep dsh-contract-suite
```

![Terminal demo: real dsh-contract-suite install output](docs/assets/dsh-contract-suite-install.gif)

*临时 profile 中真实 `dsh plugin add dsh-finops-suite` 输出；路径为临时目录。*

## 边界

- 仅公开/合成样例；不含客户数据或客户证据。
- alpha/partial、not counted，不作 GA 或生产可用声明。
- 除非工具明确说明，否则不调用模型、不联网。
- 每个工具的精确边界见工具表与 `ACCEPTANCE.csv`。

## 公开样例

公开/合成 fixture 在 `test/fixtures/`；`ACCEPTANCE.csv` 记录公开检查，全部 `counted=false`。

## 开发

```sh
pnpm install --frozen-lockfile
pnpm build && pnpm lint && pnpm typecheck && pnpm test
```

## 兼容性

| 维度 | 状态 |
|---|---|
| Harness | `dsh >=0.2.1-rc.3 <0.3.0` |
| Node | `>=24.9.0 <25` |
| Platforms | All; local files only |
| 数据 | No network, no model call, no upload |

## 权限与数据

- 本地运行；不联网、不调用模型、不上传。
- 只使用公开/合成 fixture；不含客户数据或客户证据。
- alpha/partial；not counted，不作 GA 或生产可用声明。
- 冻结包仍可安装；不再加新功能，只修真实故障。

## 相关项目

兄弟包与家族索引： [dsh-legal-intake](https://github.com/PerryLink/dsh-legal-intake) · [dsh-legal-clause](https://github.com/PerryLink/dsh-legal-clause)

- [领域索引](https://perrylink.github.io/dsh-plugins/)
- [Checker 家族](https://perrylink.github.io/zh/checkers/)
- [主线家族](https://github.com/PerryLink/dsh-kit)

## 家族

<details>
<summary>DSH 领域插件家族（15 个包 + 2 个 suite）</summary>

| Package | npm |
|---|---|
| **[dsh-einvoice](https://github.com/PerryLink/dsh-einvoice)** | [npm](https://www.npmjs.com/package/dsh-einvoice) |
| **[dsh-docx-redline](https://github.com/PerryLink/dsh-docx-redline)** | [npm](https://www.npmjs.com/package/dsh-docx-redline) |
| **[dsh-policy-ledger](https://github.com/PerryLink/dsh-policy-ledger)** | [npm](https://www.npmjs.com/package/dsh-policy-ledger) |
| **[dsh-ghg](https://github.com/PerryLink/dsh-ghg)** | [npm](https://www.npmjs.com/package/dsh-ghg) |
| **[dsh-bankrec](https://github.com/PerryLink/dsh-bankrec)** | [npm](https://www.npmjs.com/package/dsh-bankrec) |
| **[dsh-ap-three-way](https://github.com/PerryLink/dsh-ap-three-way)** | [npm](https://www.npmjs.com/package/dsh-ap-three-way) |
| **[dsh-ifc-qto](https://github.com/PerryLink/dsh-ifc-qto)** | [npm](https://www.npmjs.com/package/dsh-ifc-qto) |
| **[dsh-qms-capa](https://github.com/PerryLink/dsh-qms-capa)** | [npm](https://www.npmjs.com/package/dsh-qms-capa) |
| **[dsh-legal-intake](https://github.com/PerryLink/dsh-legal-intake)** | [npm](https://www.npmjs.com/package/dsh-legal-intake) |
| **[dsh-legal-clause](https://github.com/PerryLink/dsh-legal-clause)** | [npm](https://www.npmjs.com/package/dsh-legal-clause) |
| **[dsh-freight-audit](https://github.com/PerryLink/dsh-freight-audit)** | [npm](https://www.npmjs.com/package/dsh-freight-audit) |
| **[dsh-hs-candidate](https://github.com/PerryLink/dsh-hs-candidate)** | [npm](https://www.npmjs.com/package/dsh-hs-candidate) |
| **[dsh-travel-recon](https://github.com/PerryLink/dsh-travel-recon)** | [npm](https://www.npmjs.com/package/dsh-travel-recon) |
| **[dsh-pim-lint](https://github.com/PerryLink/dsh-pim-lint)** | [npm](https://www.npmjs.com/package/dsh-pim-lint) |
| **[dsh-eval-pack](https://github.com/PerryLink/dsh-eval-pack)** | [npm](https://www.npmjs.com/package/dsh-eval-pack) |
| **[dsh-finops-suite](https://github.com/PerryLink/dsh-finops-suite)** | [npm](https://www.npmjs.com/package/dsh-finops-suite) |
| **[dsh-contract-suite](https://github.com/PerryLink/dsh-contract-suite)** | [npm](https://www.npmjs.com/package/dsh-contract-suite) |

</details>

## 许可证

Apache-2.0. See `LICENSE`, `NOTICE`, `THIRD-PARTY-NOTICES`.
