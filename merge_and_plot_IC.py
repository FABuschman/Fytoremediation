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
outdir = fabfunctions.makedir(os.path.join(rootdir, "Dataverwerking Python"))  #MAKE THIS 'WORKDIR'
outdir_plot = fabfunctions.makedir(os.path.join(outdir, f"plots/_kas/{today}/IC"))

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

# the compartments in order as they are greenhouse
soiltypes_goodorder = ["Sand", "Zeolite", "Activated Carbon","Bentonite", "Magnetite"] 

# dataframe with the dates of sowing and harvesting; take care: index and roundnr available
dates_round_plants= pd.DataFrame({"start":[datetime.strptime('28-Mar-2025', "%d-%b-%Y"), datetime.strptime('28-May-2025', "%d-%b-%Y"),\
                                           datetime.strptime('11-Sep-2025', "%d-%b-%Y")], \
                                  "end": [datetime.strptime('16-May-2025', "%d-%b-%Y"), datetime.strptime('14-Aug-2025', "%d-%b-%Y"),\
                                         datetime.strptime('19-jan-2026', "%d-%b-%Y")]} ) #NB for round 3 many plants were harvested after this end date

dates_round_plants.insert(2,"roundnr", list(range(1,dates_round_plants.end.size+1) ) ) #add round number
dates_round_plants.insert(2,"duration_rnd",dates_round_plants.end-dates_round_plants.start) #add the duration 

#print the dates and duration per round (not using the index)
for rnd in dates_round_plants.roundnr:
    print(f"Round {rnd} starts {dates_round_plants.start[rnd-1]} and ends {dates_round_plants.end[rnd-1]} \
           and has a duration of {dates_round_plants.duration_rnd[rnd-1]}")

datesfilltanks=  [datetime.strptime('03-Jul-2025', "%d-%b-%Y"), 
                 datetime.strptime('28-Jul-2025', "%d-%b-%Y"),
                 datetime.strptime('11-Aug-2025', "%d-%b-%Y"),
                 datetime.strptime('2-sep-2025', "%d-%b-%Y"),
                 datetime.strptime('21-jan-2026', "%d-%b-%Y")]

print(f"Water was added to tanks on {len(datesfilltanks)} moments, starting {datesfilltanks[0]}")

#settings for plots
plt.style.use('default')
plt.rcParams['font.size'] = 14. #font size used for all plt.plots
plt.rcParams.update({'figure.max_open_warning': 0}) #suppresses (erroneous) warnings about figures that are open 


#%% Import
#=============================================================================
#import reconstructed water volume with Date as the index column 
vol_reconstr = pd.read_excel(os.path.join(indir, fin_2025),
                         sheet_name="Watervolume",
                         usecols=["Date", "Sand", "Zeolite", "Activated Carbon","Bentonite", "Magnetite"], skiprows=6, index_col=0)

#import metadata and IC data
#2025
metadata25 = pd.read_excel(os.path.join(indir, fin_2025),
                         sheet_name="labcodes",
                         usecols=["labcode", "matrix","soil type", "biota","sample name", "Date"], skiprows=1)
metadata25["monstercode"] = [str(i).replace("-","") for i in metadata25["labcode"]] #remove '-' in name used to merge (needed as in some data tabs no '-' were added)

# get list of sheets with IC data and load them all
xl = pd.ExcelFile(os.path.join(indir, fin_2025))
sheets = [s for s in xl.sheet_names if ("IC" in s) and ("ICP" not in s)]

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
sheets = [s for s in xl.sheet_names if ("IC" in s) and ("ICP" not in s)]

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

vol_tank_full=266 # the volume of water (l) per compartment when tank is full 
vol_water_wetsoil=50 #the volume of water in wet (terrestrial) soil, see box A (Zwart, 2025)

#change order soil types to order in greenhouse
vol_reconstr_plot=vol_reconstr.reindex(soiltypes_goodorder, axis="columns") 

#% Interpolate the reconstructed watervolume per compartment on sampling dates 
fabfunctions.plot_timeseries(vol_reconstr_plot, outdir_plot,
                     fname= f"Water volume_tank_on_marks", ylab=f"Water volume in tank (l)", 
                     dates_round_plants=dates_round_plants, datesfilltanks=datesfilltanks) #plot the volume that was reconstructed from marks and logbook

vol_reconstr['date_float'] = [da.timestamp() for da in vol_reconstr.index] #add column with numeric date (float) for interpolation;   .index.to_list()
vol_reconstr.set_index('date_float',inplace=True) #modify dataframe forever (not only here, or something like that)
    #watervolrec.set_index('Date',inplace=True) #change the index again to datetime dates

dates_sampling= df['Date'].unique()  #make new dataframe with volume on sampling dates, which can be multiplied by pivot dataframe (concentration) to yield mass
df_vol = pd.DataFrame({'date':dates_sampling})
df_vol.set_index('date', inplace=True)

dates_sampling_float= [da.timestamp() for da in dates_sampling] #numeric date (float) needed for interpolation; 

for soil in vol_reconstr.columns:  #INTERPOLATE VOLUME for soil ('type' cannot be used, as it is protected)
     df_vol[soil] = np.interp(dates_sampling_float, 
                                vol_reconstr.index.to_list(), vol_reconstr[soil].values) #soil must be [], and not in between .., since a space occurs in one of the names

df_vol_wetsoil= df_vol.copy() #copy the dataframe and numbers
nsampling_wetsoil= range(1,len(df_vol_wetsoil.values)) #correct all but first moment with wet soil volume
for n in nsampling_wetsoil:
    df_vol_wetsoil.values[n]= df_vol.values[n]+ vol_water_wetsoil

#change order soil types to order in greenhouse
df_vol_wetsoil_plot=df_vol_wetsoil.reindex(soiltypes_goodorder, axis="columns") 

fabfunctions.plot_timeseries(df_vol_wetsoil_plot, outdir_plot,
                     fname= f"Water volume in tank and soil_interpolated", ylab=f"Water volume in tank and soil (l)", 
                     dates_round_plants=dates_round_plants, datesfilltanks=datesfilltanks) #plot the volume that was reconstructed from marks and logbook


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
                
    #Multiply with volume to arrive at mass
    df_mass= pd.DataFrame(df_vol_wetsoil*df_pivot.values, columns=df_pivot.columns, index=df_pivot.index) #temporarily made for each soil

    #change order soil types to order in greenhouse
    df_pivot_plot=df_pivot.reindex(soiltypes_goodorder, axis="columns") 
    df_mass_plot=df_mass.reindex(soiltypes_goodorder, axis="columns") 

    # plot timeseries   #first and second argument need to BE given, others are matched by defined name
    fabfunctions.plot_timeseries(df_pivot_plot, outdir_plot,
                    fname= f"Concentration {sub}", ylab=f"Concentration {sub} ({unitDeltalab})", 
                    dates_round_plants=dates_round_plants, datesfilltanks=datesfilltanks)
                        #cmap='tab20',  xlab ='', title=sub,
    
    fabfunctions.plot_timeseries(df_mass_plot, outdir_plot,
                    fname= f"Mass {sub}", ylab=f"Mass {sub} ({unitDeltalab[:2]})", 
                    dates_round_plants=dates_round_plants, datesfilltanks=datesfilltanks)

#check that dates sampling and in pivot were indeed the same
dates_pivot_float= [d.timestamp() for d in df_pivot.index] #numeric date (float) needed for interpolation; 

print(f"Sampling dates and dates according pivot should be within 12 hours, check: ")
print(np.isclose(dates_pivot_float, dates_sampling_float, rtol=1e-10, atol=12*60*60, equal_nan=True))
