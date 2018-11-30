from PIL import Image
from os import remove
from datetime import datetime, timedelta
from configparser import ConfigParser
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import requests
import sys


##### EPOCH_TO_DT() ###########################################################
def epoch_to_dt(t):
    # Convert epoch date to datetime for plotting

    # Setup Offsets
    offset = datetime(1970, 1, 1, 0, 0, 0)-datetime(1900, 1, 1, 0, 0, 0)
    off_sec = timedelta.total_seconds(offset)

    # Convert using offsets
    t_datetime = []
    for tt in t:
        t_sec = tt - off_sec
        t_datetime.append(datetime.utcfromtimestamp(t_sec))

    return t_datetime
###############################################################################


##### READ_CONFIG_HELPER() ####################################################
def read_config_helper(config, param_name, s):
    # Given an configuration parameter name and cfg section, parses config info
    key_str = config.get(s, param_name)
    if key_str is None:
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


##### READ_CONFIG()############################################################
def read_config(params_list, cfg_file):
    # Reads and parses .cfg config files

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
            param[param_name] = read_config_helper(config, param_name, s)

        # Parse optional parameters
        if config.has_option(s, 'scalar'):
            param['scalar'] = float(config.get(s, 'scalar'))
        else:
            param['scalar'] = 1.0

        if config.has_option(s, 'opOff'):
            param['opOff'] = int(config.get(s, 'opOff'))
        else:
            param['opOff'] = 0

        if config.has_option(s, 'vectorIndex'):
            param['vectorIndex'] = int(config.get(s, 'vectorIndex'))
        else:
            param['vectorIndex'] = float('NaN')

        # Add to configutation list
        cfg[s] = param

    return cfg
###############################################################################


##### UPDATE_STATUS() #########################################################
def updateStatus(t, end_want, stream):
    ref_desg = stream.split('/streamed')[0].replace('/', '-')
    t_now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
    if not t:
        end_time = "---"
        t_diff = float('NaN')
        status = -1
    else:
        end_time = np.nanmax(t)
        t_diff = end_want - end_time
        t_diff = t_diff.days*86400 + t_diff.seconds + t_diff.microseconds*1E-6
        # If diff less than 12 hr --> Green
        if t_diff <= 86400/2.0:
            status = 0
        # If diff less than 24 hr --> Yellow
        elif t_diff <= 86400.0:
            status = 1
        # If Diff greater than 24 hr --> Red :(
        else:
            status = 2

        # Process End Time for Errors
        if t_diff >= 10*365*86400:
            end_time = "---"
        else:
            end_time = end_time.strftime('%Y-%m-%d %H:%M:%S UTC')
    f = open(status_file, 'a+')
    f.write("%s,%s,%s,%2.4f,%i\n" % (ref_desg, t_now, end_time, t_diff, status))
    f.close()
    
###############################################################################


##### GET_OFFSET() ############################################################
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


##### GET_DATA() ##############################################################
def get_data(req_url, username, token):
    # Given a request URL, returns a json element with the data from M2M
    SUCCESS_CODE = 200
    try:
        raw_data = requests.get(req_url, auth=(username, token),
                                timeout=10, verify=False)
        if raw_data.status_code != SUCCESS_CODE:
            print('Error: status code ', raw_data.status_code)
            print('Error: response.json(): ', raw_data.json())
            return []

        return raw_data.json()

    except Exception as err:
        print('Exception: %s' % str(err))
        return []
###############################################################################


##### GET_ARGS() ##############################################################
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
        return config_file, time_window, dest_dir
###############################################################################


# Set Up Auth and request variables
from ooicreds import USERNAME, TOKEN, BASE_URL
limit = '1000'

# Retrieve arguments
config_file, time_window, dest_dir = get_args()

# Add trailing slash to destination directory if not there
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
label_size = 23
title_size = 30
value_size = 22
legtx_size = 24
label_wt = "bold"
title_wt = "bold"
cfg_dir = '/home/sbaker/scripts/config/'
status_file = '/var/www/html/status/inst_status_m2m.csv'
params_list = ['streamName', 'paramNames',
               'dbKeyNames', 'pdNumsString',
               'units']

# Read in the configuration file
cfg = read_config(params_list, config_file)

