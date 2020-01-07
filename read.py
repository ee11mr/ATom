import numpy as np
import pandas as pd
from netCDF4 import Dataset
from datetime import datetime
import matplotlib.pyplot as plt
path='/users/mjr583/scratch/ATom/ATom_merge_1581/data/'
savepath='/users/mjr583/scratch/ATom/plots/'
species=['acetaldehyde','acetone','meoh']
for spec in species:
    if spec == 'acetaldehyde':
        ATinput='CH3CHO_TOGA'
    elif spec=='acetone':
        ATinput='Acetone_TOGA'
    elif spec=='meoh':
        ATinput='CH3OH_TOGA'
    else:
        print('Wrong')
    
    fh=Dataset(path+'MER-TOGA_DC8_ATom-2.nc','r')
    lon = fh.groups['MMS'].variables['G_LONG'][:]
    lat = fh.groups['MMS'].variables['G_LAT'][:]
    
    times = fh.variables['time'][:]
    t = datetime(2016,1,1,0,0) ## time is given in seconds since 2016-01-01. Converting into datetime object
    ts = (t-datetime(1970,1,1,0,0)).total_seconds()
    timex=[] 
    for i in range(len(times)):
        timex.append(datetime.fromtimestamp(times[i]+ts).strftime("%d/%m/%Y %H:%M:%S"))
    dates_list= [datetime.strptime(time, "%d/%m/%Y %H:%M:%S").strftime('"%d/%m/%Y %H:%M:%S"') for time in timex]
    data = (fh.groups['TOGA']).variables[ATinput]
    
    var = pd.DataFrame({'date':dates_list, spec:data[:]})
    var = var.set_index(['date'])
    var.index = pd.to_datetime(var.index,format='"%d/%m/%Y %H:%M:%S"')
    hourly = var.resample('H').mean()
    
    ## read CVAO OVOC data for comparison
    filepath  = '/users/mjr583/scratch/NCAS_CVAO/CVAO_datasets/'
    filen = filepath+'cv_ovocs_2018_M_Rowlinson.csv'
    odf = pd.read_csv(filen, index_col=0)
    odf.index = pd.to_datetime(odf.index,format='%d/%m/%Y %H:%M')
    
    ocols = list(odf) 
    for col in ocols:
        odf = odf.loc[~(odf[col] <= 0.)]
    Ohourly = odf[spec].resample('H').mean()
    
    plt.scatter(hourly.index, hourly, label='ATom')
    plt.scatter(Ohourly.index,Ohourly, label='CVAO')
    plt.xlim(left=hourly.index[0]-50)
    plt.xlim(right=hourly.index[-1]+50)
    plt.legend(frameon=False)
    plt.ylim(bottom=0.,top=1000)
    plt.savefig(savepath+spec+'.png')
    plt.close()  
