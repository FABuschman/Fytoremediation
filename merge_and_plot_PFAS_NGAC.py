# -*- coding: utf-8 -*-
"""
@author: linde_ae   Frans Buschman
"""
# packages
#=============================================================================
###import csv              #for the mapping files
from datetime import date
from datetime import datetime #added to make list of dates
import numpy as np
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

#import my own functions
import fabfunctions

# functions   ---> in fabfunctions.py
#=============================================================================


#%% user settings
#=============================================================================

today = date.today().strftime("%Y%m%d")

rootdir = r"p:\470-gml-data\Delta-lab\projecten\fytoremediatie EMK\Data" #use raw strings for names with \
indir = r"p:\470-gml-data\Delta-lab\Intake\labwerk formulier"
#workdir = os.path.join(rootdir, "Dataverwerking Python\\scripts\\_kas") #not needed: mapping Mass_pure_PFAS_added are with scripts in GIT-folder

outdir_plot_water = fabfunctions.makedir(os.path.join(rootdir, f"Dataverwerking Python\\plots\\_kas\\{today}\\water"))  
outdir_plot_plant = fabfunctions.makedir(os.path.join(rootdir, f"Dataverwerking Python\\plots\\_kas\\{today}\\plant"))  
outdir_plot_plant_dry_wet = fabfunctions.makedir(os.path.join(rootdir,\
                                                               f"Dataverwerking Python\\plots\\_kas\\{today}\\plant\\Conc_dry_wet"))  #subdir
outdir_plot_combine = fabfunctions.makedir(os.path.join(rootdir,\
                                                               f"Dataverwerking Python\\plots\\_kas\\{today}\\_combine"))  #for final plots
outdir_plot_gado = fabfunctions.makedir(os.path.join(rootdir, f"Dataverwerking Python\\plots\\_kas\\{today}\\gadolinium"))  #subdir
outdir_plot_soil = fabfunctions.makedir(os.path.join(rootdir, f"Dataverwerking Python\\plots\\_kas\\{today}\\soil"))  

# list files
fin_2025 = "2025-023 EMK PFAS Kas proeven.xlsm" #2025
fin_2026 = "2026-004 Fyto-PFAS kas Delft proeven.xlsm" #the last samples of round 3 taken in 2026, including a re-analysis of two water sampling moments 
    #the re-analysis results are in a separate tab, and the results of the first (wrong) analysis are removed from the other tab (on sampling moment was in 2025)

fin_pfas_added = "Mass_pure_PFAS_in_Date.csv" #pure PFAS mass added to the water on 2 dates; sum for all compartments (mg)

# dataframe with the dates of sowing and harvesting; take care: index and roundnr available
dates_round_plants= pd.DataFrame({"start":[datetime.strptime('28-Mar-2025', "%d-%b-%Y"), datetime.strptime('28-May-2025', "%d-%b-%Y"),\
                                           datetime.strptime('11-Sep-2025', "%d-%b-%Y"), datetime.strptime('01-May-2026', "%d-%b-%Y") \
                                           ], #datetime.strptime('16-Jul-2026', "%d-%b-%Y")   16 July in stead of 14 july, in orderto see when round 5 starts
                                  "end": [datetime.strptime('16-May-2025', "%d-%b-%Y"), datetime.strptime('14-Aug-2025', "%d-%b-%Y"),\
                                         datetime.strptime('21-Jan-2026', "%d-%b-%Y"), datetime.strptime('14-Jul-2026', "%d-%b-%Y") \
                                         ]} ) #NB 30oct is estimated for round 5   datetime.strptime('30-Oct-2026', "%d-%b-%Y")

dates_round_plants.insert(2,"roundnr", list(range(1,dates_round_plants.end.size+1) ) ) #add round number
dates_round_plants.insert(2,"duration_rnd",dates_round_plants.end-dates_round_plants.start) #add the duration 
dates_round_plants[['start', 'end']] = dates_round_plants[['start', 'end']].apply(
    pd.to_datetime
)

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
soiltypes_goodorder = ["Sand", "Sand+salt","Bentonite", "Magnetite", "Zeolite", "Activated Carbon",
                       "Biochar"] # all adsorbants; "Iron-Zeolite",   "No adsorbant" is used for comp4 when the tank was empty: leaving that out, results in plots without these results

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


#Total PFAS mass added (microg) to each water storage reservoir 
pfas_added = pd.read_csv(fin_pfas_added, sep=';',index_col=0)

df_pfas_added = pd.concat([
    pd.DataFrame({
        'compound': pfas_added.columns,
        'date_added': pd.to_datetime(pfas_added.loc['Date_r1'], errors='coerce'),
        'mass': pd.to_numeric(pfas_added.loc['Mass_mg_r1'], errors='coerce') * 1000 / 5, # in micrograms per compartment
    }),
    pd.DataFrame({
        'compound': pfas_added.columns,
        'date_added': pd.to_datetime(pfas_added.loc['Date_r2'], errors='coerce'),
        'mass': pd.to_numeric(pfas_added.loc['Mass_mg_r2'], errors='coerce') * 1000 / 5, # in micrograms per compartment
    }),
], ignore_index=True).dropna(subset=['date_added'])
df_pfas_added.loc[df_pfas_added['mass'].eq(0), 'mass'] = np.nan

#% import meta data 
cols_meta = ['labcode', 'matrix','soil type','biota','plant tissue',
             'compartment','subcompartment','sample name','Date'] #'sample name' is used to find duplos

df_meta = pd.read_excel(os.path.join(indir, fin_2025),\
                        sheet_name ='labcodes',usecols=cols_meta, skiprows=1,index_col='labcode') #for round 1 to first part 3

cols_meta.append('Plant state') #in round 3 we differentiated between live/intermediate/dead plants: also import this column
df_meta2 = pd.read_excel(os.path.join(indir, fin_2026),\
                         sheet_name ='labcodes',usecols=cols_meta, skiprows=0,index_col='labcode') #for round 3 last part

