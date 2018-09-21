

FILES=$HOME/ooi-plotter/config/*.cfg
for f in $FILES
do
  date && python -W ignore $HOME/ooi-plotter/loadData.py $f week /var/www/html/kcrtest/images
  sleep 1
done

