#!/usr/bin/env python3
"""
Kaspa Testnet 12 CLI - Node Interaction Tool
"""

import argparse
import json
import subprocess
import sys
import time
import os

CONFIG = {
    "rpc_host": "localhost",
    "rpc_port": 16210,
    "network": "testnet-12",
    "data_dir": os.path.expanduser("~/.rusty-kaspa/kaspa-testnet-12"),
    "node_binary": os.path.expanduser("~/kaspa-node/rusty-kaspa/target/release/kaspad"),
    "wallet_binary": os.path.expanduser("~/kaspa-node/kaspa-testnet-12-main/rothschild"),
}

COLORS = {
    "red": "\033[0;31m",
    "green": "\033[0;32m",
    "yellow": "\033[1;33m",
    "blue": "\033[0;34m",
    "cyan": "\033[0;36m",
    "nc": "\033[0m",
}


def print_color(text, color="nc"):
    print(f"{COLORS.get(color, '')}{text}{COLORS['nc']}")


def rpc_call(method, params=None):
    """Make RPC call to the node via gRPC using rothschild."""
    import socket
    
    if params is None:
        params = []
    
    # Build JSON-RPC request
    request = json.dumps({
        "id": 1,
        "method": method,
        "params": params
    }) + "\n"
    
    # Try gRPC port first, then JSON-RPC
    ports = [17210, 18210, 16210]
    
    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect(('127.0.0.1', port))
            sock.sendall(request.encode('utf-8'))
            data = sock.recv(8192)
            sock.close()
            
            # Parse response
            resp = json.loads(data.decode('utf-8', errors='replace'))
            if 'result' in resp:
                return resp['result']
        except Exception as e:
            continue
    
    return None


def check_node_status():
    """Check if node is running and get status."""
    print_color("\n=== Kaspa Node Status ===", "blue")
    
    # Check if node is running
    result = subprocess.run(
        ["lsof", "-i", f":{CONFIG['rpc_port']}"],
        capture_output=True, 
        text=True
    )
    
    if "kaspad" not in result.stdout:
        print_color("✗ Node is NOT running", "red")
        print(f"  Start with: {CONFIG['node_binary']} --testnet --netsuffix=12 --utxoindex")
        return
    
    print_color("✓ Node is running", "green")
    
    # Use tail to get latest log info
    try:
        with open("/tmp/kaspad.log", "r") as f:
            lines = f.readlines()[-50:]
            
        # Find recent block info
        for line in lines:
            if "Block count:" in line or "blockCount" in line:
                print(f"  {line.strip()}")
            elif "Accepted" in line and "blocks" in line:
                print(f"  {line.strip()}")
                break
    except:
        pass
    
    # Use rothschild to get node info
    test_wallet = "0000000000000000000000000000000000000000000000000000000000000001"
    cmd = [CONFIG['wallet_binary'], "-k", test_wallet]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=15
        )
        output = result.stdout + result.stderr
        
        for line in output.split("\n"):
            if "block count" in line.lower():
                print(f"  {line.strip()}")
            elif "network:" in line.lower():
                print(f"  {line.strip()}")
            elif "difficulty:" in line.lower():
                print(f"  {line.strip()}")
    except:
        pass