df_meta_allrounds = pd.concat([df_meta, df_meta2], ignore_index=False, sort=False) #round 3 to be added from 2026 data

# add wet weight
#ROUND 1
weight_round1 = pd.read_excel(os.path.join(indir, fin_2025), sheet_name="Gewicht nat biota t=1", #see tab plant final data Ewan
                        usecols=['Sample', 'Nat sample gewicht'], skiprows=6,index_col='Sample')   
weight_round1=weight_round1[:86].rename(columns={'Nat sample gewicht': 'tot wet weight'})

#ROUND 2
weight_round2 = pd.read_excel(os.path.join(indir, fin_2025), sheet_name="Gewicht nat biota t=2",
                        usecols=['sample code', 'total wet weight (g) '], index_col='sample code')   
weight_round2=weight_round2.rename(columns={'total wet weight (g) ': 'tot wet weight'})

#ROUND 3
weight_round3 = pd.read_excel(os.path.join(indir, fin_2026), sheet_name="Plants-round3",
                        usecols=['sample code', 'total wet weight (g) ', 'wet weight for Delta-lab (g)', 'dry weight Delta-lab (g) '], index_col='sample code')   #last two for plant state analysis
weight_round3=weight_round3.rename(columns={'total wet weight (g) ': 'tot wet weight'})

#ROUND 4
weight_round4 = pd.read_excel(os.path.join(indir, fin_2026), sheet_name="Plants-round4",
                        usecols=['sample code', 'total wet weight (g) ', 'wet weight for Delta-lab (g)', 'dry weight Delta-lab (g) '], index_col='sample code')   #last two for plant state analysis
weight_round4=weight_round4.rename(columns={'total wet weight (g) ': 'tot wet weight'})

#ROUND 5
##weight_round5 = pd.read_excel(os.path.join(indir, fin_2026), sheet_name="Plants-round5",
#                        usecols=['sample code', 'total wet weight (g) ', 'wet weight for Delta-lab (g)', 'dry weight Delta-lab (g) '], index_col='sample code')   #last two for plant state analysis
##weight_round5=weight_round5.rename(columns={'total wet weight (g) ': 'tot wet weight'})


#combine weights
weight_allrounds = pd.concat([weight_round1, weight_round2, weight_round3, weight_round4], ignore_index=False, sort=False) #round 3 to be added from 2026 data

df_meta_allrounds=df_meta_allrounds.join(weight_allrounds, how='left') #join (not merge) to add a column (NaN when no match)



#Dry factor is estimated based on round 1 (5 repetitions) and round 3 (1-5 repetitions) for OVEN drying (decided to exclude samples that were freezedried)
dry_factor ={"flower":0.10,
              "leaves":0.14,
              "stem":0.09,
              "roots":0.10,
              "seeds":1,
              "nvt": np.nan,
              "n.a.": np.nan} #last two added, as these names are used when no tissue was available (resp. for 2025 and 2026)

tissue_names=list(dry_factor.keys())[:5]

df_meta_allrounds['dry factor'] = [dry_factor[i] if not pd.isnull(i) else np.nan for i in df_meta_allrounds['plant tissue']] #complex way of assigning the dry factor
# for i in df_meta_allrounds['plant tissue']:
#     if not pd.isnull(i):
#         df_meta_allrounds['dry factor'][i] = dry_factor[i]  
#     else: np.nan 

#Calculate dry weight by multiplying wet weight with dry factor
df_meta_allrounds['dry weight'] = df_meta_allrounds.apply(lambda r:(r['tot wet weight']*r['dry factor']
                                                 if type(r['tot wet weight']) in (int, float)
                                                 else np.nan), axis=1) # conditional columnwise as they are not always numeric
#print(df_meta_allrounds[490:505])

#% import mapping
mapping_agro = pd.read_csv("mapping.csv", sep=';', index_col=1).to_dict() #index_col set to 1, as in NGAC data the full name is used, so key=full name


#% import data from Agro Control (NGAC)
cols_data_agro = ['Monster::MonstercodeKlant','Parameter','TextWaarde']

#2025 (note that NGAC re-analyzed the last set of water samples of 2025: the correct ones are included in the lab form)
# for raw data from NGAC (for some samples 3 numbers), see folder: Data\PFAS data\Agro control\__rawdata)
xls_2025 = pd.ExcelFile(os.path.join(indir, fin_2025))
sheets_agro_2025= [s for s in xls_2025.sheet_names if ("PFAS NGAC" in s) and ("ICP" not in s)]
df_raw_agro = fabfunctions.make_data_table(
    os.path.join(indir, fin_2025), sheets_agro_2025, cols_data_agro
)  # convert all lines to structured data tables

#2026 (note that NGAC re-analyzed the first set of water samples of 2025: the correct ones are included in the lab form)
# for raw data from NGAC (for some samples 3 numbers), see folder: Data\PFAS data\Agro control\__rawdata)
xls_2026 = pd.ExcelFile(os.path.join(indir, fin_2026))
sheets_agro_2026= [s for s in xls_2026.sheet_names if ("NGAC LCMS" in s) and ("ICP" not in s)]

df_raw_agro2 = fabfunctions.make_data_table(
    os.path.join(indir, fin_2026), sheets_agro_2026, cols_data_agro
)  # convert all lines to structured data tables
#df_raw_agro2['Monster::MonstercodeKlant']

df_raw_agro_allrounds= pd.concat([df_raw_agro, df_raw_agro2], ignore_index=False, sort=False)



# Convert all non-numeric data (except np.nan)
for col in df_raw_agro_allrounds.columns:
    df_raw_agro_allrounds[col] = pd.to_numeric(df_raw_agro_allrounds[col], errors='coerce') #numbers were text in xls; with coerce directly make text with '<' NaN


#%% combine data
#=============================================================================

