
FILES=/home/krosburg/ooi-plotter/config/*.cfg
for f in $FILES
do
  echo -n "$(echo $f | cut -d'/' -f6) - "
  date && python -W ignore $HOME/ooi-plotter/loadData.py $f month /var/www/html/kcrtest/images && echo " "
  sleep 1
done

