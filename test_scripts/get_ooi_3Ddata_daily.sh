
FILES=$HOME/ooi-plotter/config/*.3dcfg
for f in $FILES
do
  echo $f
  date && python $HOME/ooi-plotter/loadData_3D.py $f day /var/www/html/kcrtest/images
  sleep 1
done

