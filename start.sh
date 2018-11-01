#!/bin/bash
echo 'Starting fatController'
nohup ./boss.py &
sleep 1
echo 'Starting talker1'
nohup ./talker1.py &
#echo 'Starting middelMan'
#nohup ./middleMan.py &
#echo 'Starting message Loader'
#nohup ./run_msg_loader.py &
