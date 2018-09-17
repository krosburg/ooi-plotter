
#FILES=/home/sbaker/scripts/config/*.cfg
FILES=../config/*.cfg
for f in $FILES
do
  date && python ../loadData.py $f week ../images
  sleep 1
done

