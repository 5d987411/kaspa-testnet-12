#!/bin/bash

case "$1" in
  start)
    echo "Starting kaspad testnet 12..."
    nohup /Users/4dsto/kaspa-node/kaspa-testnet-12-main/kaspad --testnet --netsuffix=12 --utxoindex --appdir ~/.kaspa-testnet12 > /tmp/kaspad_tn12.log 2>&1 &
    echo $! > /tmp/kaspad.pid
    echo "Kaspad started with PID: $(cat /tmp/kaspad.pid)"
    sleep 2
    
    echo "Starting dashboard..."
    cd /Users/4dsto/kaspa-node/dashboard
    nohup python3 server.py > /tmp/dashboard.log 2>&1 &
    echo $! > /tmp/dashboard.pid
    echo "Dashboard started with PID: $(cat /tmp/dashboard.pid)"
    echo ""
    echo "Dashboard: http://localhost:8080"
    ;;
  stop)
    echo "Stopping services..."
    [ -f /tmp/kaspad.pid ] && kill $(cat /tmp/kaspad.pid) && rm /tmp/kaspad.pid
    [ -f /tmp/dashboard.pid ] && kill $(cat /tmp/dashboard.pid) && rm /tmp/dashboard.pid
    echo "Stopped"
    ;;
  status)
    echo "=== Kaspad ==="
    if [ -f /tmp/kaspad.pid ] && kill -0 $(cat /tmp/kaspad.pid) 2>/dev/null; then
      echo "Running (PID: $(cat /tmp/kaspad.pid))"
      tail -5 /tmp/kaspad_tn12.log
    else
      echo "Not running"
    fi
    echo ""
    echo "=== Dashboard ==="
    if [ -f /tmp/dashboard.pid ] && kill -0 $(cat /tmp/dashboard.pid) 2>/dev/null; then
      echo "Running (PID: $(cat /tmp/dashboard.pid))"
    else
      echo "Not running"
    fi
    ;;
  log)
    tail -f /tmp/kaspad_tn12.log
    ;;
  *)
    echo "Usage: $0 {start|stop|status|log}"
    exit 1
    ;;
esac
