# -*- coding: utf-8 -*-
"""
@author: Frans Buschman, MGdV
"""
# packages
#=============================================================================
from datetime import date
from datetime import datetime #added to make list of dates
import numpy as np
import os
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

#import my own functions
import fabfunctions

# new functions   ---> in fabfunctions.py

def create_array(col:pd.DataFrame)-> np.array:
    """Create 2D numpy array from column in dataframe that contains numeric data presented as strings """

    # If present, remove all non-digit characters
    try:
        col = col.str.replace(r'\D+', '', regex=True).astype('float')    
    except:
        pass
        
    # reshape to 2D array with one column and multiple rows    
    arr = col.values.reshape(-1,1)

    return arr

def perform_regression(xcol:pd.DataFrame,ycol:pd.DataFrame):
    """Perform simple linear regression on two columns of a dataframe and return model """

    x = create_array(xcol)
    y = create_array(ycol)
    
    model = LinearRegression().fit(x,y) 
    
    return model
   

def plot_regression(path:str,fname:str,model:pd.DataFrame, xcol:pd.DataFrame,ycol:pd.DataFrame, title:str, xlab:str, ylab:str):
    """Perform simple linear regression and plot results """

    # prepare data
    x = create_array(xcol)
    y = create_array(ycol)

    ### # perform lineair regression
    ### model = LinearRegression().fit(x,y) 
    
    r_sq = round(model.score(x,y),3)
    intercept = round(model.intercept_[0],2)
    coef = round(model.coef_[0][0],4)
    formula = (f"Conc = {intercept} + {coef}* area")

    # plot results of calibration
    fig = plt.figure(figsize=(5.69, 5.27), constrained_layout=True, dpi=300)# was 11.69, 8.27
    ax = fig.add_subplot(1, 1, 1)

    ax.scatter(x,y, color='black', label = 'data') #plot scatters
    ax.plot(x,model.predict(x), color='red', linewidth=2, label = formula) #plot line
    ax.legend(title = f'R\N{SUPERSCRIPT TWO} = {r_sq}' ,loc = 'lower right')

    # Set axis labels
    ax.set_title(title) #print only the pfas component, not "_Results"
    
    ax.set(xlabel=xlab, ylabel=ylab)

    # set axis limits
    #    ax.set_ylim(0, )

    # Save plot to file
    plot_filename = os.path.join(path, fname + ".png")
    plt.savefig(plot_filename, bbox_inches='tight', dpi=300)

    plt.close(fig)  
#=============================================================================



#%% user settings
#=============================================================================

today = date.today().strftime("%Y%m%d")

rootdir = r"p:\470-gml-data\Delta-lab\projecten\fytoremediatie EMK\Data" #use raw strings for names with \
indir = r"p:\470-gml-data\Delta-lab\Intake\labwerk formulier"
workdir = os.path.join(rootdir, "Dataverwerking Python\\scripts\\_kas") #for mapping files
outdir_plot = fabfunctions.makedir(os.path.join(rootdir, f"Dataverwerking Python\\plots\\_kas\\{today}\\LC_MS"))  

# list files
fin_2025 = "2025-023 EMK PFAS Kas proeven.xlsm" 
f_mapping="Mapping_Deltalab.xlsx"

#define the soil types and PFAS components in the Delft greenhouse (used for plots)
soiltypes_goodorder = ["Sand", "Zeolite", "Charcoal","Bentonite", "Magnetite"] #the Delta-lab data uses Charcoal iso "Activated Carbon"
compounds_select = ['PFBA', 'PFHxA', 'PFHpA', 'PFOA', 'PFBS', 'PFOS', 'PFHpS', 'PFHxS']

unit_water_dl = '\u03BCg/l'  #unit for water concentration Delta-lab

#dictionary to have dates for the moments 't' given in data
dict_t= {'t0': datetime.strptime('28-Mar-2025', "%d-%b-%Y"),
            't1': datetime.strptime('02-Apr-2025', "%d-%b-%Y"),
            't3': datetime.strptime('09-Apr-2025', "%d-%b-%Y"),
            't5': datetime.strptime('15-Apr-2025', "%d-%b-%Y"),
            't6': datetime.strptime('17-Apr-2025', "%d-%b-%Y"),
            't7': datetime.strptime('22-Apr-2025', "%d-%b-%Y"),
            't9': datetime.strptime('29-Apr-2025', "%d-%b-%Y"),
            't10': datetime.strptime('02-May-2025', "%d-%b-%Y")} #dates according xls Ewan Zwart: "Final kas data.xlsx"