# Keep only lab codes present in both the metadata and NGAC result tables.
df_all_agro = df_meta_allrounds.join(df_raw_agro_allrounds, how='inner', validate='one_to_one')

#for 2025-023-474 there are lines in both labformulier and NGAC data (though empty), resulting in a row in df_all_agro with text iso a date: 
df_all_agro.loc[df_all_agro['Date'] == 'Geen bloem beschikbaar'] = np.nan # make this text NaN to avoid errors later
df_all_agro['Date'] = pd.to_datetime(
    df_all_agro['Date'],
    errors='coerce',
    format='mixed',
) #normalize the metadata in Date to datetime

#compare duplo with original measurement
duplo_obs= df_all_agro[df_all_agro['sample name'].str.contains('duplo', case=False, na=False)]
for i, row in duplo_obs.iterrows():
    duplo_pair = df_all_agro[df_all_agro['sample name'].str.contains(row['sample name'][:29], case=False, na=False)]
    print (duplo_pair)

# Remove duplicate measurements while preserving the original row order.
df_all_agro = df_all_agro[~df_all_agro['sample name'].str.contains('duplo', case=False, na=False)].copy()

#df_water_agro = df_all_agro[df_all_agro['matrix'].eq('Water')].copy()
df_water_agro = df_all_agro.loc[df_all_agro['matrix'] == 'Water',:]
print(f'Number of rows df_all_agro {np.size(df_all_agro,0)} , of which water: {np.size(df_water_agro,0)}')

df_plant_agro = df_all_agro.loc[df_all_agro['matrix'] == 'Plant',:]
    #df_plant_agro['Date'][128:132]
print(f'Number of rows df_all_agro {np.size(df_all_agro,0)} , of which plant: {np.size(df_plant_agro,0)}')

#in 2025 lab formulier "Bodem" consistently used, whereas in 2026 "Soil" is used (all English)
df_soil_agro = df_all_agro.loc[(df_all_agro['matrix'] == 'Bodem') | (df_all_agro['matrix'] == 'Soil'), :]  
print(f'Number of rows df_all_agro {np.size(df_all_agro,0)} , of which soil: {np.size(df_soil_agro,0)}')

#to check combining the data
#pd.set_option('display.max_columns', None) 
#pd.set_option('display.max_rows', None)
#print(df_all_agro[:5])



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
    pd.to_datetime(df_water_agro['Date'], errors='coerce').dropna().unique()
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
fabfunctions.plot_timeseries(df_vol_wetsoil_onsampling_plot, outdir_plot_water,
                     fname= f"Water volume in tank and soil_interpolated on t(PFAS)", ylab=f"Water volume in tank and soil (l)", 
                     dates_round_plants=dates_round_plants, datesfilltanks=datesfilltanks) 

#plot the original volume of water and wetsoil
df_vol_wetsoil_plot=df_vol_wetsoil.reindex(soiltypes_goodorder, axis="columns") #Activated carbon is often first, change to order in greenhouse
fabfunctions.plot_timeseries(df_vol_wetsoil_plot, outdir_plot_water,
                     fname= f"Water volume in tank and soil (as read from marks and rod)", ylab=f"Water volume in tank and soil (l)", 
                     dates_round_plants=dates_round_plants, datesfilltanks=datesfilltanks) 

#Estimate water volume from assuming that mass(CL) is preserved (second method)
# # df_vol = pd.DataFrame({'date':dates_sampling})
# # df_vol.set_index('date', inplace=True)

# # dates_sampling_float= [da.timestamp() for da in dates_sampling] #numeric date (float) needed for interpolation; 

# # for soil in df_vol_allrounds.columns:  #INTERPOLATE VOLUME for soil ('type' cannot be used, as it is protected)
# #     df_vol[soil] = np.interp(dates_sampling_float, 
# #                                df_vol_allrounds.index.to_list(), df_vol_allrounds[soil].values) #soil must be [], and not in between .., since a space occurs in one of the names

# # df_vol_plot=df_vol.reindex(soiltypes_goodorder) #Activated carbon is often first, change to order in greenhouse

# # fabfunctions.plot_timeseries(df_vol, outdir_plot_water,
# #                      fname= f"Water volume on sampling", ylab=f"Interpolated water volume (l)", 
# #                      dates_round_plants=dates_round_plants, datesfilltanks=datesfilltanks) #plot the interpolatede volume, which is used further on


#%% Plot water data
#=============================================================================                                                         
#% Make figure of PFAS in water over time

#analyse for these PFAS compounds
compounds_select = ['PFBA', 'PFHxA', 'PFHpA', 'PFOA', 'PFBS', 'PFOS', 'PFHpS', 'PFHxS',
                    'PFPeA', 'PFPeS', '4_2 FTS', '6_2 FTS'] 

unit_water_NGAC = "\u03bcg/l"

df_waterpfasmass_aggr = {} #for aggregation of water mass by compound

