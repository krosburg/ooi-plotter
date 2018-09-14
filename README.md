# ooi-plotter
This is a package that contains automated plotting routines for plotting line and contour plots of OOI data, given a configuration file.

## Configuration files
Config files can be found in:
<code>./config</code>

Two types of configuration files exist:
<code>*.cfg</code>
and
<code>*.3dcfg</code>
The prior controls plotting of x vs. y plots, or line plots, while the latter controls the plotting of contour plots.

## Syntax
To create line plots for an instrument, use the following syntax:

<code>python -W ignore newloadData.py <config-file> <time-window> <output-dir></code>

For example:
<code>python -W ignore newloadData.py ADCPTE101.cfg month /var/www/html/images</code>
would create one-month plots for ADCPTE101 and store them in the images file on the local webserver. Note, that the script will automatically deposit the images into a subdirectory matching the time-window (i.e. /var/www/html/images/month/).

Likewise, <code>python -W ignore loadData_3D.py ADCPTE101.3dcfg week</code> would create one-week plots for ADCPTE101 and store them in <code>./week/</code>. Yes that's right folks, the third argument is optional. If ommitted, the code defaults to <code>$PWD</code>, and again uses a subdirectory matching the time-window.
''Note: at this time, if the subdirectories day/week/month/year are not created the code will error and fail. It's on the to-do list.''
