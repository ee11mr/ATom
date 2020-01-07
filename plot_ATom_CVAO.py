import numpy as np
import pandas as pd
from netCDF4 import Dataset
from datetime import datetime
import matplotlib.pyplot as plt
path='/users/mjr583/scratch/ATom/ATom_merge_1581/data/'
savepath='/users/mjr583/scratch/ATom/plots/'
species=['acetaldehyde','acetone','meoh']
uppers=[3000,1500,3000]
for s,spec in enumerate(species):
    variable=[] ; latitude=[] ; longitude=[]
    timestamps=[] ; altitude=[] ; pressure=[]
    ## Loop through the 3 TOGA campaigns to get all the data
    for i in range(1,4):
        if spec == 'acetaldehyde':
            ATinput='CH3CHO_TOGA'
        elif spec=='acetone':
            ATinput='Acetone_TOGA'
        elif spec=='meoh':
            ATinput='CH3OH_TOGA'
        else:
            print('Not a valid variable name')

        fh=Dataset(path+'MER-TOGA_DC8_ATom-'+str(i)+'.nc','r')

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
        variable.append(var)
        
        lon = fh.groups['MMS'].variables['G_LONG'][:]    
        Xlon = pd.DataFrame({'date':dates_list, 'Lon':lon[:]})
        Xlon = Xlon.set_index(['date'])
        Xlon.index = pd.to_datetime(var.index,format='"%d/%m/%Y %H:%M:%S"')
        longitude.append(Xlon)
        
        lat = fh.groups['MMS'].variables['G_LAT'][:]
        Xlat = pd.DataFrame({'date':dates_list, 'Lat':lat[:]})
        Xlat = Xlat.set_index(['date'])
        Xlat.index = pd.to_datetime(var.index,format='"%d/%m/%Y %H:%M:%S"')
        latitude.append(Xlat)
        
        alt = fh.groups['MMS'].variables['G_ALT'][:] * 1e-3
        Xalt = pd.DataFrame({'date':dates_list, 'Alt':alt[:]})
        Xalt = Xalt.set_index(['date'])
        Xalt.index = pd.to_datetime(var.index,format='"%d/%m/%Y %H:%M:%S"')
        altitude.append(Xalt)
        
        p = fh.groups['MMS'].variables['P'][:] * 1e-3
        Xp = pd.DataFrame({'date':dates_list, 'P':p[:]})
        Xp = Xp.set_index(['date'])
        Xp.index = pd.to_datetime(var.index,format='"%d/%m/%Y %H:%M:%S"')
        pressure.append(Xp)
    ## concatenate dataframes
    var_frames = [variable[0], variable[1], variable[2]]
    lat_frames = [latitude[0], latitude[1], latitude[2]]
    lon_frames = [longitude[0], longitude[1], longitude[2]]
    alt_frames = [altitude[0], altitude[1], altitude[2]]
    p_frames = [pressure[0], pressure[1], pressure[2]]
    
    variable = pd.concat(var_frames)
    longitude = pd.concat(lon_frames)
    latitude = pd.concat(lat_frames)
    altitude = pd.concat(alt_frames)
    pressure = pd.concat(p_frames)

    ## select low altitude data at appropriate latitude and longitudes
    var1 = variable[spec][altitude['Alt']<=2.]
    
    var2 = var1[longitude['Lon']<=-10.]
    var3 = var2[longitude['Lon']>=-40.]
    
    var4 = var3[latitude['Lat']<=20.]
    var5 = var4[latitude['Lat']>=10.]
    variable=var5
    n= str(len(variable))
    
    ## read CVAO OVOC data for comparison
    filepath  = '/users/mjr583/scratch/NCAS_CVAO/CVAO_datasets/'
    filen = filepath+'cv_ovocs_2018_M_Rowlinson.csv'
    odf = pd.read_csv(filen, index_col=0)
    odf.index = pd.to_datetime(odf.index,format='%d/%m/%Y %H:%M')
    
    ocols = list(odf) 
    for col in ocols:
        odf = odf.loc[~(odf[col] <= 0.)]
    hourly = odf[spec].between_time('10:00','14:00').resample('H').mean()
    daily = odf[spec].resample('D').mean()
    
    cvao = hourly
    plt.scatter(cvao.index,cvao, label='CVAO')
    plt.scatter(variable.index, variable, label='ATom (n='+n+')')
    plt.xlim(left=datetime.strptime('2016-10-01', '%Y-%M-%d'))
    plt.xlim(right=datetime.strptime('2018-10-01', '%Y-%M-%d'))
    plt.legend(frameon=False)
    plt.ylim(bottom=0.,top=uppers[s])
    plt.ylabel(spec+'(ppt)')
    plt.savefig(savepath+'ATom_'+spec+'.png')
    plt.close()  
