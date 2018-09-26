import requests
import numpy as np
import pandas as pd
import json
from datetime import datetime, timedelta
from configparser import ConfigParser
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from PIL import Image
from os import remove


#### EPOCH_TO_DT() ###########################################################
# Convert epoch date to datetime for plotting
def epoch_to_dt(t):

    # Setup Offsets
    offset = datetime(1970, 1, 1, 0, 0, 0)-datetime(1900, 1, 1, 0, 0 ,0)
    off_sec = timedelta.total_seconds(offset)

    # Convert using offsets
    t_datetime = []
    for tt in t:
        t_sec = tt - off_sec
        t_datetime.append(datetime.utcfromtimestamp(t_sec))

    return t_datetime
###############################################################################



#### READ_CONFIG_HELPER() ######################################################
# Given an configuration parameter name and cfg section, parses config info
def read_config_helper(config,param_name,s):
    key_str = config.get(s,param_name)
    if key_str == None:
        print('Warning: ' + param_name + ' is missing from config file')
        exit(0)
    else:
        if param_name == 'pdNumsString':
            return key_str
        elif len(key_str.split(',')) > 1:
            return key_str.split(',')
        else:
            return key_str
###############################################################################



#### READ_CONFIG()############################################################
# Reads and parses .3dcfg config files
def read_config(params_list,cfg_file):
    # Initialzie config object and read file
    config = ConfigParser()
    config.read(cfg_file)

    # Define config dictionary and read in parameters
    cfg = {}
    for s in config.sections():
        # Retrieve Title
        param = {}
        param['title'] = s

        # Parse non-optional parameters
        for param_name in params_list:
            param[param_name] = read_config_helper(config,param_name,s)

        # Parse optional parameters
        if config.has_option(s,'scalar'): param['scalar'] = config.get(s,'scalar')
        else: param['scalar'] = 1
        
        if config.has_option(s,'opOff'): param['opOff'] = int(config.get(s,'opOff'))
        else: param['opOff'] = 0

        # Add to configutation list
        cfg[s] = param

    return cfg
###############################################################################


#### GET_OFFSET() ############################################################
def get_offset(time_window):
    # Case statement that returns the time offset given a time_window string.
    if time_window == 'day':
        return 1
    elif time_window == 'week':
        return 7
    elif time_window == 'month':
        return 30
    elif time_window == 'year':
        return 365 
    else:
        raise Exception('Interval time not specified')
###############################################################################


#### GET_DATA() ##############################################################
def get_data(req_url, username, token):
    # Given a request URL, returns a json element with the data from M2M
    SUCCESS_CODE = 200
    try:
        raw_data = requests.get(req_url, auth=(username, token),
                                timeout=10,
                                verify=False)
        if raw_data.status_code != SUCCESS_CODE:
            print('Error: status code ', raw_data.status_code)
            print('Error: response.json(): ', raw_data.json())
            return []
            
        return raw_data.json()

    except Exception as err:
        print('Exception: %s' % str(err))
        return []
###############################################################################


#### GET_ARGS() ##############################################################
def get_args():
    # Retrieves important arguments from the command line
    if len(sys.argv) < 3:
        raise Exception('Not enough arguments')
    else:
        config_file = sys.argv[1]
        time_window = sys.argv[2]
        if len(sys.argv) >= 4:
            dest_dir = sys.argv[3]
        else:
            dest_dir = './'
        return config_file,time_window,dest_dir
###############################################################################


#### PARSE_DATA() ############################################################
def parse_data(raw_data, params):
    # Given a raw json data from m2m and a list of params from the cfg
    # file, parses the data as necesary for plotting.
    x, y, z = [], [] ,[]
    for data in raw_data:
        x.append(data[params['xParam']])
        y.append(data[params['yParam']])
        z.append(data[params['zParam']])
    
    # Convert x, y, z to numpy arrays
    x = np.array(x, dtype=np.float)
    y = np.array(y, dtype=np.float)
    z = np.array(z, dtype=np.float).transpose() * np.float(params['scalar'])

    # Convert Time if Needed
    if params['xParam'] == 'time':
        x = epoch_to_dt(x)
        x = mdates.date2num(x)

    # Remove Fill Values from Y
    y[y <= -9999998.0] = float('NaN')

    # If 2D y, select 1st 1D non-NaN 1D array
    try:
        y.shape[1]
        cnt = 0
        while np.isnan(y[cnt][1]):
            cnt = cnt + 1
        y = y[cnt]
    except Exception:
        #None
        print("probrem!")

    # Remove Z Fill Values
    z[z > 9999998.0] = float('NaN')
    z[z < -9999998.0] = float('NaN')
    z[z == -9999999.0] = float('NaN')

    return x, y, z
