# `[tool.miri.consume]` fixtures

The project declaration is the only place in the Discovery Contract where a **caller-side file can name something
to execute**, and it arrives with every `git pull` and is editable by any pull request. §7 therefore closes its
grammar: `server` from a fixed enumeration, optional `transport`, and **nothing else** — `command`, `args`, `env`,
`url` and `path` are structurally excluded.

These are the paired inputs for that rule. Each is a complete `pyproject.toml` fragment.

| File | Shape | A conformant generator MUST |
|---|---|---|
| `conforming.toml` | `server = "miri"` | accept it and generate harness config |
| `hostile-command.toml` | adds `command` / `args` | **reject the declaration** — not ignore the key |
| `hostile-unknown-key.toml` | adds an undeclared key | **reject the declaration** |
| `hostile-server-value.toml` | `server` outside the enumeration | **reject the declaration** |
| `hostile-env.toml` | adds `env` | **reject the declaration** |

**Rejecting is not the same as ignoring**, and the distinction is the whole check: a generator that ignores an
unknown key silently accepts a file an attacker edited and proceeds as though it were clean. §7 requires rejection so
that a pull request adding `command = "curl …"` fails loudly instead of being quietly dropped.

Pass condition for every hostile case: the generator **refuses and emits no harness configuration**. A generator
that produces config with the hostile key stripped has failed — it has normalized an attack into an acceptable form,
which is the same error §3.2.2 forbids for document names.
