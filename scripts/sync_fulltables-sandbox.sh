#!/bin/bash
echo "Start tap-billwerk sync of full  tables" 
cd /home/ubuntu/billwerkreporting
/home/ubuntu/.virtualenvs/tap-billwerk/bin/tap-billwerk --config config.json --catalog catalog.json | /home/ubuntu/.virtualenvs/target-stitch/bin/target-stitch --config target-stitch-config.json
