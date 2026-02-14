# Kaspa Testnet 12 Dashboard

## Quick Start

```bash
# Check node status
python3 kaspa-cli.py status

# Check wallet balance
python3 kaspa-cli.py balance -k <PRIVATE_KEY>

# Send KAS
python3 kaspa-cli.py send -k <PRIVATE_KEY> -a <RECIPIENT_ADDRESS>

# Get UTXOs
python3 kaspa-cli.py utxos <ADDRESS>

# Check disk usage
python3 kaspa-cli.py disk

# Start node
python3 kaspa-cli.py start

# Stop node
python3 kaspa-cli.py stop
```

## Commands

### Status
Shows if the node is running and basic info:
```bash
python3 kaspa-cli.py status
```

### Balance
Check wallet balance using private key:
```bash
python3 kaspa-cli.py balance -k 39186751d974432cb50431befe5575e3d138f66c218a1018f8fa2959dc8de6aa
```

### Send
Send KAS to an address:
```bash
python3 kaspa-cli.py send -k <PRIVATE_KEY> -a <TO_ADDRESS> -f 1000
```

### UTXOs
Get UTXOs for an address:
```bash
python3 kaspa-cli.py utxos kaspatest:qr6khmwdv9umd0wp3etenxv5c02s7zztse7lm98mnu3vugsun9j56lkrppy6j
```

### Disk
Check node disk usage:
```bash
python3 kaspa-cli.py disk
```

## Node Information

- **RPC Port:** 16210 (gRPC), 18210 (JSON-RPC)
- **P2P Port:** 16311
- **Network:** testnet-12
- **Data Directory:** ~/.rusty-kaspa/kaspa-testnet-12/

## Wallet

### Current Wallet
- **Private Key:** 39186751d974432cb50431befe5575e3d138f66c218a1018f8fa2959dc8de6aa
- **Address:** kaspatest:qr6khmwdv9umd0wp3etenxv5c02s7zztse7lm98mnu3vugsun9j56lkrppy6j

### Generate New Wallet
```bash
openssl rand -hex 32
```

## Node Start/Stop

### Start Node
```bash
cd ~/kaspa-node/kaspa-testnet-12-main
../rusty-kaspa/target/release/kaspad --testnet --netsuffix=12 --utxoindex --rpclisten-json=127.0.0.1:18210 --unsaferpc
```

### Stop Node
```bash
pkill -f kaspad
```

## Log Files

- Node log: `/tmp/kaspad.log`
- Node data: `~/.rusty-kaspa/kaspa-testnet-12/`

## References

- [Rusty Kaspa](https://github.com/kaspanet/rusty-kaspa)
- [Testnet 12 Docs](https://github.com/kaspanet/rusty-kaspa/tree/covpp/docs/testnet12.md)
- [Kaspa Faucet](https://faucet-tn12.kaspanet.io)
- [Block Explorer](https://tn12.kaspa.stream)
