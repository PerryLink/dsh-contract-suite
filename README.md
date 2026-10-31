# dsh-contract-suite

One-command install for the **法务运营** family: `dsh-legal-intake` + `dsh-legal-clause`.

> **Status: alpha / public-synthetic / partial / not counted / not GA.** This is a bundle layer only; it has no code of its own. Member packages keep their own versions, README, acceptance rows and licenses.

## Install

```sh
dsh plugin --profile <profile> add dsh-contract-suite
dsh --profile <profile> --dump-config | grep dsh-contract-suite
```

Requires DSH `>=0.2.1-rc.3 <0.3.0` and Node `>=24.9 <25`.

## Members

| Package | Version | Install alone |
|---|---:|---|
| `dsh-legal-intake` | `0.1.0-alpha.2` | `dsh plugin --profile <profile> add dsh-legal-intake` |
| `dsh-legal-clause` | `0.1.0-alpha.4` | `dsh plugin --profile <profile> add dsh-legal-clause` |

The suite pins exact member versions. It inserts one Cordis row per member; it does not copy their code, acceptance rows, or fixtures.

## Limits / non-claims

- No customer evidence, customer data, or production-readiness claim.
- Not a GA bundle; member packages are alpha/public-synthetic.
- Does not add tools of its own; install a member alone if you need only that tool.
- No Gitee/GitCode/npm mirror of member code in this package; it is a bundle manifest.

## Development

```sh
npm pack --dry-run
```

## License

Apache-2.0. See `LICENSE` and member packages' notices.
