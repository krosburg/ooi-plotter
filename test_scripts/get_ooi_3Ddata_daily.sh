
FILES=$HOME/ooi-plotter/config/*.3dcfg
for f in $FILES
do
  echo -n "$(echo $f | cut -d'/' -f6) - "
  date && python -W ignore $HOME/ooi-plotter/loadData_3D.py $f day /var/www/html/kcrtest/images && echo " "
  sleep 1
done
