#!/bin/bash
echo "Start tap-billwerk sync of incremental tables" 
cd /home/ubuntu/billwerkreporting
/home/ubuntu/.virtualenvs/tap-billwerk/bin/tap-billwerk --config config.json --catalog catalog_incremental.json --state state.json | /home/ubuntu/.virtualenvs/target-stitch/bin/target-stitch --config target-stitch-config.json >> state.json | tail -1 state.json > state.json.tmp && mv state.json.tmp state.json