def check_balance(private_key):
    """Check wallet balance."""
    print_color("\n=== Wallet Balance ===", "blue")
    
    if not private_key:
        print_color("No private key provided. Use -k <key>", "yellow")
        return
    
    cmd = [CONFIG['wallet_binary'], "-k", private_key]
    
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        
        output_bytes = b""
        start_time = time.time()
        timeout = 45
        
        while time.time() - start_time < timeout:
            chunk = proc.stdout.read(4096)
            if chunk:
                output_bytes += chunk
            elif proc.poll() is not None:
                break
            time.sleep(0.1)
        
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except:
            proc.kill()
        
        output = output_bytes.decode('utf-8', errors='replace')
        
        for line in output.split("\n"):
            if "from address:" in line.lower():
                addr = line.split("from address:")[-1].strip()
                print(f"  Address: {addr}")
            elif "network:" in line.lower():
                print(f"  {line.strip()}")
            elif "block count:" in line.lower():
                print(f"  {line.strip()}")
            elif "difficulty:" in line.lower():
                print(f"  {line.strip()}")
            elif "daa score:" in line.lower():
                print(f"  {line.strip()}")
        
        if "estimated available UTXOs:" in output:
            utxo_count = 0
            avg_sompi = 0
            for line in output.split("\n"):
                if "avg UTXO amount:" in line.lower():
                    amount = line.split("avg UTXO amount:")[-1].strip().replace(",", "")
                    try:
                        avg_sompi = int(amount)
                    except:
                        avg_sompi = 0
                if "estimated available UTXOs:" in line.lower():
                    count_str = line.split("estimated available UTXOs:")[-1].strip().replace(",", "")
                    try:
                        utxo_count = int(count_str)
                    except:
                        utxo_count = 0
            
            if avg_sompi > 0 and utxo_count > 0:
                total_kas = (avg_sompi * utxo_count) / 1e8
                print_color(f"\n  UTXOs: {utxo_count:,}", "cyan")
                print_color(f"  Avg UTXO: {avg_sompi/1e8:.4f} KAS", "cyan")
                print_color(f"\n  Estimated Balance: {total_kas:.2f} KAS", "green")
        else:
            print_color("\n  No balance found or wallet not synced", "yellow")
        
    except Exception as e:
        print_color(f"Error checking balance: {e}", "red")


def send_transaction(private_key, to_address, amount, fee=1000):
    """Send a transaction."""
    print_color("\n=== Send Transaction ===", "blue")
    
    if not private_key or not to_address:
        print_color("Error: Private key and recipient address required", "red")
        return
    
    print(f"  From: (your address)")
    print(f"  To:   {to_address}")
    print(f"  Fee:  {fee} SOMPI")
    print()
    
    cmd = [
        CONFIG['wallet_binary'],
        "-k", private_key,
        "-a", to_address,
        "-f", str(fee)
    ]
    
    print_color("Sending transaction...", "yellow")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        output = result.stdout + result.stderr
        
        if "transaction id:" in output.lower() or "txid" in output.lower():
            for line in output.split("\n"):
                if "transaction id" in line.lower():
                    print_color(f"  {line.strip()}", "green")
        
        # Check for errors
        if "error" in output.lower() or "rejected" in output.lower():
            print_color("\nTransaction errors:", "red")
            for line in output.split("\n"):
                if "error" in line.lower() or "rejected" in line.lower():
                    print(f"  {line.strip()}")
        
        print_color("\nTransaction submitted!", "green")
        
    except Exception as e:
        print_color(f"Error: {e}", "red")


def get_node_info():
    """Get detailed node information."""
    print_color("\n=== Detailed Node Info ===", "blue")
    
    info = rpc_call("getBlockDagInfo")
    if info:
        print(f"\n  Network:          {info.get('networkName', 'N/A')}")
        print(f"  Block Count:      {info.get('blockCount', 0):,}")
        print(f"  Header Count:    {info.get('headerCount', 0):,}")
        print(f"  DAA Score:       {info.get('daaScore', 0):,}")
        print(f"  Difficulty:      {info.get('difficulty', 0):.2f}")
        print(f"  Median Time:      {info.get('medianTime', 0)}")
        print(f"  Pruning Point:   {info.get('pruningPoint', 'N/A')[:16]}...")
        print(f"  Tips:            {len(info.get('tipHashes', []))}")
    
    # Get sync status
    sync = rpc_call("getSyncStatus")
    if sync:
        print(f"\n  Syncing:         {sync.get('syncing', False)}")
        print(f"  Progress:        {sync.get('progress', 0)*100:.1f}%")


def get_utxos(address):
    """Get UTXOs for an address."""
    print_color(f"\n=== UTXOs for {address} ===", "blue")
    
    result = rpc_call("getUTXOsByAddresses", {"addresses": [address]})
    
    if not result:
        print_color("No UTXOs found or RPC error", "yellow")
        return
    
    entries = result.get("entries", [])
    print(f"  Total UTXOs: {len(entries)}")
    
    total = 0
    for i, utxo in enumerate(entries[:10], 1):
        amount = utxo.get("amount", 0)
        total += amount
        print(f"  {i}. {amount/1e8:.8f} KAS (confirmations: {utxo.get('confirmations', 'N/A')})")
    
    if len(entries) > 10:
        print(f"  ... and {len(entries) - 10} more")
    
    print_color(f"\n  Total: {total/1e8:.8f} KAS", "green")


