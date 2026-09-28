import os

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import seaborn as sns

def makedir(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"makedir: Path did not exist, and has now been created: {path} ")
    return path


def make_data_table(file, sheets: list, cols: list, return_units=False) -> pd.DataFrame:
    """Read NGAC sheets into wide result and unit tables indexed by lab code."""
    raw_data = pd.concat(
        [pd.read_excel(file, usecols=cols, sheet_name=sheet) for sheet in sheets],
        ignore_index=True,
    )
    index_column, parameter_column, value_column, unit_column = cols

    df_data = raw_data.pivot_table(
        index=index_column, columns=parameter_column, values=value_column, aggfunc='first'
    )
    df_units = raw_data.pivot_table(
        index=index_column, columns=parameter_column, values=unit_column, aggfunc='first'
    )

    if return_units:
        return df_data, df_units
    return df_data


def plot_timeseries(df, path, fname, cmap='tab20', 
                    xlab='', ylab ='', title='', dates_round_plants=None, datesfilltanks=None, mass_ini=None):
    """
    Creates a timeseries plot of data and saves it as a PNG file.
    Contaminant is plotted on the y-axis and time plotted on the x-axis. 
    """
    # Validate input DataFrame
    if df.empty:
        raise ValueError("The provided df is empty")
    
    # Create figure
    fig = plt.figure(figsize=(11.69, 5.27), constrained_layout=True, dpi=300)#height was 8.27
    ax = fig.add_subplot(1, 1, 1)

    # Create plot
    df.plot(ax=ax, cmap=cmap, marker=".", markersize=10) #plot the dataframe
    
    if mass_ini is not None:
        #for ind in mass_ini: #possibly we get initial values for each round
        plt.plot(mass_ini.date_added, mass_ini.mass, marker='s', linestyle='None', color='red', markersize=12)
        ###mass_ini.plot(ax=ax, color='red', marker='s', markersize=12)  #alos plot in the way df.plot
    
    # add shades and vertical lines
    if dates_round_plants is not None:
        for idx, rnd in enumerate(dates_round_plants.roundnr):
            ax.axvspan(dates_round_plants.start[idx], dates_round_plants.end[idx], color = 'green', alpha=0.1)  
    
    if datesfilltanks is not None:
        for y in datesfilltanks:
            ax.axvline(y, color = 'blue', linestyle='--')  #add to current axes

    # Set axis labels
    ax.set(xlabel=xlab, ylabel=ylab)
    
    # Define the date format
    myFmt = mdates.DateFormatter("%d-%b-%Y")
    ax.xaxis.set_major_formatter(myFmt)
    
    #ax.set_xticklabels([x.strftime("%d-%b-%Y") for x in df.index], rotation=90)
    #plt.xticks(rotation='horizontal') #works, but not nice here
      
    # Set grid and minor grid
    #ax.grid(visible=True, axis='both', which='major', 
     #       color='#999999', linestyle='-', alpha=0.3)
    
    # set axis limits
    ax.set_ylim(0, )

    # # Title
    # ax.set_title(title)

    ax.legend(bbox_to_anchor=(1.3, 1),loc='upper right')# loc="best")  
   
    # Save plot to file
    plot_filename = os.path.join(makedir(path), fname + ".png")
    plt.savefig(plot_filename, bbox_inches='tight', dpi=300)

    # Close the figure after saving
    plt.close(fig)  



def plot_bar_stacked(df_bar, path, fname, color_stacks , xlab='', ylab ='', ymax=None, width_bar=None):
    """
    Creates a stacked bar plot a bar for each column in 'df_bar' 
    and a slice for each row of 'df_bar'. Legend is plotted for the rows.
    """
    # Validate input DataFrame
    if df_bar.empty:
        raise ValueError("The provided df is empty")
    
    if width_bar == None:
        width_bar=0.7 #my default width (nice for 5 bars)

    # Create figure
    fig = plt.figure(figsize=(6, 5.27), constrained_layout=True, dpi=300)#width was 11.69; height was 8.27
    ax = fig.add_subplot(1, 1, 1)

    # Create plot
    df_bar.plot.bar(ax=ax, stacked=True, rot=0, width=width_bar, color=color_stacks,figsize=(6, 5.27)) 

    # set y-axis limits
    if ymax == None:
        ax.set_ylim(0, )
    else:
        ax.set_ylim(0, ymax)

    # Set axis labels
    ax.set(xlabel=xlab, ylabel=ylab)
    
    # make legend
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1], loc='upper right')#bbox_to_anchor=(1.17, 1),  #the horizontal position is different than in matplotlib plots

    plt.savefig(os.path.join(path, fname), bbox_inches='tight', dpi=300) #using the matplotlib function to save the figure
    
    plt.close(fig)
    

def plot_heat_map(df_heat, path, fname, color_map , title_heat='', ylab ='', vmax=None, annotation=None):
    """
    Creates a heat map for the transposed 'df_heat'. 
    Legend is plotted for the rows and its max value can be controlled with vmax.
    """
    # Validate input DataFrame
    if df_heat.empty:
        raise ValueError("The provided df to make heat map is empty")
    
    if annotation == None:
        annot=False
    else:
        annot=True

    fig = plt.figure(figsize=(7.69, 5.27), constrained_layout=True, dpi=300)#make it close to a square shape
    ax = fig.add_subplot(1, 1, 1)
                
    sns.heatmap(df_heat.transpose(), cmap=color_map, vmin=0, vmax=vmax, cbar=True, annot=annot, ax=ax)  # max(df5x4_1comp_subcomp_soil_plot.max(axis=1))

    ax.set_title(title_heat)

    plt.savefig(os.path.join(path,fname), bbox_inches='tight', dpi=300) #using the matplotlib function to save the figure
    plt.close(fig)   
    
    