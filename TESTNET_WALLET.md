# Kaspa Testnet 12 Wallet

## NEW WALLET (Created: 2026-02-14)
Private Key: 39186751d974432cb50431befe5575e3d138f66c218a1018f8fa2959dc8de6aa

Testnet Address: kaspatest:qr6khmwdv9umd0wp3etenxv5c02s7zztse7lm98mnu3vugsun9j56lkrppy6j

## ⚠️ WARNING
- This is for TESTNET ONLY
- NEVER use on mainnet
- Save this file securely

## Commands
# Check balance
curl -s -X POST http://localhost:16210 -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","method":"getBalanceByAddress","params":{"address":"kaspatest:qr6khmwdv9umd0wp3etenxv5c02s7zztse7lm98mnu3vugsun9j56lkrppy6j"},"id":1}'

# Send TKAS
~/kaspa-node/kaspa-testnet-12-main/rothschild -k 39186751d974432cb50431befe5575e3d138f66c218a1018f8fa2959dc8de6aa -a <RECIPIENT_ADDRESS> -f 1000
