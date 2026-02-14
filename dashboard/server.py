#!/usr/bin/env python3
"""
Simple Flask server for Kaspa Dashboard
Serves the dashboard and proxies log data
"""

from flask import Flask, render_template, jsonify, Response, make_response
import subprocess
import threading
import time
import os
import re

app = Flask(__name__)

LOG_FILE = "/tmp/kaspad.log"
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

if __name__ == '__main__':
    print(f"Starting Kaspa Dashboard on http://localhost:{PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=False)
