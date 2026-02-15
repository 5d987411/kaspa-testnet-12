#!/usr/bin/env python3
"""
Simple Flask server for Kaspa Dashboard
Serves the dashboard and proxies log data
"""

from flask import Flask, render_template, jsonify, Response, make_response, request
import subprocess
import threading
import time
import os
import re

app = Flask(__name__)

LOG_FILE = "/tmp/kaspad_tn12.log"
PORT = 8080

WALLET_KEY = "39186751d974432cb50431befe5575e3d138f66c218a1018f8fa2959dc8de6aa"
ROTHSCHILD_BIN = "/Users/4dsto/kaspa-node/kaspa-testnet-12-main/rothschild"

wallet_cache = {"data": None, "timestamp": 0}
node_info_cache = {"data": None, "timestamp": 0}
CACHE_DURATION = 15

def get_node_info():
    """Get basic node info from rothschild (fast, cached)"""
    global node_info_cache
    
    now = time.time()
    if node_info_cache["data"] and (now - node_info_cache["timestamp"]) < CACHE_DURATION:
        return node_info_cache["data"]
    
    try:
        # Use shell with timeout to get block count
        result = subprocess.run(
            f"timeout 50 {ROTHSCHILD_BIN} -k {WALLET_KEY} 2>&1 | head -20",
            shell=True,
            capture_output=True,
            timeout=55,
            text=True
        )
        
        text = result.stdout
        
        info = {"blockCount": 0, "difficulty": 0, "daaScore": 0}
        
        for line in text.split("\n"):
            line_lower = line.lower()
            if "block count:" in line_lower:
                try:
                    info["blockCount"] = int(line_lower.split("block count:")[-1].strip().replace(",", ""))
                except:
                    pass
            elif "difficulty:" in line_lower:
                try:
                    info["difficulty"] = float(line_lower.split("difficulty:")[-1].strip().replace(",", ""))
                except:
                    pass
            elif "daa score:" in line_lower:
                try:
                    info["daaScore"] = int(line_lower.split("daa score:")[-1].strip().replace(",", ""))
                except:
                    pass
            elif "difficulty:" in line.lower():
                try:
                    info["difficulty"] = float(line.split("difficulty:")[-1].strip().replace(",", ""))
                except:
                    pass
            elif "daa score:" in line.lower():
                try:
                    info["daaScore"] = int(line.split("daa score:")[-1].strip().replace(",", ""))
                except:
                    pass
        
        node_info_cache["data"] = info
        node_info_cache["timestamp"] = time.time()
        return info
        
    except Exception as e:
        return {"error": str(e)}

def get_wallet_balance():
    """Get wallet balance using rothschild"""
    global wallet_cache
    
    now = time.time()
    if wallet_cache["data"] and (now - wallet_cache["timestamp"]) < CACHE_DURATION:
        return wallet_cache["data"]
    try:
        result = subprocess.run(
            [ROTHSCHILD_BIN, "-k", WALLET_KEY],
            capture_output=True,
            timeout=30
        )
        
        output = (result.stdout + result.stderr).decode('utf-8', errors='replace')
        
        balance_info = {"utxos": 0, "avgUtxo": 0, "balance": 0, "address": "", "blockCount": 0, "difficulty": 0, "daaScore": 0}
        
        for line in output.split("\n"):
            if "from address:" in line.lower():
                balance_info["address"] = line.split("from address:")[-1].strip()
            elif "avg UTXO amount:" in line.lower():
                amount = line.split("avg UTXO amount:")[-1].strip().replace(",", "")
                try:
                    balance_info["avgUtxo"] = int(amount)
                except:
                    pass
            elif "estimated available UTXOs:" in line.lower():
                count = line.split("estimated available UTXOs:")[-1].strip().replace(",", "")
                try:
                    balance_info["utxos"] = int(count)
                except:
                    pass
            elif "block count:" in line.lower():
                try:
                    balance_info["blockCount"] = int(line.split("block count:")[-1].strip().replace(",", ""))
                except:
                    pass
            elif "difficulty:" in line.lower():
                try:
                    balance_info["difficulty"] = float(line.split("difficulty:")[-1].strip().replace(",", ""))
                except:
                    pass
            elif "daa score:" in line.lower():
                try:
                    balance_info["daaScore"] = int(line.split("daa score:")[-1].strip().replace(",", ""))
                except:
                    pass
        
        if balance_info["avgUtxo"] > 0 and balance_info["utxos"] > 0:
            balance_info["balance"] = (balance_info["avgUtxo"] * balance_info["utxos"]) / 1e8
        
        wallet_cache["data"] = balance_info
        wallet_cache["timestamp"] = time.time()
        
        return balance_info
    except Exception as e:
        return {"error": str(e)}

