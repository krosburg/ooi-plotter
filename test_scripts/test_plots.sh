#!/bin/bash

## Variables
CFGDIR='/home/sbaker/scripts/config/'
WWWDIR='/var/www/html/ooi'
SCRLOC='/home/sbaker/scripts/loadData.py'
declare -a intervals=("day" "week" "month" "year")

## Change to correct directory
cd $CFGDIR

## Get Config script from args
if [ $# -lt 1 ]; then
    echo "Make sure to supply the config file!"
    exit 1
else
    CFGFILE="$1"
fi
echo "Using $CFGFILE"
    
# Loop on intervals and generate images
for i in "${intervals[@]}"
do
    echo "Running command for $i interval..."

    ## Assemble Command
    CMD="python $SCRLOC $CFGFILE $i $WWWDIR"
    $CMD
    
done
