#!/bin/bash

# Clear script and settings first
sudo rm /etc/init.d/miner >/dev/null 2>&1
sudo update-rc.d miner remove >/dev/null 2>&1
sudo cp miner /etc/init.d/
sudo chmod 777 /etc/init.d/miner
sudo update-rc.d miner defaults

sudo chmod 777 minerDaemon
sudo cp minerDaemon ../