for comp in compounds_select:
    if comp in mapping_agro['naam'].keys():
        fullname = mapping_agro['naam'][comp]
                       
        # Create pivot table for this component
        df_pivot = df_water_agro.pivot_table(
            index='Date', columns='soil type', values=fullname
        )
        
        #(f'Making pivot water for PFAS key: {comp}, with full name: {mapping_agro['naam'][comp]}')
    
        ### plot concentration   #first and second argument need to given, others are matched by defined name
        df_pivot_plot=df_pivot.reindex(soiltypes_goodorder, axis="columns") #Activated carbon is often first, change to order in greenhouse

        figname = f"Water_conc  {comp.replace(':','_')}"
        fabfunctions.plot_timeseries(df_pivot_plot, outdir_plot_water,
                    fname=figname, ylab=f"Concentration {comp} ({unit_water_NGAC})", 
                    dates_round_plants=dates_round_plants, datesfilltanks=datesfilltanks)
    
        # Align dates and soil types explicitly before converting concentrations to mass.
        df_waterpfasmass_aggr[comp] = df_vol_wetsoil_onsampling.reindex(
            index=df_pivot_plot.index, columns=df_pivot_plot.columns
        ).mul(df_pivot_plot)
        

        #### plot mass  
        figname = f"Water_mass_ {comp.replace(':','_')}"
        if comp in list(pfas_added.columns): #for the components that were added
            fabfunctions.plot_timeseries(df_waterpfasmass_aggr[comp], outdir_plot_water,
                    fname=figname, ylab=f"Mass {comp} ({unit_water_NGAC[:2]})",  #assuming volume to be in [l]
                    dates_round_plants=dates_round_plants, datesfilltanks=datesfilltanks,
                    mass_ini=df_pfas_added.loc[df_pfas_added['compound'] == comp])
        else:                                   #for the components that were not added
            fabfunctions.plot_timeseries(df_waterpfasmass_aggr[comp], outdir_plot_water, 
                    fname=figname, ylab=f"Mass {comp} ({unit_water_NGAC[:2]})",  #assuming volume to be in [l]
                    dates_round_plants=dates_round_plants, datesfilltanks=datesfilltanks)

        # Check that the final pivot uses every normalized water-sampling date for PFBA (that was always in water, whereas '6_2 FTS' was not).
        if comp == 'PFBA':
            if df_pivot.index.equals(dates_sampling):
                print('Sampling dates and dates according to pivot are identical.')
            else:
                raise ValueError('Sampling dates and dates according to pivot are not identical.')







#%% Plot plantdata
#=============================================================================                                                         

#make plots for these plant species, per round, per PFAS component 
species=['sunflower']#, 'plantain']

#make end date later, since many plants were sampled after 'end of round 3'
dates_round_plants_ext=dates_round_plants.copy() #copy the correct dates
dates_round_plants_ext.loc[2, 'end']= datetime.strptime('27-jan-2026', "%d-%b-%Y") #the extended dates

bar_colors={tissue_names[0]: "yellow", 
                    tissue_names[1]: "lime", 
                    tissue_names[2]: "darkgreen", 
                    tissue_names[3]: "wheat",
                    tissue_names[4]: "dimgrey"}

subcomp_names=['a','b','c','d'] #df_plant_agro['subcompartment'].unique()
df_plant_agro[['biota','subcompartment', 'compartment', 'Date', 'Plant state','plant tissue']][160:180] #some samples have name "A tm D"

#distribute the plants with subcompartment "A tm D" over the first three subcompartments (only for round 3; manually)
df_plant_agro.loc[['2026-004-022','2026-004-023','2026-004-024'],'subcompartment']='a'
df_plant_agro.loc[['2026-004-025','2026-004-026','2026-004-027'],'subcompartment']='b'
df_plant_agro.loc[['2026-004-028','2026-004-029','2026-004-030'],'subcompartment']='c'

alignunits_g_to_kg=1/1000 #divide by 1000

dates_round_plants_ext

# check of total wet mass plants
wet_mass_plants_tot= df_plant_agro['tot wet weight']
df_numeric = wet_mass_plants_tot.apply(pd.to_numeric, errors='coerce')
df_numeric.sum()

unit_plant_NGAC = "\u03bcg/kg"

