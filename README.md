# BRAIN DUMP FOLDER DO NOT USE
GO TO https://github.com/5d987411/KTN12
FOR UPDATES


Updated the dashboard with API notes:
Files updated:
1. index.html - Added API notes panel in wallet section showing old vs new API
2. server.js - Added comment block at top documenting REST vs wRPC approaches
3. deadman_claim.js - Added header comment with API usage examples
4. deadman_claim_v2.js - Added header comment with API usage examples
New API pattern documented:
const { RpcClient } = require('kaspa');
const rpc = new RpcClient({
    url: 'ws://localhost:17210',  // or 'https://api-tn12.kaspa.org'
    networkId: 'testnet-12'
});
await rpc.connect();
// use rpc.getUtxosByAddresses(), submitTransaction(), etc.
await rpc.disconnect();
Ports documented:
- gRPC: 16210
- wRPC-Borsh: 17210 (recommended)
- wRPC-JSON: 18210

- 
rpc errors...
Here are the main RPC methods available (full list from docs.rs):
Query Methods:
- get_info - Node info
- get_block - Get block by hash
- get_blocks - Get blocks
- get_block_count - Block count
- get_block_dag_info - DAG info
- get_balance_by_address - Address balance
- get_balances_by_addresses - Multiple balances
- get_utxos_by_addresses - UTXOs for addresses
- get_mempool_entries - Mempool txs
- get_peer_addresses - Known peers
- get_connected_peer_info - Connected peers
- get_fee_estimate - Fee estimate
- get_sink - Current sink
- get_sink_blue_score - Sink blue score
- get_metrics - Node metrics
Actions:
- submit_transaction - Submit tx
- submit_block - Submit block
- add_peer - Add peer
- ban/unban - Ban peers
- ping - Ping node
Subscriptions:
- start_notify / stop_notify - Subscribe to events
- utxos_changed - UTXO change notifications
Ports: gRPC 16210, wRPC-Borsh 17210, wRPC-JSON 18210 (Testnet-12)



Goal
The user is setting up a Kaspa TN12 testnet dashboard with various features including:
- Starting kaspad, kaspa-miner, and related services
- Creating a web dashboard for controlling CLI commands
- Working on send/transfer functionality
- Troubleshooting UTXO sync issues
Instructions
- Various requests to add panels, buttons, debug info to the dashboard
- Fix restart button functionality
- Add kaspad parameters to dashboard
- Test wallet-cli.sh transfer functionality
Discoveries
- Local UTXO not synced - causes "Has not enough funds" errors
- wallet-cli.sh works for TN12 (uses kgraf3 CLI)
- Transfer sends transaction but balance not showing (likely propagation delay)
- kaspa-cli requires TTY
Accomplished
- Set up kaspad with various flags
- Created panels 7, 8, 9 for parameters, debug, command reference
- Fixed restart button
- Added kaspad flags like --async-threads, --ram-scale
- Fixed wallet-cli.sh to use correct CLI path
- Tested transfer - transaction created but balance not yet showing
Relevant files
- /Users/4dsto/ktn12/dashboard-tn12/index.html
- /Users/4dsto/ktn12/dashboard-tn12/server.js
- /Users/4dsto/ktn12/wallet-cli.sh
Let me format this properly.
Goal
The user is building a Kaspa TN12 testnet control panel dashboard that wraps CLI commands with buttons. Key goals include:
- Controlling kaspad, kaspa-miner, and rothschild (TX generator)
- Sending transactions and managing wallets
- Debugging UTXO sync issues
Instructions
- Add interactive panels to dashboard with toggles for kaspad flags
- Add debug console showing sync status
- Add command reference panel
- Fix restart button to properly start kaspad with built command
- Test wallet-cli.sh transfer functionality
Discoveries
1. UTXO Sync Issue: Local UTXO not synced - causes "Has not enough funds" errors. Solution: restart kaspad with --reset-db
2. wallet-cli.sh works: Uses kgraf3 CLI which works for TN12
3. Transfer test: Successfully created transaction (TX ID: e3677d46c90a83b1028cfda7b0578205d0ffe521b76b0a451c75735ff49cddcb) but balance not yet showing (likely propagation delay)
4. kaspa-cli: Requires TTY, can't run directly
5. kaspad performance flags: Added --async-threads=24 and --ram-scale=2 to speed up UTXO sync
Accomplished
- ✅ Created Panels 7, 8, 9 for parameters, debug, command reference
- ✅ Added all kaspad flags with toggles including performance options
- ✅ Fixed restart button with proper directory and output to console
- ✅ Fixed wallet-cli.sh path to kgraf3 CLI
- ✅ Tested transfer - transaction created successfully
- ⏳ Waiting for transaction to propagate to API
Relevant files / directories
- /Users/4dsto/ktn12/dashboard-tn12/index.html - Dashboard UI with panels 1-9
- /Users/4dsto/ktn12/dashboard-tn12/server.js - API endpoints
- /Users/4dsto/ktn12/wallet-cli.sh - Wallet CLI wrapper (fixed path)
- /Users/4dsto/kgraf3/target/release/kaspa-graffiti-cli - CLI binary
- /Users/4dsto/rusty-kaspa-tn12/target/release/kaspad - Node daemon
- /Users/4dsto/rusty-kaspa-tn12/target/release/rothschild - TX generator
Current Status
- kaspad running with: --testnet --netsuffix=12 --utxoindex --appdir ~/.kaspa-testnet12 --rpclisten=127.0.0.1:16210 --rpclisten-json --unsaferpc --listen=0.0.0.0:16311 --addpeer=23.118.8.168 --async-threads=24 --ram-scale=2
- Last transfer created TX but balance still showing 0 - needs time to propagate
- Dashboard running at http://localhost:3001


# Silverscript

Silverscript is a CashScript-inspired language and compiler that targets Kaspa script.

**Status:** Experimental — the project is unstable and may introduce breaking changes without notice. Use with caution and expect language syntax, APIs and output formats to change.

**Note:** The compiled scripts produced by this repository are valid only on Kaspa Testnet 12. Do not assume compatibility with other Kaspa networks or mainnet.

## Workspace

This repository is a Rust workspace. The main crate is `silverscript-lang`.

## Build & Test

```bash
cargo test -p silverscript-lang
```

## Layout

- `silverscript-lang/` – compiler, parser, and tests
- `silverscript-lang/tests/examples/` – example contracts (`.sil` files)

## Documentation

See [TUTORIAL.md](TUTORIAL.md) for a full language and usage tutorial.

## Credits

See [CREDITS.md](CREDITS.md) for acknowledgements and credits.

## Notes

- Kaspa dependencies are pulled from https://github.com/kaspanet/rusty-kaspa (branch `covpp-reset1`).
