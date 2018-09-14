
FILES=/home/sbaker/scripts/config/*.3dcfg
for f in $FILES
do
  date && python $HOME/scripts/loadData_3D.py $f week /var/www/html/ooi/images
  sleep 1
done