df_plantpfasmass_aggr = {}
for specie in species:
    
    # filter data frame on plant species
    df_plant_1specie = df_plant_agro[df_plant_agro['biota'] == specie].reset_index(drop= True)
        
    #print(df_plant_1specie[['dry weight', 'dry factor']]) #print several columns (note that [[]] is needed for column indexing)

    for rnd in  dates_round_plants_ext.roundnr: #per round of plants
        #find the rows within the period of a round
        mask_1rnd = (df_plant_1specie['Date'] > dates_round_plants_ext.start[rnd-1]) & (df_plant_1specie['Date'] <= dates_round_plants_ext.end[rnd-1])
        
        df_plant_1specie_1round={} #clear data from previous round
        df_plant_1specie_1round= df_plant_1specie.loc[mask_1rnd].reset_index() 

        print(f"For round {rnd} dates of harvesting {specie} used in the plots were: ")  
        print(df_plant_1specie_1round.Date.unique())
    
        

        ### barplot plant mass dry weight plant: sum plant MASSes from multiple samples and over subcompartments
        ### 
        df_plant_1specie_1round_grouped = \
                df_plant_1specie_1round.groupby(['soil type', 'compartment', 'plant tissue'])['dry weight'].agg('sum').reset_index()
                
        #prepare Dataframe to plot as bar
        outdict_tis_soil = {} #method: make a nested dictionary, and convert that again to get a complete 5x5 DataFrame (reason for method: not always data are available for each plant tissue)
        for tis in tissue_names:
            df_1tis_temp = df_plant_1specie_1round_grouped[df_plant_1specie_1round_grouped['plant tissue'].str.contains(tis)]
            df_1tis_temp.set_index('soil type',inplace=True)
            inndict = df_1tis_temp['dry weight'].to_dict()
            outdict_tis_soil[tis]=inndict
            
        df5x5_tis_soil = pd.DataFrame(outdict_tis_soil)

        #change order of soil types (rows)
        df5x5_tis_soil_plot=df5x5_tis_soil.reindex(soiltypes_goodorder) #Activated carbon is often first, change to order in greenhouse
        
        # #shorten row name
        df5x5_tis_soil_plot=df5x5_tis_soil_plot.rename(index={'Activated Carbon': 'AC'})
                
        
        ### Create and save stacked bar plot 
        #
        fabfunctions.plot_bar_stacked(df5x5_tis_soil_plot, outdir_plot_plant, f"{specie}_Plant_mass_r{rnd}.png",\
                          color_stacks=bar_colors, ymax=600, ylab =f"Mass {specie} per tissue round {rnd} (g dw)" , )
        
        
        
        ### Make heat map plant mass [subcompartment, compartment]    
        #
        df_plant_subcomp_grouped = \
                df_plant_1specie_1round.groupby(['soil type', 'compartment', 'subcompartment'])['dry weight'].agg('sum').reset_index()
        
        #prepare Dataframe to plot as heat map
        outdict_subcomp_soil = {} #method: make a nested dictionary, and convert that again 
        for subcomp in subcomp_names:
            df_1subcomp_temp = df_plant_subcomp_grouped[df_plant_subcomp_grouped['subcompartment'].str.contains(subcomp)]
            df_1subcomp_temp.set_index('soil type',inplace=True)
            inndict = df_1subcomp_temp[f"dry weight"].to_dict() #this line is different from plant mass
            outdict_subcomp_soil[subcomp]=inndict


        df5x4_1comp_subcomp_soil = pd.DataFrame(outdict_subcomp_soil)

        #change order of soil types (rows) and transpose for plotting
        df5x4_1comp_subcomp_soil_plot=df5x4_1comp_subcomp_soil.reindex(soiltypes_goodorder) #Activated carbon is often first, change to order in greenhouse
        
        # #shorten row name
        df5x4_1comp_subcomp_soil_plot=df5x4_1comp_subcomp_soil_plot.rename(index={'Activated Carbon': 'AC'})

        # Create and save the figure 
        fabfunctions.plot_heat_map(df5x4_1comp_subcomp_soil_plot, outdir_plot_plant, f"{specie}_Plant_mass_heat map_in_r{rnd}.png",\
                                        color_map='YlGn', title_heat= f"Mass {specie} r{rnd} (g)",\
                                        vmax=None if comp == 'PFBA' else 250)#ylab ='', annotation=None
        
        
        
        ### Plots of wet vs. dry mass + 
        # barplot PFAS mass in plant  +  heat map to show variation over subcompartments
        ### 
        df_comp_soil_totals = pd.DataFrame()
        for comp in compounds_select:
            if comp in mapping_agro['naam'].keys():
                fullname = mapping_agro['naam'][comp]
                
                #add column with mass of component in plant per sample (multiply the dry weight and concentration [ug/ kg dw])
                df_plant_1specie_1round[f"mass {comp}"]= \
                    df_plant_1specie_1round.apply(lambda r:
                            (r['tot wet weight']*r[fullname]*alignunits_g_to_kg
                            if type(r['tot wet weight']) in (int, float)
                            else np.nan), axis=1) 
                
                #to check calculation of mass
                df_plant_1specie_1round[['plant tissue','compartment', 'subcompartment', 'tot wet weight','dry weight', fullname,f"mass {comp}"]]

                
                ### plot the concentration of the dried samples and wet samples, which are available for round 2 sunflower
                if rnd==2:
                    if specie=='sunflower':
                        #the concentrations measured in subcompartment 2d and 3c
                        subset_2d= df_plant_1specie_1round.loc[(df_plant_1specie_1round['compartment']==2) & \
                                                                        (df_plant_1specie_1round['subcompartment']=='d' )].reset_index()
                        subset_3c= df_plant_1specie_1round.loc[(df_plant_1specie_1round['compartment']==3) & \
                                                                        (df_plant_1specie_1round['subcompartment']=='c' )].reset_index()
                        # Create figure to plot dry and wet concentrations round 2
                        fig, axs = plt.subplots(ncols=2,sharey=True, figsize=(11.69, 6.27), dpi=300)
                    
                        axs[0].plot(subset_2d.loc[subset_2d['tot wet weight'].notna(), 'plant tissue'],
                                    subset_2d.loc[subset_2d['tot wet weight'].notna(), fullname] , 'g.-') 
                        axs[0].plot(subset_2d.loc[subset_2d['tot wet weight'].isna(), 'plant tissue'],
                                    subset_2d.loc[subset_2d['tot wet weight'].isna(), fullname], 'rx-') 
                        axs[0].plot(subset_2d.loc[subset_2d['tot wet weight'].notna(), 'plant tissue'],
                                    subset_2d.loc[subset_2d['tot wet weight'].notna(), fullname]/
                                        subset_2d.loc[subset_2d['tot wet weight'].notna(), 'dry factor'] , 'g--') 
                        axs[0].set_title(f" {subset_2d['soil type'].unique()}")
                        axs[0].set(ylabel= f"Concentration {comp} ({unit_plant_NGAC})")

                        axs[1].plot(subset_3c.loc[subset_3c['tot wet weight'].notna(), 'plant tissue'],
                                    subset_3c.loc[subset_3c['tot wet weight'].notna(), fullname], 'g.-',\
                                        label='wet to NGAC') 
                        axs[1].plot(subset_3c.loc[subset_3c['tot wet weight'].isna(), 'plant tissue'],
                                    subset_3c.loc[subset_3c['tot wet weight'].isna(), fullname], 'rx-',\
                                        label='freeze-dried to NGAC') 
                        axs[1].plot(subset_3c.loc[subset_3c['tot wet weight'].notna(), 'plant tissue'],
                                    subset_3c.loc[subset_3c['tot wet weight'].notna(), fullname]/
                                        subset_3c.loc[subset_3c['tot wet weight'].notna(), 'dry factor'] ,
                                        'g--',  label='conc wet/ dry factor') 
                        axs[1].set_title(f" {subset_3c['soil type'].unique()}")
            
                        #make the legend only for second subplot (is same for first plot)
                        axs[1].legend(loc='upper right')

                        plt.savefig(os.path.join(f"{outdir_plot_plant_dry_wet}", \
                                                 f"{specie}_concentration_{comp}_wet_vs_dry_2d_3c_in_r{rnd}.png"),\
                                                      bbox_inches='tight', dpi=300) 
                        plt.close()

                
                ### plot the concentration of the different 'Plant states', which are available for round 3 sunflower
                if rnd==3:
                    if specie=='sunflower':
                        
                        plant_state_plot=['alive','intermediate','dead']
                        df_plant_1specie_1round['Plant state']= df_plant_1specie_1round['Plant state'].replace({'Intermediate': 'intermediate'}) #otherwise uppercase not found

                        # Create figure with all dry factors round 3
                        fig, ax = plt.subplots(ncols=3,sharey=True, figsize=(11.69, 6.27), dpi=300)
                        for ip,p in enumerate(plant_state_plot):
                            for s in soiltypes_goodorder:  #also loop over soils to show them as different colors
                                subset_state_1soil=df_plant_1specie_1round.loc[(df_plant_1specie_1round['soil type']==s)]
                            
                                ax[ip].plot(subset_state_1soil.loc[subset_state_1soil['Plant state']==p, 'plant tissue' ],\
                                    subset_state_1soil.loc[subset_state_1soil['Plant state']==p,'dry weight Delta-lab (g) ']/ \
                                    subset_state_1soil.loc[subset_state_1soil['Plant state']==p,'wet weight for Delta-lab (g)'] \
                                    ,'.', label= s)
                                #print(f"the dry factor for state {p} in soil type {s} is for all tissues: {subset_state_1soil.loc[subset_state_1soil['Plant state']==p,'dry weight Delta-lab (g) ']/ \
                                #    subset_state_1soil.loc[subset_state_1soil['Plant state']==p,'wet weight for Delta-lab (g)']}" )
                                                      
                            ax[ip].set_ylim(0,1)
                            ax[ip].set_title(f"{p}")
                            ax[0].set(ylabel= f"dry factor {specie}")
                            ax[0].legend(loc='upper right')
                        
                        plt.savefig(os.path.join(outdir_plot_plant_dry_wet, f"{specie}_dry factor_3states_dots_r{rnd}.png"),\
                                                      bbox_inches='tight', dpi=300) 
                        plt.close()


                        # Create figure with subplot per plant tissue:  concentrations round 3
                        fig, ax = plt.subplots(ncols=4,sharey=True, figsize=(11.69, 6.27), dpi=300) #no plot for 'seeds'
                        
                        ##from cycler import cycler
                        ##ax.set_prop_cycle(cycler('color', ['green', 'orange', 'black']))
                        #ax.set_prop_cycle('color',['green', 'orange', 'black'])
                        
                        for idx,t in enumerate(tissue_names[:4]):
                            
                            subset_state_1tis=df_plant_1specie_1round.loc[(df_plant_1specie_1round['plant tissue']==t)] # loop over soil types to plot color of compartment
                            
                            for ip,p in enumerate(plant_state_plot):
                                                    
                                ax[idx].plot(subset_state_1tis.loc[subset_state_1tis['Plant state']==p,'dry weight Delta-lab (g) ']/ \
                                         subset_state_1tis.loc[subset_state_1tis['Plant state']==p,'wet weight for Delta-lab (g)'],\
                                         subset_state_1tis.loc[subset_state_1tis['Plant state']==p, fullname], 'd',label=p)
                                
                            ax[idx].set_xlim(0, 1)
                            ax[idx].set_title(f"{t}")
                            ax[idx].set(xlabel='dry factor')
                        
                        #make the legend only for last subplot (is same for others) and ylabel only for first
                        ax[0].set(ylabel=f"concentration {comp} ({unit_plant_NGAC})")
                        ax[idx].legend(loc='upper left')

                        plt.savefig(os.path.join(outdir_plot_plant_dry_wet, f"{specie}_conc_{comp}_5tissues_plant state_r{rnd}.png"),\
                                                      bbox_inches='tight', dpi=300) 
                        plt.close()

                

                ### Make bar plot per comp in plant [subcompartment, compartment]    
                #sum all MASSes in compartment per plant tissue per compartment
                df_mass1comp_1sp_1r_grouped = \
                        df_plant_1specie_1round.groupby(['soil type', 'compartment', 'plant tissue'])[f"mass {comp}"].agg('sum').reset_index()
                
                #prepare Dataframe to plot as bar
                outdict_tis_soil = {} #method: make a nested dictionary, and convert that again to get a complete 5x5 DataFrame (reason for method: not always data are available for each plant tissue)
                for tis in tissue_names:
                    df_1tis_temp = df_mass1comp_1sp_1r_grouped[df_mass1comp_1sp_1r_grouped['plant tissue'].str.contains(tis)]
                    df_1tis_temp.set_index('soil type',inplace=True)
                    inndict = df_1tis_temp[f"mass {comp}"].to_dict() #this line is different from plant mass
                    outdict_tis_soil[tis]=inndict
                    
                df5x5_1comp_tis_soil = pd.DataFrame(outdict_tis_soil)

                #change order of soil types (rows)
                df5x5_1comp_tis_soil_plot=df5x5_1comp_tis_soil.reindex(soiltypes_goodorder) #Activated carbon is often first, change to order in greenhouse
                
                                #Aggregate for plotting all rounds together (not yet plotted the same within loop)
                df_pfasmassplants_1comp_soil_totals = df5x5_1comp_tis_soil_plot.sum(axis=1).to_frame().T
                df_pfasmassplants_1comp_soil_totals.index = [rnd]
                df_pfasmassplants_1comp_soil_totals.index.name = 'roundnr'
                df_plantpfasmass_aggr[comp] = pd.concat([
                    df_plantpfasmass_aggr.get(comp, pd.DataFrame()),
                    df_pfasmassplants_1comp_soil_totals,
                ])
                
                ### Create and save stacked bar plot: for whole round and uptake per day
                #
                #shorten name of activated carbon (after creating the aggregated df)
                df5x5_1comp_tis_soil_plot=df5x5_1comp_tis_soil_plot.rename(index={'Activated Carbon': 'AC'})
                
                fabfunctions.plot_bar_stacked(df5x5_1comp_tis_soil_plot, outdir_plot_plant, f"{specie}_mass_{comp}_in_r{rnd}.png",\
                                               ylab=f"Mass {comp} in {specie} tissue r{rnd} ({unit_plant_NGAC[:2]})",\
                                               color_stacks=bar_colors) #no ymax
                
                n_days_rnd=pd.Timedelta(dates_round_plants.loc[rnd-1,'duration_rnd']).days #number of days for this round as integer
                fabfunctions.plot_bar_stacked(df5x5_1comp_tis_soil_plot/n_days_rnd,\
                                               outdir_plot_plant, f"{specie}_DailyUptake_mass_{comp}_in_r{rnd}.png",\
                                               ylab=f"Uptake {comp} r{rnd} ({n_days_rnd} d) in {specie} ({unit_plant_NGAC[:2]}/d)",\
                                               color_stacks=bar_colors, ymax=60 ) #ymax from PFBA to compare rounds and components
                


                ### Make heat map comp in plant [subcompartment, compartment]    
                #aggregate mass per compartment and SUBcompartment: sum all samples including different plant tissue
                df_mass_subcomp_grouped = \
                        df_plant_1specie_1round.groupby(['soil type', 'compartment', 'subcompartment'])[f"mass {comp}"].agg('sum').reset_index()
                
                #prepare Dataframe to plot as heat map
                outdict_subcomp_soil = {} #method: make a nested dictionary, and convert that again 
                for subcomp in subcomp_names:
                    df_1subcomp_temp = df_mass_subcomp_grouped[df_mass_subcomp_grouped['subcompartment'].str.contains(subcomp)]
                    df_1subcomp_temp.set_index('soil type',inplace=True)
                    inndict = df_1subcomp_temp[f"mass {comp}"].to_dict() #this line is different from plant mass
                    outdict_subcomp_soil[subcomp]=inndict
                    
                df5x4_plantmass_subcomp_soil = pd.DataFrame(outdict_subcomp_soil)

                #change order of soil types (rows) and transpose for plotting
                df5x4_plantmass_subcomp_soil_plot=df5x4_plantmass_subcomp_soil.reindex(soiltypes_goodorder) #Activated carbon is often first, change to order in greenhouse
                
                # #shorten row name
                df5x4_plantmass_subcomp_soil_plot=df5x4_plantmass_subcomp_soil_plot.rename(index={'Activated Carbon': 'AC'})

                
                # Create and save the figure 
                fabfunctions.plot_heat_map(df5x4_plantmass_subcomp_soil_plot, outdir_plot_plant, f"{specie}_heat map_{comp}_in_r{rnd}.png",\
                                        color_map='YlOrRd', title_heat= f"Mass {comp} in {specie} r{rnd} ({unit_plant_NGAC[:2]})",\
                                        vmax=None if comp == 'PFBA' else 1300)