def get_node_stats():
    """Parse kaspad.log for stats"""
    stats = {
        "status": "offline",
        "blockCount": 0,
        "headerCount": 0,
        "difficulty": 0,
        "daaScore": 0,
        "blueScore": 0,
        "peers": 0,
        "mempool": 0,
        "pruningPoint": "",
        "lastBlock": "",
        "lastBlueScore": 0,
        "txRate": 0,
        "blockRate": 0,
        "synced": False,
        "recentBlocks": [],
        "uptime": "",
        "memory": ""
    }
    
    try:
        # Check if node is running
        result = subprocess.run(
            ["lsof", "-i", ":16210"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        if "kaspad" not in result.stdout:
            return stats
        
        # Get memory for kaspad process
        result = subprocess.run(
            ["ps", "-o", "rss=", "-p", ""],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        pid_match = re.search(r'(\d+)\s+.*kaspad', result.stdout if result.stdout else "")
        if pid_match:
            pid = pid_match.group(1)
            mem_result = subprocess.run(
                ["ps", "-o", "rss=", "-p", pid],
                capture_output=True,
                text=True
            )
            if mem_result.stdout.strip():
                mem_kb = int(mem_result.stdout.strip())
                mem_gb = mem_kb / 1024 / 1024
                stats["memory"] = f"{mem_gb:.1f} GB"
        
        # Get disk space used by node
        node_dir = os.path.expanduser("~/.rusty-kaspa/kaspa-testnet-12")
        if os.path.exists(node_dir):
            try:
                result = subprocess.run(
                    ["du", "-sh", node_dir],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.stdout:
                    stats["memory"] = result.stdout.split()[0]
            except:
                pass
        
        stats["status"] = "online"
        
        # Get node info - try rothschild with short timeout
        try:
            result = subprocess.run(
                f"timeout 8 {ROTHSCHILD_BIN} -k {WALLET_KEY} 2>&1 | head -15",
                shell=True,
                capture_output=True,
                timeout=10,
                text=True
            )
            text = result.stdout
            for line in text.split("\n"):
                line_lower = line.lower()
                if "block count:" in line_lower:
                    try:
                        stats["blockCount"] = int(line_lower.split("block count:")[-1].strip().replace(",", ""))
                    except:
                        pass
                elif "difficulty:" in line_lower:
                    try:
                        stats["difficulty"] = float(line_lower.split("difficulty:")[-1].strip().replace(",", ""))
                    except:
                        pass
                elif "daa score:" in line_lower:
                    try:
                        stats["daaScore"] = int(line_lower.split("daa score:")[-1].strip().replace(",", ""))
                        stats["blueScore"] = stats["daaScore"]
                    except:
                        pass
                elif "pruning point:" in line_lower:
                    try:
                        pp = line_lower.split("pruning point:")[-1].strip().replace(",", "")
                        stats["pruningPoint"] = pp[:16] + "..."
                    except:
                        pass
        except:
            pass
        
        # Read log file for realtime stats
        if os.path.exists(LOG_FILE):
            try:
                with open(LOG_FILE, 'r', encoding='utf-8', errors='replace') as f:
                    lines = f.readlines()[-500:]
            except Exception as e:
                lines = []
            
            for line in reversed(lines):
                if "Block count:" in line and not stats["blockCount"]:
                    match = re.search(r'Block count:\s*(\d+)', line)
                    if match:
                        stats["blockCount"] = int(match.group(1))
                
                if "Header count:" in line and not stats["headerCount"]:
                    match = re.search(r'Header count:\s*(\d+)', line)
                    if match:
                        stats["headerCount"] = int(match.group(1))
                
                if "Difficulty:" in line and not stats["difficulty"]:
                    match = re.search(r'Difficulty:\s*([\d.]+)', line)
                    if match:
                        stats["difficulty"] = float(match.group(1))
                
                if "DAA score:" in line:
                    match = re.search(r'DAA score:\s*(\d+)', line)
                    if match:
                        stats["blueScore"] = int(match.group(1))
                        stats["daaScore"] = int(match.group(1))
                
                if "Pruning point:" in line and not stats["pruningPoint"]:
                    match = re.search(r'Pruning point:\s*([a-f0-9]+)', line)
                    if match:
                        stats["pruningPoint"] = match.group(1)[:16] + "..."
                
                if "Accepted" in line and "blocks" in line:
                    match = re.search(r'Accepted\s+(\d+)\s+blocks\s+\.\.\.([a-f0-9]+)', line)
                    if match:
                        stats["blockRate"] = int(match.group(1))
                        block_hash = match.group(2)
                        if block_hash not in [b['hash'] for b in stats["recentBlocks"]]:
                            stats["recentBlocks"].append({
                                "hash": block_hash[:16] + "...",
                                "fullHash": block_hash,
                                "blueScore": stats["blueScore"]
                            })
                            if len(stats["recentBlocks"]) > 10:
                                stats["recentBlocks"] = stats["recentBlocks"][:10]
                
                if "Tx throughput" in line:
                    match = re.search(r'([\d.]+)\s+u-tps', line)
                    if match:
                        stats["txRate"] = float(match.group(1))
        
        # Get peers
        try:
            result = subprocess.run(
                ["lsof", "-i", ":16311"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            stats["peers"] = len([l for l in result.stdout.split('\n') if "ESTABLISHED" in l])
        except:
            stats["peers"] = 0
        
    except Exception as e:
        stats["error"] = str(e)
    
    return stats

@app.route('/')
def index():
    resp = make_response(render_template('index.html'))
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp

@app.route('/api/stats')
def api_stats():
    resp = make_response(jsonify(get_node_stats()))
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp

@app.route('/api/log')
def api_log():
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r') as f:
                lines = f.readlines()[-50:]
            return jsonify({"lines": lines, "success": True})
    except Exception as e:
        return jsonify({"error": str(e), "success": False})

@app.route('/deadman')
def deadman():
    return render_template('deadman.html')

@app.route('/api/deadman/generate-keys', methods=['POST'])
def deadman_generate_keys():
    """Generate a new keypair for deadman switch"""
    try:
        # Use openssl to generate a keypair
        # Generate private key
        priv_proc = subprocess.Popen(
            ["openssl", "ecparam", "-genkey", "-name", "secp256k1"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        priv_der, _ = priv_proc.communicate(timeout=10)
        
        # Get public key from private key
        pub_proc = subprocess.Popen(
            ["openssl", "ec", "-pubout"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        pub_pem, _ = pub_proc.communicate(input=priv_der, timeout=10)
        
        # Convert PEM to hex (uncompressed format)
        # Skip header/footer and decode base64
        import base64
        pub_pem_str = pub_pem.decode('utf-8')
        pub_lines = pub_pem_str.split('\n')
        pub_b64 = ''.join([l for l in pub_lines if not l.startswith('-----')])
        pub_der2 = base64.b64decode(pub_b64)
        
        # DER to uncompressed hex (04 + X + Y)
        # Skip ASN.1 header and get 65 bytes (33 + 32)
        pub_hex = pub_der2.hex()
        # Find the uncompressed pubkey (starts with 04)
        idx = pub_hex.find('04')
        if idx >= 0:
            pub_key = pub_hex[idx:idx+130]  # 04 + 64 bytes = 130 chars
        else:
            pub_key = "04" + pub_hex[-128:]  # Fallback
        
        return jsonify({"success": True, "publicKey": pub_key})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/deadman/create-args', methods=['POST'])
def deadman_create_args():
    """Generate constructor arguments for deadman switch"""
    try:
        import json
        data = request.get_json()
        owner_pubkey = data.get('ownerPubkey', '')
        beneficiary_pubkey = data.get('beneficiaryPubkey', '')
        timeout = int(data.get('timeout', 31536000))
        
        # Convert hex pubkeys to byte arrays
        def hex_to_bytes(hex_str):
            if hex_str.startswith('0x'):
                hex_str = hex_str[2:]
            return [int(hex_str[i:i+2], 16) for i in range(0, len(hex_str), 2)]
        
        owner_bytes = hex_to_bytes(owner_pubkey)
        beneficiary_bytes = hex_to_bytes(beneficiary_pubkey)
        
        args = [
            {"kind": "bytes", "data": owner_bytes},
            {"kind": "bytes", "data": beneficiary_bytes},
            {"kind": "int", "data": timeout}
        ]
        
        return jsonify({"success": True, "args": args})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/deadman/check-utxo', methods=['GET'])
def deadman_check_utxo():
    """Check if a contract address has UTXOs"""
    try:
        address = request.args.get('address', '')
        if not address:
            return jsonify({"success": False, "error": "No address provided"})
        
        # Query UTXOs via rothschild (quick check)
        result = subprocess.run(
            f"echo '{{\"id\":1,\"method\":\"getUTXOsByAddresses\",\"params\":{{\"addresses\":[\"{address}\"]}}}}' | nc -w 5 localhost 18210",
            shell=True,
            capture_output=True,
            timeout=10,
            text=True
        )
        
        return jsonify({"success": True, "utxoResponse": result.stdout})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/deadman/contracts', methods=['GET', 'POST'])
def deadman_contracts():
    """Manage deadman switch contracts"""
    import json
    
    # Simple file-based storage for contracts
    CONTRACTS_FILE = os.path.expanduser("~/.kaspa_dashboard/deadman_contracts.json")
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(CONTRACTS_FILE), exist_ok=True)
    
    # Load existing contracts
    try:
        if os.path.exists(CONTRACTS_FILE):
            with open(CONTRACTS_FILE, 'r') as f:
                contracts = json.load(f)
        else:
            contracts = []
    except:
        contracts = []
    
    if request.method == 'POST':
        data = request.get_json()
        action = data.get('action', '')
        
        if action == 'add':
            contracts.append({
                'address': data.get('address', ''),
                'ownerPubkey': data.get('ownerPubkey', ''),
                'beneficiaryPubkey': data.get('beneficiaryPubkey', ''),
                'timeout': data.get('timeout', 0),
                'created': time.time()
            })
            
            with open(CONTRACTS_FILE, 'w') as f:
                json.dump(contracts, f)
            
            return jsonify({"success": True})
        
        elif action == 'remove':
            address = data.get('address', '')
            contracts = [c for c in contracts if c.get('address') != address]
            
            with open(CONTRACTS_FILE, 'w') as f:
                json.dump(contracts, f)
            
            return jsonify({"success": True})
    
    return jsonify({"success": True, "contracts": contracts})

if __name__ == '__main__':
    print(f"Starting Kaspa Dashboard on http://localhost:{PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=False)
