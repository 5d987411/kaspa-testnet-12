
# Silverscript

Silverscript is a CashScript-inspired language and compiler that targets Kaspa script.

## Workspace

This repository is a Rust workspace. The main crate is `silverscript-lang`.

## Build & Test

```bash
cargo test -p silverscript-lang
```

## Layout

- `silverscript-lang/` – compiler, parser, and tests
- `silverscript-lang/tests/examples/` – example contracts (`.silver`)

## Notes

- Kaspa dependencies are pulled from https://github.com/kaspanet/rusty-kaspa (branch `covpp-reset1`).