# Plot the aggregated plant mass: four round bars per soil type.
round_colors = dict(zip(range(1, 5), sns.color_palette('tab10', 4)))
for comp, df_plantmass_by_round in df_plantpfasmass_aggr.items():
    df_plantmass_by_round_plot = df_plantmass_by_round.reindex(
        index=range(1, 5), columns=soiltypes_goodorder
    ).transpose()
    fabfunctions.plot_bar_stacked(
        df_plantmass_by_round_plot,
        outdir_plot_combine,
        f"{specie}_mass_{comp}_all_rounds.png",
        color_stacks=round_colors,
        xlab='Soil type',
        ylab=f"Mass {comp} in {specie} ({unit_plant_NGAC[:2]})",
        stacked=False,
    )


#%% Process the ICP-MS data (Gd)

#read the background concentration derived from comparison with other REE by Marc Verheul    READ FROM LABFORM? THIS FILE HAS ALL WATER DATA OBTAINED (STEP IN BETWEEN THOUGH)
gado_plants = pd.read_excel(os.path.join(rootdir, "Wateranalyses ICP-MS\\Copy of 260128 Q-All 10x Deltares ICP-MS_MV Gd- bererkeningen.xlsx"), \
                          sheet_name='Deltares 260223 ICPMS', usecols=['Sample Id',  'gd antro (ppb= ug/kg)'], skiprows=24,index_col='Sample Id') 

