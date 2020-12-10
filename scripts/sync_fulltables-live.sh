#!/bin/bash
echo "Start tap-billwerk sync of full  tables" 
cd /home/ubuntu/billwerkreporting
/home/ubuntu/.virtualenvs/tap-billwerk/bin/tap-billwerk --config config-live.json --catalog catalog.json | /home/ubuntu/.virtualenvs/target-stitch/bin/target-stitch --config target-stitch-live-config.json
