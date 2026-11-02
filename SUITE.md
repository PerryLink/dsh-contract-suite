# dsh-contract-suite — suite contract

**Kind:** install-only bundle. **No tools of its own.** Members keep their own tools, stores, versions and acceptance rows.

## Members

| Member | Pinned version |
|---|---:|
| `dsh-legal-intake` | `0.1.0-alpha.10` |
| `dsh-legal-clause` | `0.1.0-alpha.12` |

## Install

```sh
dsh plugin --profile <profile> add dsh-contract-suite
```

## Uninstall

```sh
dsh plugin --profile <profile> remove dsh-contract-suite
```

Removing the suite removes only the suite row. Member packages remain installed; remove them individually if you no longer need them.

## Upgrade

The suite pins exact member versions. A member bump requires a new suite release; do not assume a suite upgrade moves members independently.

## Conflicts

No shared service, port or storage domain. Members are separate Cordis rows and can be installed individually.

## Verification

The install smoke workflow installs the suite, asserts every member row is present, and removes the suite again. Member acceptance rows stay with the member repositories.