ratio_gado_sand=gado_plants[4:16]/3.5 #3.5 is the average of the water samples (holds for all compartments, but Zeolite); plotted on x-axis

fig, axicpms = plt.subplots(ncols=4,sharey=True, figsize=(11.69, 6.27), dpi=300)

for comp in compounds_select:
    if comp in mapping_agro['naam'].keys():
        fullname = mapping_agro['naam'][comp]

        #select the matching data (see in 2026-004 EMK kas proeven 2026-004-124till138 sample name for numbers sent to NGAC)
        df_plants_icpms= df_plant_agro[['biota','sample name', 'plant tissue','Plant state', 'compartment', 'tot wet weight','dry factor',\
                                        fullname]][196:208] #209
        #df_plants_icpms._append( df_plant_agro[['sample name', 'plant tissue','Plant state', 'compartment', 'tot wet weight', 'Perfluor-n-butaanzuur (PFBA)']][159:160])
        #df_plants_icpms._append( df_plant_agro[['sample name', 'plant tissue','Plant state', 'compartment', 'tot wet weight', 'Perfluor-n-butaanzuur (PFBA)']][152:153])

        df_plants_icpms['gado ratio']= ratio_gado_sand.values #copy the ratios of Gd to this df to be able to plot per plant tissue
        df_plants_icpms['gado ratio wet']= df_plants_icpms['gado ratio']*df_plants_icpms['dry factor']

        #the water concentration at start of round 3
        pfas_water_t0r3=df_water_agro[fullname].loc[(df_water_agro['compartment']==1) & (df_water_agro['Date']==datetime.strptime('11-Sep-2025', "%d-%b-%Y"))]
        for it, tis_name in enumerate(tissue_names[ :4]):

            mask_tis= df_plants_icpms['plant tissue']== tis_name
                        
            axicpms[it].plot(df_plants_icpms['gado ratio wet'].loc[mask_tis].values, \
                             df_plants_icpms[fullname].loc[mask_tis].values/ pfas_water_t0r3.values , '.-', label=comp) 
            axicpms[it].set_title(f"{tis_name}")
            axicpms[it].set_xlim(0,4)