###############################################################################


# Set Up Auth and request variables
from ooicreds import USERNAME, TOKEN, BASE_URL
limit = '1000'


# Retrieve arguments
config_file, time_window, dest_dir = get_args()
    
# Reformat Destination Directory
if dest_dir[-1] != '/':
    dest_dir = dest_dir + '/'

# Setup Time Offset
offset = get_offset(time_window)

# Create Start and End Dates
t_end = datetime.utcnow().isoformat() + 'Z'
dt_end = datetime.strptime(t_end, '%Y-%m-%dT%H:%M:%S.%fZ')
dt_start = dt_end - timedelta(days=offset)
t_start = dt_start.isoformat() + 'Z'

# Define Other Variables
label_size = 20
cfg_dir = '/home/sbaker/scripts/config/'
params_list = ['dbKeyNames', 'xParam', 'yParam',
               'zParam', 'streamName', 'pdNumsString',
               'yaxisInterval', 'precision', 'yunits', 'zunits']


# Read in the configuration file
cfg = read_config(params_list, config_file)


# Loop on all elements in configuration file
for cBlock in cfg:
    params = cfg.get(cBlock)

    # Setup Request Variables
    req_url = BASE_URL + params['streamName'] + '?beginDT=' + t_start \
                       + '&endDT=' + t_end + '&limit=' + limit \
                       + '&parameters=' + params['pdNumsString']

    # Setup Plot
    fig = plt.figure(figsize=(18,4.475))

    # Get data
    raw_data = get_data(req_url, USERNAME, TOKEN)

    # If device is oprationally off, print a green message
    failFlag = False
    if params['opOff'] == 1:
        failFlag = True
        print(params['title']+' operationally off. Skipping.')
        plt.plot()
        plt.text(0, 0, 'OPERATIONALLY OFFLINE',
                 ha='center', va='center', size=60, color='green')
        plt.text(0, -0.02, 'No need for concern!',
                 ha='center', va='center', size=40, color='black')

    # If no data returned, print a red error message
    elif not raw_data:
        failFlag = True
        print('No data for '+params['title']+'. Skipping.')
        plt.plot()
        plt.text(0, 0, 'ERROR',
                 ha='center', va='center', size=60, color='red')
        plt.text(0, -0.02, 'No Data Returned from M2M Query',
                 ha='center', va='center', size=40, color='black')

    # If device is functioning off, plot the datas as usual
    else:
        # Parse Data
        x, y, z = parse_data(raw_data, params)

        # Plot
        # Contour and add colorbar
        minval = np.nanmin(z)
        maxval = np.nanmax(z)
        avgval = np.nanmean(z)
        CS = plt.pcolor(x, y, z, cmap=plt.get_cmap('RdBu_r'),
                        vmin=minval, vmax=maxval)
        CS.cmap.set_under('white')

        # Colorbar
        cb = plt.colorbar()
        cb.set_label(r'($%s$)' % params['zunits'])

        # Add Grid
        plt.grid(True, linestyle='dashed', linewidth=2)
        
        # Set Axes Limits
        if params['yParam'] == 'bin_depths':
            ylims = [np.nanmax(y), np.nanmin(y)]
        else:
            ylims = [np.nanmin(y), np.nanmax(y)]
        plt.ylim(ylims)
        plt.xlim(mdates.date2num([dt_start, dt_end]))

        # Format Xticks
        ax = plt.gca()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M\n%m-%d'))

    # Add Title and Y label
    plt.ylabel(params['yParam'].replace('_', ' ') + ' ($' + params['yunits'] + '$)', fontsize=label_size)
    plt.title(params['title'], fontsize=label_size)
    if not failFlag:
        plt.xlabel("Min=%2.2f, Max=%2.2f, Avg=%2.2f" % (minval, maxval, avgval))

    # Save Figure
    parts = params['streamName'].split('/')
    region = parts[0]
    node = parts[1]
    inst = parts[2][3:]
    rID = region + '-' + node + '-'
    fig_file = dest_dir + time_window + '/' + rID + params['title']
    plt.savefig(fig_file + '.png', bbox_inches='tight')
    Image.open(fig_file + '.png').convert('RGB').save(fig_file + '.jpg', 'JPEG')
    remove(fig_file + '.png')
    print(fig_file + '.png updated')
