#!/bin/bash
# Deploy DeadmanSwitch (Kaspa.com style) to Kaspa Testnet 12
# Usage: ./deploy_deadman_kaspa.sh <private-key>

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SILVERSCRIPT_DIR="/home/cliff/silverscript"
CONTRACT_FILE="$SILVERSCRIPT_DIR/deadman.json"
ARGS_FILE="$SILVERSCRIPT_DIR/deadman_args.json"

echo "=========================================="
echo -e "${BLUE}DeadmanSwitch Deployment${NC}"
echo "=========================================="
echo ""

if [ $# -lt 1 ]; then
    echo -e "${RED}Error: Missing private key${NC}"
    echo "Usage: $0 <private-key>"
    exit 1
fi

PRIVATE_KEY=$1

echo -e "${GREEN}Contract:${NC} DeadmanSwitch"
echo -e "${GREEN}File:${NC} $CONTRACT_FILE"
echo ""

echo -e "${BLUE}Contract Details:${NC}"
echo "----------------------------------------"
CONTRACT_NAME_FROM_FILE=$(cat $CONTRACT_FILE | grep '"contract_name"' | cut -d'"' -f4)
SCRIPT_LENGTH=$(python3 -c "import json; print(len(json.load(open('$CONTRACT_FILE'))['script']))")
ABI_ENTRIES=$(cat $CONTRACT_FILE | grep '"abi"' -A 100 | grep '"name"' | wc -l)

echo "  Name: $CONTRACT_NAME_FROM_FILE"
echo "  Script Size: $SCRIPT_LENGTH bytes"
echo "  Entrypoints: $ABI_ENTRIES"
echo ""

echo -e "${BLUE}Constructor Args:${NC}"
python3 -c "
import json
with open('$ARGS_FILE') as f:
    args = json.load(f)
    print(f'  Owner: {bytes(args[0][\"data\"]).hex()}')
    print(f'  Heir: {bytes(args[1][\"data\"]).hex()}')
    print(f'  Inactivity Period: {args[2][\"data\"]} seconds ({args[2][\"data\"]/86400:.1f} days)')
"

echo ""
echo -e "${BLUE}ABI:${NC}"
cat $CONTRACT_FILE | python3 -c "
import json,sys
d=json.load(sys.stdin)
for func in d.get('abi', []):
    print(f'  {func[\"name\"]}({', '.join([i[\"type_name\"] for i in func.get(\"inputs\", [])])})')
"

echo ""
echo -e "${BLUE}Bytecode (hex):${NC}"
python3 -c "
import json
with open('$CONTRACT_FILE') as f:
    data = json.load(f)
    script = data['script']
    print('  ' + ''.join([f'{b:02x}' for b in script]))
"

echo ""
echo -e "${GREEN}Contract ready for deployment!${NC}"
echo ""
echo "To deploy:"
echo "  1. Start kaspad on testnet-12"
echo "  2. Get testnet coins from faucet"
echo "  3. Use rothschild to create P2SH output with this redeem script"
echo "  4. Broadcast the transaction"
echo ""
echo "Entrypoints:"
echo "  - keepAlive(sig): Refresh the timer (owner signature)"
echo "  - claim(sig): Claim funds after inactivity period (heir signature)"
