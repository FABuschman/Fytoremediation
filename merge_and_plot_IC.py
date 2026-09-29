# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 13:11:57 2024
Last major update and check: 22 Dec 2025
@author: linde_ae FransBuschman
"""

# packages
#=============================================================================
import numpy as np
import os

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning) #do not show warnings for future Python versions; must be before import pandas
import pandas as pd

import matplotlib.pyplot as plt
#import matplotlib.dates as mdates
from datetime import date
from datetime import datetime 
import fabfunctions

# functions   ---> in fabfunctions.py
#=============================================================================


#%% user settings
#=============================================================================
today = date.today().strftime("%Y%m%d")

rootdir = r"p:\470-gml-data\Delta-lab\projecten\fytoremediatie EMK\Data"
indir = r'p:\470-gml-data\Delta-lab\Intake\labwerk formulier'
#outdir = fabfunctions.makedir(os.path.join(rootdir, "Dataverwerking Python"))  #MAKE THIS 'WORKDIR'
outdir_plot = fabfunctions.makedir(os.path.join(rootdir, f"Dataverwerking Python/plots/_kas/{today}/IC"))

# list files
fin_2025 = "2025-023 EMK PFAS Kas proeven.xlsm" #2025
fin_2026 = "2026-004 Fyto-PFAS kas Delft proeven.xlsm" #the last samples of round 3 taken in 2026

# limit of detection: dictionary with the nutrients as key (also used for selecting which nutrients to plot) 
lod = { 
#"Fluoride"	  :0.02,
"Chloride"	  :0.07,
"Nitrite"	  :0.01,
"Bromide"	  :0.03,
"Nitrate"	  :0.18,
"Sulfate"	  :0.42,
"Phosphate"	  :0.05,
#"Lithium"	  :0.01,
"Sodium"	  :0.05,
"Ammonium"	  :0.002,
"Potassium"	  :0.04,
"Magnesium"	  :0.04,
"Calcium"	  :0.1
}

# unit concentration for results from Deltalab
unitDeltalab = "mg/l"

# dataframe with the dates of sowing and harvesting; take care: index and roundnr available
dates_round_plants= pd.DataFrame({"start":[datetime.strptime('28-Mar-2025', "%d-%b-%Y"), datetime.strptime('28-May-2025', "%d-%b-%Y"),\
                                           datetime.strptime('11-Sep-2025', "%d-%b-%Y"), datetime.strptime('01-May-2026', "%d-%b-%Y"),
                                           datetime.strptime('16-Jul-2026', "%d-%b-%Y")], #16 July in stead of 14 july, in orderto see when round 5 starts
                                  "end": [datetime.strptime('16-May-2025', "%d-%b-%Y"), datetime.strptime('14-Aug-2025', "%d-%b-%Y"),\
                                         datetime.strptime('21-Jan-2026', "%d-%b-%Y"), datetime.strptime('14-Jul-2026', "%d-%b-%Y"),
                                         datetime.strptime('30-Oct-2026', "%d-%b-%Y")]} ) #NB 30oct is estimated for round 5

dates_round_plants.insert(2,"roundnr", list(range(1,dates_round_plants.end.size+1) ) ) #add round number
dates_round_plants.insert(2,"duration_rnd",dates_round_plants.end-dates_round_plants.start) #add the duration 

#print the dates and duration per round (not using the index)
for rnd in dates_round_plants.roundnr:
    print(f"Round {rnd} starts {dates_round_plants.start[rnd-1]} and ends {dates_round_plants.end[rnd-1]} \
           and has a duration of {dates_round_plants.duration_rnd[rnd-1]}")

datesfilltanks=  [datetime.strptime('03-Jul-2025', "%d-%b-%Y"), 
                 datetime.strptime('28-Jul-2025', "%d-%b-%Y"),
                 datetime.strptime('11-Aug-2025', "%d-%b-%Y"),
                 datetime.strptime('2-Sep-2025', "%d-%b-%Y"),
                 datetime.strptime('21-Jan-2026', "%d-%b-%Y"),
                 datetime.strptime('04-May-2026', "%d-%b-%Y"),
                 datetime.strptime('27-Jul-2026', "%d-%b-%Y"),
                 datetime.strptime('18-Aug-2026', "%d-%b-%Y")]

print(f"Water was added (a bit on top or reservoir fully filled up) on {len(datesfilltanks)} moments, starting {datesfilltanks[0]}")

#the order of the soil compartments in the Delft greenhouse (used for plots)
soiltypes_goodorder = ["Sand", "Sand+salt","Bentonite", "Magnetite", "Zeolite","Iron-Zeolite", "Activated Carbon",
                       "Biochar"] # all adsorbants; "No adsorbant" is used for comp4 when the tank was empty: leaving that out, results in plots without these results


#settings for plots
plt.style.use('default')
plt.rcParams['font.size'] = 14. #font size used for all plt.plots
plt.rcParams.update({'figure.max_open_warning': 0}) #suppresses (erroneous) warnings about figures that are open 


#%% Import
#=============================================================================

# import reconstructed water volume rounds 1-4 with Date as the index column 
vol_reconstr_r1_3 = pd.read_excel(os.path.join(indir, fin_2025),    
                         sheet_name="Watervolume",
                         usecols=["Date", "Sand", "Zeolite", "Activated Carbon","Bentonite", "Magnetite"], skiprows=6, index_col=0)
wl_from_r4 = pd.read_excel(os.path.join(indir, fin_2026),\
                         sheet_name ='Watervolume',usecols=["Date", "Sand", "Zeolite", "Biochar","Iron-Zeolite", "Sand+salt"], skiprows=3,index_col=0) #for round 3 last part
# Known volume at water level (see labform Watervolume)
Lookup_from_r4 = pd.read_excel(os.path.join(indir, fin_2026),\
                         sheet_name ='Watervolume',usecols=["water level (cm)", "Volume (l)"], skiprows=3,index_col=0) #the lookup table water level --> volume since round 4

# Perform interpolation since round 4
vol_interpolated_since_r4 = pd.DataFrame(
    np.interp(
        wl_from_r4.to_numpy(),
        Lookup_from_r4.index.to_numpy(),
        Lookup_from_r4['Volume (l)'].to_numpy(),
    ),
    index=wl_from_r4.index,
    columns=wl_from_r4.columns
)

df_vol_allrounds = pd.concat([vol_reconstr_r1_3, vol_interpolated_since_r4], axis=0, sort=False) 

#import metadata and IC data
#2025
metadata25 = pd.read_excel(os.path.join(indir, fin_2025),
                         sheet_name="labcodes",
                         usecols=["labcode", "matrix","soil type", "biota","sample name", "Date"], skiprows=1)
metadata25["monstercode"] = [str(i).replace("-","") for i in metadata25["labcode"]] #remove '-' in name used to merge (needed as in some data tabs no '-' were added)

# get list of sheets with IC data and load them all
xl = pd.ExcelFile(os.path.join(indir, fin_2025))
sheets = [s for s in xl.sheet_names if s.startswith("IC") and "ICP" not in s] #there is one sheet that starts with "kopie": this way excluded

list_raw = [] #add data to this list
colstoread= list(lod.keys()) #use earlier defined keys to get names of columns to read
colstoread.append('monstercode') #add this crucial one (at end)
for s in sheets: 
    # import csv file
    dfraw = pd.read_excel(os.path.join(indir, fin_2025),
                          usecols=colstoread, 
                          sheet_name=s, skiprows=27, index_col=0) #two columns with monstercode occur: only first loaded, I guess (and they seem the same)
    # add to list
    list_raw.append(dfraw)

#make dataframe from data in list
dfin25 = pd.concat(list_raw).reset_index()
dfin25['monstercode'] =[str(i).replace("-","") for i in dfin25["monstercode"]] #also in tabs with data remove '-' in name used to merge


#2026
metadata26 = pd.read_excel(os.path.join(indir, fin_2026),
                         sheet_name="labcodes",
                         usecols=["labcode", "matrix","soil type", "biota","sample name", "Date"], skiprows=0) #NB skiprows=0 for 2026 (=1 for 2025)
metadata26["monstercode"] = [str(i).replace("-","") for i in metadata26["labcode"]] #remove '-' in name used to merge (needed as in some data tabs no '-' were added)

# get list of sheets with IC data and load them all
xl = pd.ExcelFile(os.path.join(indir, fin_2026))
sheets = [s for s in xl.sheet_names if s.startswith("IC") and "ICP" not in s]

list_raw = [] #add data to this list
colstoread= list(lod.keys()) #use earlier defined keys to get names of columns to read
colstoread.append('monstercode') #add this crucial one (at end)
for s in sheets: 
    # import csv file
    dfraw = pd.read_excel(os.path.join(indir, fin_2026),
                          usecols=colstoread, 
                          sheet_name=s, skiprows=27, index_col=0) #two columns with monstercode occur: only first loaded, I guess (and they seem the same)
    # add to list
    list_raw.append(dfraw)

#make dataframe from data in list
dfin26 = pd.concat(list_raw).reset_index()
dfin26['monstercode'] =[str(i).replace("-","") for i in dfin26["monstercode"]] #also in tabs with data remove '-' in name used to merge


#%% Combine the dataframes
#============================================================================= 
#combine the dataframes for two years
df_meta_all = pd.concat([metadata25, metadata26], ignore_index=False, sort=False) #all meta data

dfin_all= pd.concat([dfin25, dfin26], ignore_index=False, sort=False) #all concentration data


#make one dataframe to be durther analyzed
df = df_meta_all.merge(dfin_all, how = 'inner', on='monstercode') 

duplicates = df[df.duplicated(subset=["monstercode"], keep=False)] #removing duplo data (can be done more elegant)
print(duplicates)

#%% Process
#=============================================================================

#%Estimate volume of water per compartment, which can be multiplied by pivot dataframe (concentration) to yield mass
vol_water_wetsoil=50 #the volume of water in wet (terrestrial) soil, see box A (Zwart, 2025)

#Add water volume in soil and plant for all times but the first (rough estimate, assuming it is always wetted)
df_vol_wetsoil = df_vol_allrounds.copy()
df_vol_wetsoil.index = pd.to_datetime(df_vol_wetsoil.index, errors='coerce')
df_vol_wetsoil = df_vol_wetsoil.loc[~df_vol_wetsoil.index.isna()].sort_index()
df_vol_wetsoil = df_vol_wetsoil.apply(pd.to_numeric, errors='coerce')
df_vol_wetsoil.iloc[1:] = df_vol_wetsoil.iloc[1:].add(vol_water_wetsoil)

#% Interpolate the water and wet soil volume per compartment on sampling dates 
#   df_vol_allrounds['date_float'] = [da.timestamp() for da in df_vol_allrounds.index] #add column with numeric date (float) for interpolation;   .index.to_list()
#   df_vol_allrounds.set_index('date_float',inplace=True) #modify dataframe forever (not creating a new one; for debugging still to be possible I only use it when I change the index)

dates_sampling = pd.DatetimeIndex(
    pd.to_datetime(df['Date'], errors='coerce').dropna().unique()
).sort_values()
df_vol_wetsoil_onsampling = pd.DataFrame(index=dates_sampling)
df_vol_wetsoil_onsampling.index.name = 'Date'

for soil in df_vol_wetsoil.columns:
    volume_measurements = df_vol_wetsoil[soil].dropna()
    if volume_measurements.empty:
        raise ValueError(f'No volume measurements found for {soil}')

    sampling_in_range = (
        (dates_sampling >= volume_measurements.index.min())
        & (dates_sampling <= volume_measurements.index.max())
    )
    interpolated_volume = pd.Series(np.nan, index=dates_sampling, dtype=float)
    interpolated_volume.loc[sampling_in_range] = np.interp(
        dates_sampling[sampling_in_range].asi8,
        volume_measurements.index.asi8,
        volume_measurements.to_numpy(),
    )
    df_vol_wetsoil_onsampling[soil] = interpolated_volume

#plot the volume in tank and soil interpolated on sampling dates 
df_vol_wetsoil_onsampling_plot=df_vol_wetsoil_onsampling.reindex(soiltypes_goodorder, axis="columns") #Activated carbon is often first, change to order in greenhouse
fabfunctions.plot_timeseries(df_vol_wetsoil_onsampling_plot, outdir_plot,
                     fname= f"Water volume in tank and soil_interpolated on t(IC)", ylab=f"Water volume in tank and soil (l)", 
                     dates_round_plants=dates_round_plants, datesfilltanks=datesfilltanks) 

#plot the original volume of water and wetsoil
df_vol_wetsoil_plot=df_vol_wetsoil.reindex(soiltypes_goodorder, axis="columns") #Activated carbon is often first, change to order in greenhouse
fabfunctions.plot_timeseries(df_vol_wetsoil_plot, outdir_plot,
                     fname= f"Water volume in tank and soil (as read from marks and rod)", ylab=f"Water volume in tank and soil (l)", 
                     dates_round_plants=dates_round_plants, datesfilltanks=datesfilltanks) 


# #% Obtain volume from mass CL (t=0) is preserved
# df_pivot_chloride =df.pivot(index=['Date'],
#                        columns= ['soil type'],
#                        values='Chloride').replace("n.a.", np.nan)

# vol_from_cl= (df_pivot_chloride.values[0]*vol_tank_full)/df_pivot_chloride #the volume*concentration at t=0 divided by concentration CL(t)

# vol_final= vol_from_cl.copy() #first volume estimates are okay
# for soil in df_pivot_chloride.columns: #correct first two volumes of round 3
#     vol_final.at['2025-09-11', soil] = vol_tank_full+vol_water_wetsoil
#     vol_final.at['2025-10-02', soil] = vol_tank_full+vol_water_wetsoil

# nsampling_correct= range(11,len(vol_from_cl.values))
# for n in nsampling_correct:
#     vol_final.values[n]= vol_final.values[n-1]+ vol_from_cl.values[n]-vol_from_cl.values[n-1]

# #change order soil types to order in greenhouse
# vol_final_plot=vol_final.reindex(soiltypes_goodorder, axis="columns") 

# fabfunctions.plot_timeseries(vol_final_plot, outdir_plot,
#                       fname= f"Water volume from CL_round3adapted", ylab=f"Water volume assuming CL is preserved (l; round 3 adapted)", 
#                       dates_round_plants=dates_round_plants, datesfilltanks=datesfilltanks) #plot the interpolatede volume, which is used further on


#% iterate over nutrients to get final results
for sub, lod in lod.items():

    # pivot table 
    df_pivot =df.pivot(index=['Date'],
                       columns= ['soil type'],
                       values=sub).replace("n.a.", np.nan)
                
    ### plot concentration   #first and second argument need to given, others are matched by defined name
    df_pivot_plot=df_pivot.reindex(soiltypes_goodorder, axis="columns") #Activated carbon is often first, change to order in greenhouse
    
    fabfunctions.plot_timeseries(df_pivot_plot, outdir_plot,
                    fname= f"Concentration {sub}", ylab=f"Concentration {sub} ({unitDeltalab})", 
                    dates_round_plants=dates_round_plants, datesfilltanks=datesfilltanks)
                        #cmap='tab20',  xlab ='', title=sub,
    
    # Align dates and soil types explicitly before converting concentrations to mass.
    df_mass_plot = df_vol_wetsoil_onsampling.reindex(
                index=df_pivot_plot.index, columns=df_pivot_plot.columns
            ).mul(df_pivot_plot)
          
    fabfunctions.plot_timeseries(df_mass_plot, outdir_plot,
                    fname= f"Mass {sub}", ylab=f"Mass {sub} ({unitDeltalab[:2]})", 
                    dates_round_plants=dates_round_plants, datesfilltanks=datesfilltanks)

#check that dates sampling and in pivot were indeed the same
dates_pivot_float= [d.timestamp() for d in df_pivot.index] #numeric date (float) needed for interpolation; 

# Check that the final pivot uses every normalized water-sampling date.
if df_pivot.index.equals(dates_sampling):
    print('Sampling dates and dates according to pivot are identical.')
else:
    raise ValueError('Sampling dates and dates according to pivot are not identical.')
##print(f"Sampling dates and dates according pivot should be within 12 hours, check: ")
##print(np.isclose(dates_pivot_float, dates_sampling_float, rtol=1e-10, atol=12*60*60, equal_nan=True))
