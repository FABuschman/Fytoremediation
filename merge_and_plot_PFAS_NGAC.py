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
workdir = os.path.join(rootdir, "Dataverwerking Python\\scripts\\_kas") #for mapping files
outdir_plot_water = fabfunctions.makedir(os.path.join(rootdir, f"Dataverwerking Python\\plots\\_kas\\{today}\\water"))  
outdir_plot_plant = fabfunctions.makedir(os.path.join(rootdir, f"Dataverwerking Python\\plots\\_kas\\{today}\\plant"))  
outdir_plot_plant_dry_wet = fabfunctions.makedir(os.path.join(rootdir,\
                                                               f"Dataverwerking Python\\plots\\_kas\\{today}\\plant\\Conc_dry_wet"))  #subdir
outdir_plot_gado = fabfunctions.makedir(os.path.join(rootdir, f"Dataverwerking Python\\plots\\_kas\\{today}\\gadolinium"))  #subdir
outdir_plot_soil = fabfunctions.makedir(os.path.join(rootdir, f"Dataverwerking Python\\plots\\_kas\\{today}\\soil"))  

# list files
fin_2025 = "2025-023 EMK PFAS Kas proeven.xlsm" #2025
fin_2026 = "2026-004 Fyto-PFAS kas Delft proeven.xlsm" #the last samples of round 3 taken in 2026, including a re-analysis of two water sampling moments 
    #the re-analysis results are in a separate tab, and the results of the first (wrong) analysis are removed from the other tab (on sampling moment was in 2025)

fin_waterini = "initial_mass.csv" #PFAS mass added to the water (not the pure PFAS mass); Note that "initial_waterconcentration.csv" is the concentration measured from effluent, not from tank

