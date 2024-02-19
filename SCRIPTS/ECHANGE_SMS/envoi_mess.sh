#!/bin/sh

message="Attention ! La prise semble être en surchauffe, la température enregistrée est de : "
param=$1

msg_final="$message $param"

echo $message
echo $param
echo $msg_final

gammu sendsms TEXT 0679401999 -text "$msg_final"
