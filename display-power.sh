#!/bin/bash
#Version 2.0.0

#Accepts 1 argument of either TOGGLE, ON, OFF

#xset_cmd='/usr/bin/xset'
arg=$1
vcgen_cmd='/usr/bin/vcgencmd'
cut_cmd='/usr/bin/cut'
sleep_cmd='/usr/bin/sleep'
mqttpub_cmd='/usr/bin/mosquitto_pub'
#grep_cmd='/usr/bin/grep'

#vcgencmd outputs display_power=0 for off and =1 for on
function is_off() {
  result=`$vcgen_cmd display_power |$cut_cmd -d= -f2`
  return $result
}

function turn_off() {
  $vcgen_cmd display_power 0
  $mqttpub_cmd -t frame/state -m OFF -q 0 -r
}

function turn_on() {
  $vcgen_cmd display_power 1
  $mqttpub_cmd -t frame/state -m ON -q 0 -r
}

function toggle() {
  if is_off
  then
    turn_on()
    # delay & restart monitor process to prevent accidental multi touches from queueing
    $sleep_cmd 1
    systemctl --user restart touch-monitor

  else
    turn_off()
    # delay & restart monitor process to prevent accidental multi touches from queueing
    $sleep_cmd 1
    systemctl --user restart touch-monitor

  fi
}

if [ "$arg" == "TOGGLE" ]
then
  toggle
elif [ "$arg" == "OFF" ]
then
  turn_off
elif [ "$arg" == "ON" ]
then
  turn_on
fi
