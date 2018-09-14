
FILES=/home/sbaker/scripts/config/*.cfg
for f in $FILES
do
  date && python $HOME/scripts/loadData.py $f month /var/www/html/ooi
  sleep 1
done