def start_node():
    """Start the Kaspa node."""
    print_color("\n=== Starting Kaspa Node ===", "blue")
    
    # Check if already running
    result = subprocess.run(
        ["lsof", "-i", f":{CONFIG['rpc_port']}"],
        capture_output=True,
        text=True
    )
    
    if "kaspad" in result.stdout:
        print_color("Node is already running!", "yellow")
        return
    
    cmd = [
        CONFIG['node_binary'],
        "--testnet",
        "--netsuffix=12",
        "--utxoindex",
        "--rpclisten-json=127.0.0.1:18210",
        "--unsaferpc"
    ]
    
    print(f"  Command: {' '.join(cmd)}")
    print_color("\nStarting node in background...", "yellow")
    
    subprocess.Popen(
        cmd,
        stdout=open("/tmp/kaspad.log", "a"),
        stderr=subprocess.STDOUT
    )
    
    print_color("Node started! Check logs with: tail -f /tmp/kaspad.log", "green")


def stop_node():
    """Stop the Kaspa node."""
    print_color("\n=== Stopping Kaspa Node ===", "blue")
    
    result = subprocess.run(
        ["pkill", "-f", "kaspad"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print_color("Node stopped!", "green")
    else:
        print_color("Node was not running", "yellow")


def disk_usage():
    """Check disk usage of node data."""
    print_color("\n=== Disk Usage ===", "blue")
    
    data_dir = CONFIG['data_dir']
    
    if os.path.exists(data_dir):
        result = subprocess.run(
            ["du", "-sh", data_dir],
            capture_output=True,
            text=True
        )
        size = result.stdout.split()[0] if result.stdout else "Unknown"
        print(f"  Node data: {size}")
    else:
        print_color("  Data directory not found", "yellow")


def main():
    parser = argparse.ArgumentParser(
        description="Kaspa Testnet 12 CLI - Node Interaction Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s status              - Check node status
  %(prog)s start               - Start the node
  %(prog)s stop                - Stop the node
  %(prog)s balance -k <key>    - Check wallet balance
  %(prog)s send -k <key> -a <addr> - Send KAS
  %(prog)s info                - Get detailed node info
  %(prog)s utxos <address>    - Get UTXOs for address
  %(prog)s disk                - Check disk usage
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # status command
    subparsers.add_parser("status", help="Check node status")
    
    # start command
    subparsers.add_parser("start", help="Start the Kaspa node")
    
    # stop command
    subparsers.add_parser("stop", help="Stop the Kaspa node")
    
    # info command
    subparsers.add_parser("info", help="Get detailed node information")
    
    # disk command
    subparsers.add_parser("disk", help="Check disk usage")
    
    # balance command
    balance_parser = subparsers.add_parser("balance", help="Check wallet balance")
    balance_parser.add_argument("-k", "--private-key", required=True, help="Private key (hex)")
    
    # send command
    send_parser = subparsers.add_parser("send", help="Send KAS")
    send_parser.add_argument("-k", "--private-key", required=True, help="Private key (hex)")
    send_parser.add_argument("-a", "--address", required=True, help="Recipient address")
    send_parser.add_argument("-f", "--fee", default=1000, help="Fee in SOMPI (default: 1000)")
    
    # utxos command
    utxos_parser = subparsers.add_parser("utxos", help="Get UTXOs for address")
    utxos_parser.add_argument("address", help="Kaspa address")
    
    args = parser.parse_args()
    
    if args.command == "status":
        check_node_status()
    elif args.command == "start":
        start_node()
    elif args.command == "stop":
        stop_node()
    elif args.command == "info":
        get_node_info()
    elif args.command == "disk":
        disk_usage()
    elif args.command == "balance":
        check_balance(args.private_key)
    elif args.command == "send":
        send_transaction(args.private_key, args.address, 0, args.fee)
    elif args.command == "utxos":
        get_utxos(args.address)
    else:
        # Default to status if no command
        check_node_status()


if __name__ == "__main__":
    main()