# Loop on all elements in configuration file
status_flag = True
for cBlock in cfg:
    params = cfg.get(cBlock)

    # Setup Request Variables
    req_url = BASE_URL + params['streamName'] + '?beginDT=' + t_start \
                       + '&endDT=' + t_end + '&limit=' + limit \
                       + '&parameters=' + params['pdNumsString']

    # Setup Plot
    fig = plt.figure(figsize=(18, 4.475))

    # Get data
    raw_data = get_data(req_url, USERNAME, TOKEN)

    # Convert data to Pandas Frame
    data = pd.DataFrame.from_records(raw_data)

    # Extract parameter names
    pnames = params['paramNames'][0:-1]

    #  If device is oprationally off, print a green message
    failFlag = False
    if params['opOff'] == 1:
        failFlag = True
        if "day" in time_window and status_flag:
            updateStatus([], dt_end, params['streamName'])
            status_flag = False
        print(params['title']+' operationally off. Skipping.')
        plt.plot()
        plt.text(0, 0, 'OPERATIONALLY OFFLINE',
                 ha='center', va='center', size=60, color='green')
        plt.text(0, -0.02, 'No need for concern!',
                 ha='center', va='center', size=40, color='black')

    # If no data returned, print a red error message
    elif not raw_data:
        failFlag = True
        if "day" in time_window and status_flag:
            updateStatus(datetime(1,1,1), dt_end, params['streamName'])
            status_flag = False
        print('No data for '+params['title']+'. Skipping.')
        plt.plot()
        plt.text(0, 0, 'ERROR',
                 ha='center', va='center', size=60, color='red')
        plt.text(0, -0.02, 'No Data Returned from M2M Query',
                 ha='center', va='center', size=40, color='black')

    # If device is functioning, plot the datas as usual
    else:

        # Get the time variable
        t = epoch_to_dt(np.array(data['time'], dtype=np.float))

        # Write to Status File
        if "day" in time_window and status_flag:
            updateStatus(t, dt_end, params['streamName'])
            status_flag = False

        # Extract non-time variables
        minvals, maxvals, avgvals = [], [], []
        for pname in pnames:
            # Get Data from data frame
            if ~np.isnan(params['vectorIndex']):
                if "SPKIRA" in config_file:
                    x = []
                    for xx in data[pname]:
                        x.append(xx[params['vectorIndex']])
                    x = np.array(x, dtype=np.float)
                else:
                    x = np.array(data[pname][params['vectorIndex']])
                x = x*np.float(params['scalar'])
            elif "PCO2WA105" in config_file:
                x = []
                for dat in raw_data:
                    x.append(dat[pname])
                x = np.array(x, dtype=np.float)*np.float(params['scalar'])
            else:
                x = np.array(data[pname], dtype=np.float)*np.float(params['scalar'])
            x[x <= -9.99e6] = float('NaN')

            # Store min/max/mean values
            minvals.append(np.nanmin(x))
            maxvals.append(np.nanmax(x))
            avgvals.append(np.nanmean(x))

            # Create label string
            labStr = '%s: min=%2.2f, max=%2.2f, mean=%2.2f' % (pname,
                                                               minvals[-1],
                                                               maxvals[-1],
                                                               avgvals[-1])

            # Plot variable vs time
            plt.plot(mdates.date2num(t), x, linewidth=3, label=labStr)

        # Add Grid
        plt.grid(True, linestyle='dashed', linewidth=2)

        # Will need to create ylims here tho eventually

        # Set Axes Limits
        plt.ylim(min(minvals), max(maxvals))
        plt.xlim(mdates.date2num([dt_start, dt_end]))

        # Format Xticks
        ax = plt.gca()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M\n%m/%d/%y'))
        plt.tick_params(labelsize=value_size)

    # Add Title and Y label
    ylab_str = '($' + params['units'] + '$)'
    titl_str = params['title'].replace('_', ' ')
    plt.ylabel(ylab_str, fontsize=label_size, fontweight=label_wt)
    plt.title(titl_str, fontsize=title_size, fontweight=title_wt)

    # Add Legend
    box_y = -.50*(1 + ((len(pnames)-1)*.225))
    lgd = plt.legend(loc='lower right', bbox_to_anchor=(1.005, box_y),
                     fontsize=legtx_size, frameon=False)

    # Save Figure
    parts = params['streamName'].split('/')
    region = parts[0]
    node = parts[1]
    inst = parts[2][3:]
    rID = region + '-' + node + '-'
    fig_file = dest_dir + time_window + '/' + rID + params['title']
    #fig_file = dest_dir + time_window + '/' + params['title']
    if not failFlag:
        plt.savefig(fig_file+'.png', bbox_extra_artists=(lgd,), bbox_inches='tight')
    else:
        plt.savefig(fig_file+'.png', bbox_inches='tight')
    Image.open(fig_file+'.png').convert('RGB').save(fig_file + '.jpg', 'JPEG')
    remove(fig_file + '.png')
    print(fig_file + '.png updated')