#settings for plots
plt.style.use('default')
plt.rcParams['font.size'] = 14. #font size used for all plt.plots
###plt.rcParams.update({'figure.max_open_warning': 0}) #suppresses (erroneous) warnings about figures that are open 

### PYDEVD_WARN_SLOW_RESOLVE_TIMEOUT:2

#%% Import
"""
Use 1st level column names, i.e. pfas compounds, to separate raw dataframe in subsets.
For each subset, also separate soil types
Store in nested dictionary: {pfas1:{soil1:data,soil2:data,soil3:data,calibr:data},pfas2:{soil1:data...}
"""
#=============================================================================

# import the LC-MS data
df = pd.read_excel(os.path.join(indir, fin_2025), sheet_name="LC_MS Delta-lab", index_col=[0,1], header=[0,1],skiprows=2)


#import the mapping, used to find the code of component as used for the NGAC files
mapping_dl = pd.read_excel(os.path.join(workdir, f_mapping), skiprows=1,\
                           index_col=1).to_dict() #map on the name used in Delta-lab results (not the code)
#print(mapping_dl['name LC-MS Delta-lab']['PFBA'])


#%% combine data
'''Create list with unique 1st level columnnames, i.e. pfas compounds (NB their name ends with " Results") '''
#=============================================================================

cols = []

for c in df.columns:
    cols.append(c[0]) #list of first out of 2 column names

# Keep 'Sample' data (same for each pfas) separate; will be added to data for each pfas compound
cols_pfas_dl = list(set(cols)) #list each unique column name (also re-orders the column names)
cols_pfas_dl.remove('Sample')

#Create nested dictionary with data for each pfas compound
outdict = {}

for pfas_dl in cols_pfas_dl:
    # combine sample data with pfas data
    df_merge = df['Sample'].merge(df[pfas_dl], left_index=True, right_index=True)
 
    # create inner dictionary with data per soil type
    indict = {}
    # select data per soil type
    for s in soiltypes_goodorder:
        df_soil = df_merge[df_merge['Name'].str.contains(s)]
        indict[s] = df_soil

    # add calibration data to inner dictionary    
    df_cal = df_merge[df_merge['Level'].notnull()]
    indict['calibration']= df_cal
    
    # create entry in outer dictionary: key is pfas compound, value is inner dictionary
    outdict[pfas_dl] = indict

outdict.keys()


#%% Process
''' Perform calibration for the pfas components with a code in the mapping file, since only these were added '''
#=============================================================================

#calibrate for the PFAS components selected for the Delft greenhouse (more components were analyzed in Delta-lab)
level_calib= range(0,8) #the level to be used for the calibration (8 refers to 200 ug/l added in this data set)

for comp in compounds_select:
    if comp in mapping_dl['name LC-MS Delta-lab']: #mapping_dl.keys():

        fullname_comp= mapping_dl['name LC-MS Delta-lab'][comp] #get the name used in Delta-lab output
        print(f'PFAS key: {comp}, with Delta-lab full name: {fullname_comp}')
        
        #Extract calibration data from nested dictionary
        df_calib = outdict[f"{fullname_comp} Results"]['calibration'] #add " Results" to match with data from LC-MS

        model_comp=perform_regression(df_calib.iloc[level_calib]['Area'], df_calib.iloc[level_calib]['Name'])

        plot_regression(outdir_plot, f"Calibration_{comp}__{fullname_comp}.png", model_comp,\
                        df_calib.iloc[level_calib]['Area'], df_calib.iloc[level_calib]['Name'],\
                        title=f"Calibration_{comp} ({fullname_comp})",\
                        xlab='Area', ylab=f"Conc ({unit_water_dl})") 

        #derive the time series
        df_conc_1comp = pd.DataFrame({'t': dict_t.values()})  #initiate new dataframe
        df_conc_1comp.set_index('t', inplace=True)

        for s in soiltypes_goodorder:
            
            #Extract calibration data from nested dictionary
            df_intime = outdict[f"{fullname_comp} Results"][s] #add " Results" to match with data from LC-MS

            if df_intime.empty:
                df_conc_1comp[s]=np.nan
            else:
                df_conc_1comp[s]=model_comp.predict(create_array(df_intime.Area))
        
        # correct the soil type name to name we selected
        df_conc_1comp=df_conc_1comp.rename(columns={"Charcoal": "Activated Carbon"}) 

        fabfunctions.plot_timeseries(df_conc_1comp, outdir_plot,
                    fname=f"Concentration in time for {comp}__{fullname_comp}",
                    ylab=f"Concentration {comp} ({unit_water_dl})")

df_conc_1comp


