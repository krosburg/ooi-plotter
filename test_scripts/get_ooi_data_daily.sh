

FILES=$HOME/ooi-plotter/config/*.cfg
#rm -f /var/www/html/status/inst_status_m2m.csv
for f in $FILES
do
    echo -n "$(echo $f | cut -d'/' -f6) - "
    source activate py36
    date && $HOME/miniconda3/bin/python -W ignore $HOME/ooi-plotter/loadData.py $f day /var/www/html/kcrtest/images && echo " "
  sleep 1
done
mv -f /var/www/html/status/inst_status_m2m.csv.tmp /var/www/html/status/inst_status_m2m.csv