# dataframe with the dates of sowing and harvesting; take care: index and roundnr available
dates_round_plants= pd.DataFrame({"start":[datetime.strptime('28-Mar-2025', "%d-%b-%Y"), datetime.strptime('28-May-2025', "%d-%b-%Y"),\
                                           datetime.strptime('11-Sep-2025', "%d-%b-%Y"), datetime.strptime('01-May-2026', "%d-%b-%Y"),
                                           datetime.strptime('14-Jul-2026', "%d-%b-%Y")], \
                                  "end": [datetime.strptime('16-May-2025', "%d-%b-%Y"), datetime.strptime('14-Aug-2025', "%d-%b-%Y"),\
                                         datetime.strptime('21-jan-2026', "%d-%b-%Y"), datetime.strptime('15-Jul-2026', "%d-%b-%Y"),
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
soiltypes_goodorder = ["Sand", "Zeolite", "Activated Carbon","Bentonite", "Magnetite",
                       "Biochar", "No adsorbant", "Sand+salt","Iron-zeolite"] #add the three new ones ("No adsorbant" means "Sand" in compartment 4)

#settings for plots
plt.style.use('default')
plt.rcParams['font.size'] = 14. #font size used for all plt.plots
plt.rcParams.update({'figure.max_open_warning': 0}) #suppresses (erroneous) warnings about figures that are open 


#%% Import
#=============================================================================

# import reconstructed water volume with Date as the index column 
vol_reconstr = pd.read_excel(os.path.join(indir, fin_2025),    
                         sheet_name="Watervolume",
                         usecols=["Date", "Sand", "Zeolite", "Activated Carbon","Bentonite", "Magnetite"], skiprows=6, index_col=0)
wl_from_r4 = pd.read_excel(os.path.join(indir, fin_2026),\
                         sheet_name ='Watervolume',usecols=["Date", "Sand", "Zeolite", "Biochar","Iron-Zeolite", "Sand+salt"], skiprows=3,index_col=0) #for round 3 last part
# Known volume at water level (see labform Watervolume)
Lookup_from_r4 = pd.read_excel(os.path.join(indir, fin_2026),\
                         sheet_name ='Watervolume',usecols=["water level (cm)", "Volume (l)"], skiprows=3,index_col=0) #the lookup table water level --> volume since round 4

# Perform interpolation
#= wl_from_r4
vol_interpolated_since_r4 = pd.DataFrame(
    np.interp(
        wl_from_r4.to_numpy(),
        Lookup_from_r4.index.to_numpy(),
        Lookup_from_r4['Volume (l)'].to_numpy(),
    ),
    index=wl_from_r4.index,
    columns=["Sand", "Zeolite", "Biochar", "Iron-Zeolite", "Sand+salt"], #is this copy of adsorbants needed?
)


print(vol_interpolated_since_r4)

df_vol_allrounds = pd.concat([vol_reconstr, vol_interpolated_since_r4], ignore_index=False, sort=False) 





#Total PFAS mass added (microg) to each water storage reservoir 
pfas_ini = pd.read_csv(os.path.join(workdir, fin_waterini), sep=';')
pfas_ini= pfas_ini.rename(index={0: 'mass from bottle'})
pfas_ini= pfas_ini.rename(index={1: 'purity_factor'})
pfas_ini.loc[len(pfas_ini)]=pfas_ini.loc['mass from bottle',:]*pfas_ini.loc['purity_factor',:]*1000/5 #new row
pfas_ini= pfas_ini.rename(index={2: 'mass'}) #the mass PFAS added

#add a row with dates (should be datetime to be plotted with other datetime data)
pfas_ini.loc[len(pfas_ini)]= [datetime.strptime('28-Mar-2025', "%d-%b-%Y")] *6
pfas_ini.loc[3]['PFBS']= datetime.strptime('14-Apr-2025', "%d-%b-%Y") #only PFBS was added later
    #mass_pfas_ini.loc[1, len(mass_pfas_ini)]= mass_pfas_ini.loc[1, len(mass_pfas_ini)].date() #trying to convert to datetime again to avoid warning...
pfas_ini= pfas_ini.rename(index={3: 'date_added'})

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

#combine weights
weight_allrounds = pd.concat([weight_round1, weight_round2, weight_round3], ignore_index=False, sort=False) #round 3 to be added from 2026 data

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
mapping_agro = pd.read_csv(os.path.join(workdir, "mapping.csv"), sep=';',
                      index_col=1).to_dict() #index_col set to 1, as in NGAC data the full name is used, so key=full name


#% import data from Agro Control (NGAC)
cols_data_agro = ['Monster::MonstercodeKlant','Parameter','TextWaarde','EenheidCode']

#2025 (note that NGAC re-analyzed the last set of water samples of 2025: the correct ones are included in the lab form)
# for raw data from NGAC (for some samples 3 numbers), see folder: Data\PFAS data\Agro control\__rawdata)
xls_2025 = pd.ExcelFile(os.path.join(indir, fin_2025))
sheets_agro_2025= [s for s in xls_2025.sheet_names if ("PFAS NGAC" in s) and ("ICP" not in s)]
df_raw_agro, df_units_agro = fabfunctions.make_data_table(
    os.path.join(indir, fin_2025), sheets_agro_2025, cols_data_agro, return_units=True
)  # convert all lines to structured data tables

#2026 (note that NGAC re-analyzed the first set of water samples of 2025: the correct ones are included in the lab form)
# for raw data from NGAC (for some samples 3 numbers), see folder: Data\PFAS data\Agro control\__rawdata)
xls_2026 = pd.ExcelFile(os.path.join(indir, fin_2026))
sheets_agro_2026= [s for s in xls_2026.sheet_names if ("NGAC LCMS" in s) and ("ICP" not in s)]
df_raw_agro2, df_units_agro2 = fabfunctions.make_data_table(
    os.path.join(indir, fin_2026), sheets_agro_2026, cols_data_agro, return_units=True
)  # convert all lines to structured data tables
#df_raw_agro2['Monster::MonstercodeKlant']

df_raw_agro_allrounds= pd.concat([df_raw_agro, df_raw_agro2], ignore_index=False, sort=False)
df_units_agro_allrounds = pd.concat([df_units_agro, df_units_agro2], ignore_index=False, sort=False)



# Convert all non-numeric data (except np.nan)
for col in df_raw_agro_allrounds.columns:
    df_raw_agro_allrounds[col] = pd.to_numeric(df_raw_agro_allrounds[col], errors='coerce') #numbers were text in xls; with coerce directly make text with '<' NaN


#%% combine data
#=============================================================================

# Keep only lab codes present in both the metadata and NGAC result tables.
df_all_agro = df_meta_allrounds.join(df_raw_agro_allrounds, how='inner', validate='one_to_one')
df_all_agro = df_all_agro.join(
    df_units_agro_allrounds.add_suffix(' unit'), how='left', validate='one_to_one'
)

#for 2025-023-474 there are lines in both labformulier and NGAC data (though empty), resulting in a row in df_all_agro with text iso a date: 
df_all_agro.loc[df_all_agro['Date'] == 'Geen bloem beschikbaar'] = np.nan # make this text NaN to avoid errors later
    #df_all_agro['Date'].apply(lambda x: x if isinstance(x,datetime) else np.nan) #no filling of the nan, as that is risky   .fillna(method = "ffill")

# In 2026, average original and duplo measurements into one sample record.
df_all_agro['labcode'] = df_all_agro.index
df_all_agro['is duplo'] = df_all_agro['sample name'].str.contains('duplo', case=False, na=False)
df_all_agro['sample name'] = df_all_agro['sample name'].str.replace(
    r'\s*duplo\s*', '', case=False, regex=True
).str.strip()
result_columns = df_raw_agro_allrounds.columns
group_columns = df_all_agro.columns.difference(result_columns.union(['labcode', 'is duplo']), sort=False).tolist()
df_all_agro = (
    df_all_agro.sort_values('is duplo')
    .groupby(group_columns, dropna=False, as_index=False)
    .agg({**{column: 'mean' for column in result_columns}, 'labcode': 'first'})
    .set_index('labcode')
)

df_water_agro = df_all_agro.loc[df_all_agro['matrix'] == 'Water',:]
print(f'Number of rows df_all_agro {np.size(df_all_agro,0)} , of which water: {np.size(df_water_agro,0)}')

df_plant_agro = df_all_agro.loc[df_all_agro['matrix'] == 'Plant',:]
    #df_plant_agro['Date'][128:132]
print(f'Number of rows df_all_agro {np.size(df_all_agro,0)} , of which plant: {np.size(df_plant_agro,0)}')

#in 2025 lab formulier "Bodem" consistently used, whereas in 2026 "Soil" is used (all English)
df_soil_agro = df_all_agro.loc[(df_all_agro['matrix'] == 'Bodem') | (df_all_agro['matrix'] == 'Soil'), :]  
print(f'Number of rows df_all_agro {np.size(df_all_agro,0)} , of which soil: {np.size(df_soil_agro,0)}')

def get_ngac_unit(dataframe, parameter):
    units = dataframe[f'{parameter} unit'].dropna().unique()
    if len(units) == 0:
        raise ValueError(f'No unit found for {parameter}')
    return units[0]


#to check combining the data
#pd.set_option('display.max_columns', None) 
#pd.set_option('display.max_rows', None)
#print(df_all_agro[:5])

#%% Process
#=============================================================================

#%Estimate volume of water per compartment, which can be multiplied by pivot dataframe (concentration) to yield mass
#vol_tank_full=266 # the volume of water (l) per compartment when tank is full 
vol_water_wetsoil=50 #the volume of water in wet (terrestrial) soil, see box A (Zwart, 2025)

#% Interpolate the reconstructed watervolume per compartment on sampling dates 
vol_reconstr['date_float'] = [da.timestamp() for da in vol_reconstr.index] #add column with numeric date (float) for interpolation;   .index.to_list()
vol_reconstr.set_index('date_float',inplace=True) #modify dataframe forever (not creating a new one; for debugging still to be possible I only use it when I change the index)

dates_sampling= df_water_agro.loc[:,"Date"].unique()  #now with loc (later to be checked that pivot table has same dates)
df_vol = pd.DataFrame({'date':dates_sampling})
df_vol.set_index('date', inplace=True)

dates_sampling_float= [da.timestamp() for da in dates_sampling] #numeric date (float) needed for interpolation; 

for soil in vol_reconstr.columns:  #INTERPOLATE VOLUME in tank for soil ('type' cannot be used, as it is protected)
     df_vol[soil] = np.interp(dates_sampling_float, 
                                vol_reconstr.index.to_list(), vol_reconstr[soil].values) #soil must be [], and not in between .., since a space occurs in one of the names

#Add water volume in soil and plant for all times but the first (rough estimate, assuming it is always wetted)
df_vol_wetsoil= df_vol.copy() #copy the dataframe and numbers   
for index, j in enumerate(df_vol_wetsoil):
    df_vol_wetsoil[j][1:len(df_vol_wetsoil[j])]=df_vol_wetsoil[j][1:len(df_vol_wetsoil[j])]+vol_water_wetsoil

df_vol_wetsoil_plot=df_vol_wetsoil.reindex(soiltypes_goodorder, axis="columns") #Activated carbon is often first, change to order in greenhouse

#plot the volume that was reconstructed from marks and logbook
fabfunctions.plot_timeseries(df_vol_wetsoil_plot, outdir_plot_water,
                     fname= f"Water volume in tank and soil_interpolated on t(PFAS)", ylab=f"Water volume in tank and soil (l)", 
                     dates_round_plants=dates_round_plants, datesfilltanks=datesfilltanks) 

#Estimate water volume from assuming that mass(CL) is preserved (second method)
# # df_vol = pd.DataFrame({'date':dates_sampling})
# # df_vol.set_index('date', inplace=True)

# # dates_sampling_float= [da.timestamp() for da in dates_sampling] #numeric date (float) needed for interpolation; 

# # for soil in vol_reconstr.columns:  #INTERPOLATE VOLUME for soil ('type' cannot be used, as it is protected)
# #     df_vol[soil] = np.interp(dates_sampling_float, 
# #                                vol_reconstr.index.to_list(), vol_reconstr[soil].values) #soil must be [], and not in between .., since a space occurs in one of the names

# # df_vol_plot=df_vol.reindex(soiltypes_goodorder) #Activated carbon is often first, change to order in greenhouse

# # fabfunctions.plot_timeseries(df_vol, outdir_plot_water,
# #                      fname= f"Water volume on sampling", ylab=f"Interpolated water volume (l)", 
# #                      dates_round_plants=dates_round_plants, datesfilltanks=datesfilltanks) #plot the interpolatede volume, which is used further on


#%% Plot water data
#=============================================================================                                                         
#% Make figure of PFAS in water over time

#analyse for these PFAS compounds
compounds_select = ['PFBA', 'PFHxA', 'PFHpA', 'PFOA', 'PFBS', 'PFOS', 'PFHpS', 'PFHxS',
                    'PFPeA', 'PFPeS', 'PFHpS', '4:2 FTS', '6:2 FTS'] #this row added 20 April 2026 (6:2 FTS on 20 May)

for comp in compounds_select:
    if comp in mapping_agro['naam'].keys():
        fullname = mapping_agro['naam'][comp]
        unit_water_NGAC = get_ngac_unit(df_water_agro, fullname)
               
        # Average repeated measurements for the same sampling date and soil type.
        df_pivot = df_water_agro.pivot_table(
            index='Date', columns='soil type', values=fullname, aggfunc='mean'
        )
        
        print(f'Making pivot water for PFAS key: {comp}, with full name: {mapping_agro['naam'][comp]}')
    
        ### plot concentration   #first and second argument need to given, others are matched by defined name
        df_pivot_plot=df_pivot.reindex(soiltypes_goodorder, axis="columns") #Activated carbon is often first, change to order in greenhouse

        figname = f"Water_conc  {comp.replace(':','_')}"
        fabfunctions.plot_timeseries(df_pivot_plot, outdir_plot_water,
                    fname=figname, ylab=f"Concentration {comp} ({unit_water_NGAC})", 
                    dates_round_plants=dates_round_plants, datesfilltanks=datesfilltanks)
    
        # #Multiply with volume to arrive at mass
        # df_mass_plot= pd.DataFrame(df_vol_wetsoil.values*df_pivot_plot.values, columns=df_pivot_plot.columns, index=df_pivot_plot.index) #temporarily made for each soil

        #### plot mass  
        ###df_mass_plot=df_mass.reindex(soiltypes_goodorder, axis="columns") #Activated carbon is often first, change to order in greenhouse
 


 #for now manually delect the mass lines, since the volume is not yet calculated for the last samples...
   #     figname = f"Water_mass_ {comp.replace(':','_')}"
        
        
   #     if comp in list(pfas_ini.columns): #for the components that were added
   #         fabfunctions.plot_timeseries(df_mass_plot, outdir_plot_water,
   #                 fname=figname, ylab=f"Mass {comp} ({unit_water_NGAC[:2]})",  #assuming volume to be in [l]
   #                 dates_round_plants=dates_round_plants, datesfilltanks=datesfilltanks, mass_ini=pfas_ini[comp])
   #    else:                                   #for the components that were not added
   #         fabfunctions.plot_timeseries(df_mass_plot, outdir_plot_water, 
   #                 fname=figname, ylab=f"Mass {comp} ({unit_water_NGAC[:2]})",  #assuming volume to be in [l]
   #                 dates_round_plants=dates_round_plants, datesfilltanks=datesfilltanks)
    

#check for last compund that dates sampling and in pivot were indeed the same
dates_pivot_float= [d.timestamp() for d in df_pivot.index] #numeric date (float) needed for interpolation; 

print(f"Sampling dates and dates according pivot should be within 12 hours, check: ")
print(np.isclose(dates_pivot_float, dates_sampling_float, rtol=1e-10, atol=12*60*60, equal_nan=True))




#%% Plot plantdata
#=============================================================================                                                         

#make plots for these plant species, per round, per PFAS component 
species=['sunflower', 'plantain']

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

#distribute the plants with subcompartment "A tm D" over the first three subcompartments
df_plant_agro.loc[['2026-004-022','2026-004-023','2026-004-024'],'subcompartment']='a'
df_plant_agro.loc[['2026-004-025','2026-004-026','2026-004-027'],'subcompartment']='b'
df_plant_agro.loc[['2026-004-028','2026-004-029','2026-004-030'],'subcompartment']='c'
###df_plant_agro['subcompartment'] = df_plant_agro['subcompartment'].str.replace('A t/m D,','a') 

alignunits_g_to_kg=1/1000 #divide by 1000

dates_round_plants_ext

# check of total wet mass plants
wet_mass_plants_tot= df_plant_agro['tot wet weight']
df_numeric = wet_mass_plants_tot.apply(pd.to_numeric, errors='coerce')
df_numeric.sum()

for specie in species:
    
    # filter data frame on plant species
    df_plant_1specie = df_plant_agro[df_plant_agro['biota'] == specie].reset_index(drop= True)
        
    #print(df_plant_1specie[['dry weight', 'dry factor']]) #print several columns (note that [[]] is needed for column indexing)

    for rnd in  dates_round_plants_ext.roundnr: #per round of plants
        #find the rows within the period of a round
        mask_1rnd = (df_plant_1specie['Date'] > dates_round_plants_ext.start[rnd-1]) & (df_plant_1specie['Date'] <= dates_round_plants_ext.end[rnd-1])
        
        df_plant_1specie_1round={} #clear data from previous round
        df_plant_1specie_1round= df_plant_1specie.loc[mask_1rnd].reset_index() 

        print(f"For round {rnd} dates of harvesting {specie} aggregated in the plots were: ")  
        print(df_plant_1specie_1round.Date.unique())
    
        

        ### barplot plant mass dry weight plant: sum plant MASSes from multiple samples and over subcompartments
        ### 
        df_plant_1specie_1round_aggr = \
                df_plant_1specie_1round.groupby(['soil type', 'compartment', 'plant tissue'])['dry weight'].agg('sum').reset_index()
        
        #print(f"Aggregated plant mass for {specie} and round {rnd} ") 
        #print(df_plant_1specie_1round_aggr)

        #prepare Dataframe to plot as bar
        outdict_tis_soil = {} #method: make a nested dictionary, and convert that again to get a complete 5x5 DataFrame (reason for method: not always data are available for each plant tissue)
        for tis in tissue_names:
            df_1tis_temp = df_plant_1specie_1round_aggr[df_plant_1specie_1round_aggr['plant tissue'].str.contains(tis)]
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
        fabfunctions.plot_bar_stacked(df5x5_tis_soil_plot, outdir_plot_plant, f"Plant_mass_{specie}_r{rnd}.png",\
                          color_stacks=bar_colors, ymax=600, ylab =f"Mass {specie} per tissue round {rnd} (g dw)" , )
        
        
        
        ### Make heat map plant mass [subcompartment, compartment]    
        #
        df_plant_subcomp_aggr = \
                df_plant_1specie_1round.groupby(['soil type', 'compartment', 'subcompartment'])['dry weight'].agg('sum').reset_index()
        
        #prepare Dataframe to plot as heat map
        outdict_subcomp_soil = {} #method: make a nested dictionary, and convert that again 
        for subcomp in subcomp_names:
            df_1subcomp_temp = df_plant_subcomp_aggr[df_plant_subcomp_aggr['subcompartment'].str.contains(subcomp)]
            df_1subcomp_temp.set_index('soil type',inplace=True)
            inndict = df_1subcomp_temp[f"dry weight"].to_dict() #this line is different from plant mass
            outdict_subcomp_soil[subcomp]=inndict


        df5x4_1comp_subcomp_soil = pd.DataFrame(outdict_subcomp_soil)

        #change order of soil types (rows) and transpose for plotting
        df5x4_1comp_subcomp_soil_plot=df5x4_1comp_subcomp_soil.reindex(soiltypes_goodorder) #Activated carbon is often first, change to order in greenhouse
        
        # #shorten row name
        df5x4_1comp_subcomp_soil_plot=df5x4_1comp_subcomp_soil_plot.rename(index={'Activated Carbon': 'AC'})

        # Create and save the figure 
        fabfunctions.plot_heat_map(df5x4_1comp_subcomp_soil_plot, outdir_plot_plant, f"Plant_mass_{specie}_heat map_in_r{rnd}.png",\
                                        color_map='YlGn', title_heat= f"Mass {specie} for round {rnd} (g)",\
                                        vmax=250)#ylab ='', annotation=None
        
        
        
        ### Plots of wet vs. dry mass + 
        # barplot PFAS mass in plant  +  heat map to show variation over subcompartments
        ### 
        for comp in compounds_select:
            if comp in mapping_agro['naam'].keys():
                fullname = mapping_agro['naam'][comp]
                unit_plant_NGAC = get_ngac_unit(df_plant_agro, fullname)

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
                #aggregate mass per compartment: sum all MASSes in compartment per plant tissue
                df_mass1comp_1sp_1r_aggr = \
                        df_plant_1specie_1round.groupby(['soil type', 'compartment', 'plant tissue'])[f"mass {comp}"].agg('sum').reset_index()
                
                #print(f"Mass for {comp} aggregated per compartment for {specie} and round {rnd} ") 
                #print(df_mass1comp_1sp_1r_aggr)

                #prepare Dataframe to plot as bar
                outdict_tis_soil = {} #method: make a nested dictionary, and convert that again to get a complete 5x5 DataFrame (reason for method: not always data are available for each plant tissue)
                for tis in tissue_names:
                    df_1tis_temp = df_mass1comp_1sp_1r_aggr[df_mass1comp_1sp_1r_aggr['plant tissue'].str.contains(tis)]
                    df_1tis_temp.set_index('soil type',inplace=True)
                    inndict = df_1tis_temp[f"mass {comp}"].to_dict() #this line is different from plant mass
                    outdict_tis_soil[tis]=inndict
                    
                df5x5_1comp_tis_soil = pd.DataFrame(outdict_tis_soil)

                #change order of soil types (rows)
                df5x5_1comp_tis_soil_plot=df5x5_1comp_tis_soil.reindex(soiltypes_goodorder) #Activated carbon is often first, change to order in greenhouse
                
                #shorten row name
                df5x5_1comp_tis_soil_plot=df5x5_1comp_tis_soil_plot.rename(index={'Activated Carbon': 'AC'})

                
                ### Create and save stacked bar plot: for whole round and uptake per day
                #
                fabfunctions.plot_bar_stacked(df5x5_1comp_tis_soil_plot, outdir_plot_plant, f"{specie}_mass_{comp}_in_r{rnd}.png",\
                                               ylab=f"Mass {comp} in {specie} tissue for round {rnd} ({unit_plant_NGAC[:2]})",\
                                               color_stacks=bar_colors) #no ymax
                
                n_days_rnd=pd.Timedelta(dates_round_plants.loc[rnd-1,'duration_rnd']).days #number of days for this round as integer
                fabfunctions.plot_bar_stacked(df5x5_1comp_tis_soil_plot/n_days_rnd,\
                                               outdir_plot_plant, f"DailyUptake_{specie}_mass_{comp}_in_r{rnd}.png",\
                                               ylab=f"Daily uptake {comp} r{rnd} ({n_days_rnd} d) in {specie} ({unit_plant_NGAC[:2]}/d)",\
                                               color_stacks=bar_colors, ymax=60 ) #ymax from PFBA to compare rounds and components
                


                ### Make heat map comp in plant [subcompartment, compartment]    
                #aggregate mass per compartment and SUBcompartment: sum all samples including different plant tissue
                df_mass_subcomp_aggr = \
                        df_plant_1specie_1round.groupby(['soil type', 'compartment', 'subcompartment'])[f"mass {comp}"].agg('sum').reset_index()
                
                #print(f"Mass for {comp} aggregated per SUBcompartment for {specie} and round {rnd} ") 
                #print(df_mass_subcomp_aggr)

                #prepare Dataframe to plot as heat map
                outdict_subcomp_soil = {} #method: make a nested dictionary, and convert that again 
                for subcomp in subcomp_names:
                    df_1subcomp_temp = df_mass_subcomp_aggr[df_mass_subcomp_aggr['subcompartment'].str.contains(subcomp)]
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
                                        color_map='YlOrRd', title_heat= f"Mass {comp} in {specie} for round {rnd} ({unit_plant_NGAC[:2]})",\
                                        vmax=1300)


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
            unit_soil_NGAC = get_ngac_unit(df_soil_agro, fullname)

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
            df_soil_subcomp_aggr = \
							df_soil_1round.groupby(['soil type', 'compartment', 'subcompartment'])[f"mass {comp}"].agg('sum').reset_index()
						
            #prepare Dataframe to plot as heat map
            outdict_insoil = {} #method: make a nested dictionary, and convert that again 
            for subcomp in subcomp_names:
                df_1subcomp_temp = df_soil_subcomp_aggr[df_soil_subcomp_aggr['subcompartment'].str.contains(subcomp)]
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
                                        color_map='Purples', vmax=30000, title_heat= f"Mass {comp} in soil for round {rnd} ({unit_soil_NGAC[:2]})",\
                                              )#ylab ='', vmax=1000, annotation=None
