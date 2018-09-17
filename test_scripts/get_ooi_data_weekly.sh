
BASE=~/Documents/Work/Code/plot_v2
FILES=$BASE/config/*.cfg
for f in $FILES
do
  date && python -W ignore $BASE/loadData.py $f week $BASE/images
  sleep 1
done

