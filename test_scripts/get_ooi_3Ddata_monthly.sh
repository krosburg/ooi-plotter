
FILES=/home/krosburg/ooi-plotter/config/*.3dcfg
for f in $FILES
do
  date && python -W ignore $HOME/ooi-plotter/loadData_3D.py $f month /var/www/html/kcrtest/images
  sleep 1
done

