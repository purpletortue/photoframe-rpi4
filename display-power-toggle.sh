#!/bin/bash
#Version 1.0.0

#xset_cmd='/usr/bin/xset'
vcgen_cmd='/usr/bin/vcgencmd'
cut_cmd='/usr/bin/cut'
#grep_cmd='/usr/bin/grep'

#vcgencmd outputs display_power=0 for off and =1 for on
function is_off() {
  result=`$vcgen_cmd display_power |$cut_cmd -d= -f2`
  return $result
}

if is_off
then
  #turn on
  $vcgen_cmd display_power 1
else
  #turn off
  $vcgen_cmd display_power 0
fi
