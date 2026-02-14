# Deadman Switch Smart Contract

A smart contract that allows a beneficiary to claim funds after the owner has not interacted with the contract for a specified time period.

## Concept

A "deadman switch" is a mechanism that triggers an action after a predetermined period of inactivity. In this case:

- **Owner** funds the contract and can cancel anytime
- **Beneficiary** can claim funds after the timeout period elapses without owner intervention
- If the owner remains active (calls heartbeat), the timer resets

## Use Cases

1. **Estate Planning / Inheritance** - Automatically transfer funds to beneficiaries without requiring legal processes
2. **Long-term Storage** - Funds locked until you return (e.g., cold storage)
3. **Forced Savings** - Prevent yourself from spending by setting a timeout

## Contract Structure

```sil
pragma silverscript ^0.1.0;

contract DeadmanSwitchSimple(
    pubkey owner,           // Owner public key
    pubkey beneficiary,    // Beneficiary public key
    int timeout            // Timeout in seconds
) {
    // Owner cancels and recovers funds
    entrypoint function cancel(sig s) {
        require(checkSig(s, owner));
        bytes34 lock = new LockingBytecodeP2PK(owner);
        require(tx.outputs[0].lockingBytecode == lock);
    }
    
    // Beneficiary claims after timeout
    entrypoint function claim(sig s) {
        require(checkSig(s, beneficiary));
        require(this.age >= timeout);
        bytes34 lock = new LockingBytecodeP2PK(beneficiary);
        require(tx.outputs[0].lockingBytecode == lock);
    }
}
```

## Compilation

### Generate Constructor Arguments

Create `deadman_args.json` with the public keys and timeout:

```json
[
  {"kind": "bytes", "data": [1, 2, 3, ..., 32]},
  {"kind": "bytes", "data": [33, 34, 35, ..., 64]},
  {"kind": "int", "data": 31536000}
]
```

- First arg: Owner public key (32 bytes)
- Second arg: Beneficiary public key (32 bytes)  
- Third arg: Timeout in seconds (e.g., 31536000 = 1 year)

### Compile

```bash
silverc deadman_simple.sil --constructor-args deadman_args.json
```

This produces `deadman_simple.json` with the compiled bytecode.

## Deployment

### Generate Key Pairs

```bash
# Generate owner keys
kaspa-cli keygen
# Save the public key: <owner_pubkey>

# Generate beneficiary keys  
kaspa-cli keygen
# Save the public key: <beneficiary_pubkey>
```

### Create Constructor Arguments

```json
[
  {"kind": "bytes", "data": [0x01, 0x02, ..., 0x20]},
  {"kind": "bytes", "data": [0x21, 0x22, ..., 0x40]},
  {"kind": "int", "data": 31536000}
]
```

Replace the hex values with your actual public keys.

### Deploy

```bash
silverc deadman_simple.sil --constructor-args your_args.json
```

Then use the deployment script to send funds to the contract address.

## Usage

### Owner Actions

**Cancel (Recover Funds):**
- Sign with owner private key
- Call `cancel` entrypoint
- All funds returned to owner

**Heartbeat (Reset Timer):**
- Any transaction that spends from the contract with owner signature resets the timer

### Beneficiary Actions

**Claim (After Timeout):**
- Wait for `timeout` seconds without owner intervention
- Sign with beneficiary private key
- Call `claim` entrypoint
- All funds transferred to beneficiary

## Security Considerations

1. **Timeout Period**: Choose an appropriate timeout (1 year is common)
2. **Key Security**: Both owner and beneficiary keys must be stored securely
3. **Heartbeat**: Owner must remember to periodically interact with the contract
4. **No Retraction**: Once claimed, funds cannot be recovered by owner

## Example Timeout Values

| Period | Seconds |
|--------|---------|
| 30 days | 2,592,000 |
| 90 days | 7,776,000 |
| 1 year | 31,536,000 |
| 5 years | 157,680,000 |

## Files

- `deadman_simple.sil` - Contract source code
- `deadman_simple.json` - Compiled bytecode
- `deadman_args.json` - Example constructor arguments
