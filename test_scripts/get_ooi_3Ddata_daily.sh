
FILES=/home/sbaker/scripts/config/*.3dcfg
for f in $FILES
do
  echo $f
  date && python $HOME/scripts/loadData_3D.py $f day /var/www/html/ooi/images
  sleep 1
done

