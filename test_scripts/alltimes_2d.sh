#!/bin/bash
python -W ignore $HOME/ooi-plotter/loadData.py $HOME/ooi-plotter/config/$1 day /var/www/html/kcrtest/images
python -W ignore $HOME/ooi-plotter/loadData.py $HOME/ooi-plotter/config/$1 week /var/www/html/kcrtest/images
python -W ignore $HOME/ooi-plotter/loadData.py $HOME/ooi-plotter/config/$1 month /var/www/html/kcrtest/images
python -W ignore $HOME/ooi-plotter/loadData.py $HOME/ooi-plotter/config/$1 year /var/www/html/kcrtest/images
