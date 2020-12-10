#!/bin/bash
echo "Start tap-billwerk sync of incremental tables - Live Environment" 
cd /home/ubuntu/billwerkreporting
/home/ubuntu/.virtualenvs/tap-billwerk/bin/tap-billwerk --config config-live.json --catalog catalog_incremental.json --state state-live.json | /home/ubuntu/.virtualenvs/target-stitch/bin/target-stitch --config target-stitch-live-config.json >> state-live.json 
tail -1 state-live.json > state.json.tmp && mv state.json.tmp state-live.json