#make the legend only for second subplot (is same for first plot)
axicpms[1].set_xlabel("Gd conc wet plant corrected for background / conc water []")
axicpms[0].set_ylabel("PFAS conc plant / water conc []")
axicpms[0].legend(loc='upper right')

plt.savefig(os.path.join(f"{outdir_plot_gado}", f"PFAS_ratio_plant_water_Gd_ratio_sunflower_concentration_wet.png"),\
                                                      bbox_inches='tight', dpi=300) 
plt.close()



#%% Plot soil data
#=============================================================================                                                         
### heat map for PFAS in soil
# #
unit_soil_NGAC = "\u03bcg/kg"
Rounds_soil_sampled=[1,3] 
for rnd in  Rounds_soil_sampled:
    #find the rows within the period of a round
    mask_1rnd={}
    mask_1rnd = (df_soil_agro['Date'] > dates_round_plants_ext.start[rnd-1]) & (df_soil_agro['Date'] <= dates_round_plants_ext.end[rnd-1])
        
    df_soil_1round={} #clear data from previous round
    df_soil_1round= df_soil_agro.loc[mask_1rnd].reset_index() 

    print(f"For round {rnd} dates of soil sampling aggregated in the plots were: ")  
    print(df_soil_1round.Date.unique())
      
    for comp in compounds_select:
        if comp in mapping_agro['naam'].keys():
            fullname = mapping_agro['naam'][comp]
            

            #add column with mass of component in soil per sample (multiply the dry weight and concentration [ug/ kg dw])
            df_soil_1round[f"mass {comp}"]= \
							df_soil_1round.apply(lambda r:
									(0.368*0.90/4*0.45 *1450*r[fullname]
									if type(r[fullname]) in (int, float)
									else np.nan), axis=1) 
						
            #to check calculation of mass
            #print(df_soil_1round[['compartment', 'subcompartment', 'tot wet weight','dry weight', fullname,f"mass {comp}"]])


            ### Make heat map comp in soil [subcompartment, compartment]    
            #
            df_soil_subcomp_grouped = \
							df_soil_1round.groupby(['soil type', 'compartment', 'subcompartment'])[f"mass {comp}"].agg('sum').reset_index()
						
            #prepare Dataframe to plot as heat map
            outdict_insoil = {} #method: make a nested dictionary, and convert that again 
            for subcomp in subcomp_names:
                df_1subcomp_temp = df_soil_subcomp_grouped[df_soil_subcomp_grouped['subcompartment'].str.contains(subcomp)]
                df_1subcomp_temp.set_index('soil type',inplace=True)
                inndict = df_1subcomp_temp[f"mass {comp}"].to_dict() #this line is different from plant mass
                outdict_insoil[subcomp]=inndict
                
            df5x4_1comp_insoil = pd.DataFrame(outdict_insoil)

            #change order of soil types (rows) and transpose for plotting
            df5x4_1comp_insoil_plot=df5x4_1comp_insoil.reindex(soiltypes_goodorder) #Activated carbon is often first, change to order in greenhouse

            # #shorten row name
            df5x4_1comp_insoil_plot=df5x4_1comp_insoil_plot.rename(index={'Activated Carbon': 'AC'})

            # Create and save the figure 
            fabfunctions.plot_heat_map(df5x4_1comp_insoil_plot, outdir_plot_soil, f"Soil_mass_{comp}_heat map_in_r{rnd}.png",\
                                color_map='Purples', vmax=None if comp == 'PFBA' else 30000, title_heat= f"Mass {comp} in soil r{rnd} ({unit_soil_NGAC[:2]})",\
                                              )#ylab ='',  annotation=None

# Plot interpolated water mass at each round start: four round bars per soil type.
round_start_dates = pd.DatetimeIndex(dates_round_plants['start'])
round_colors = dict(zip(dates_round_plants['roundnr'], sns.color_palette('tab10', len(round_start_dates))))
for comp, df_watermass_by_date in df_waterpfasmass_aggr.items():
    df_watermass_by_round_plot = (
        df_watermass_by_date
        .reindex(df_watermass_by_date.index.union(round_start_dates))
        .sort_index()
        .interpolate(method='time')
        .reindex(round_start_dates)
    )
    df_watermass_by_round_plot.index = dates_round_plants['roundnr']
    df_watermass_by_round_plot = df_watermass_by_round_plot.reindex(
        columns=soiltypes_goodorder
    ).transpose()
    fabfunctions.plot_bar_stacked(
        df_watermass_by_round_plot,
        outdir_plot_combine,
        f"Water_mass_{comp}_all_rounds.png",
        color_stacks=round_colors,
        xlab='Soil type',
        ylab=f"Mass {comp} in water ({unit_water_NGAC[:2]})",
        stacked=False,
    )

    # Align soil-type rows and round-number columns before calculating efficiency.
    df_plantmass_by_round_plot = df_plantpfasmass_aggr[comp].transpose().reindex_like(
        df_watermass_by_round_plot
    )
    ratio_plant_water_perc = df_plantmass_by_round_plot.div(
        df_watermass_by_round_plot
    ).mul(100)
    fabfunctions.plot_bar_stacked(
            ratio_plant_water_perc,
            outdir_plot_combine,
            f"Efficiency_{specie}_to_water_mass_perc_{comp}_all_rounds.png",
            color_stacks=round_colors,
            xlab='Soil type',
            ylab=f"Uptake efficiency {comp} (%)",
            stacked=False,
        )
