#!/bin/bash
echo "Start tap-billwerk sync of incremental tables" 
cd /home/ubuntu/billwerkreporting
/home/ubuntu/.virtualenvs/tap-billwerk/bin/tap-billwerk --config config-sandbox.json --catalog catalog_incremental.json --state state-sandbox.json | /home/ubuntu/.virtualenvs/target-stitch/bin/target-stitch --config target-stitch-sandbox-config.json >> state-sandbox.json
tail -1 state-sandbox.json > state.json.tmp && mv state.json.tmp state-sandbox.json

