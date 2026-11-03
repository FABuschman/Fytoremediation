import os

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Patch
import numpy as np
import pandas as pd
import seaborn as sns

def makedir(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"makedir: Path did not exist, and has now been created: {path} ")
    return path


def make_data_table(file, sheets: list, cols: list) -> pd.DataFrame:
    """Read NGAC sheets into wide result tables indexed by lab code."""
    raw_data = pd.concat(
        [pd.read_excel(file, usecols=cols, sheet_name=sheet) for sheet in sheets],
        ignore_index=True,
    )
    index_column, parameter_column, value_column = cols

    df_data = raw_data.pivot_table(
        index=index_column, columns=parameter_column, values=value_column, aggfunc='first'
    )
    return df_data


def plot_timeseries(df, path, fname, cmap='tab20', 
                    xlab='', ylab ='', title='', ymax=None,
                    dates_round_plants=None, datesfilltanks=None, mass_ini=None):
    """
    Creates a timeseries plot of data and saves it as a PNG file.
    Contaminant is plotted on the y-axis and time plotted on the x-axis. 
    """
    # Validate input DataFrame
    if df.empty:
        return #no plot is made
    
    # Create figure
    fig = plt.figure(figsize=(11.69, 5.27), constrained_layout=True, dpi=300)#height was 8.27
    ax = fig.add_subplot(1, 1, 1)

    # Create plot
    df.plot(ax=ax, cmap=cmap, marker=".", markersize=10) #plot the dataframe
    
    if mass_ini is not None:
        if 'date_added' in mass_ini.columns:
            for soiltype in mass_ini.columns.drop('date_added'):
                if soiltype in df.columns:
                    water_mass_color = next(
                        (
                            line.get_color()
                            for line in ax.get_lines()
                            if line.get_label() == soiltype
                        ),
                        None,
                    )
                    initial_mass = mass_ini[['date_added', soiltype]].dropna()
                    ax.plot(
                        initial_mass['date_added'],
                        initial_mass[soiltype],
                        marker='s',
                        linestyle='None',
                        color=water_mass_color,
                        markersize=8, # label=f'{soiltype} initial mass',
                    )
        elif {'date_added', 'mass'}.issubset(mass_ini.columns): #can be removed?
            ax.plot(
                mass_ini.date_added,
                mass_ini.mass,
                marker='s',
                linestyle='None',
                color='red',
                markersize=12,
            )
    
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
    if ymax == None:
        ax.set_ylim(0, )
    else:
        ax.set_ylim(0, ymax)
    
    # # Title
    # ax.set_title(title)

    ax.legend(bbox_to_anchor=(1.3, 1),loc='upper right')# loc="best")  
   
    # Save plot to file
    plot_filename = os.path.join(makedir(path), fname + ".png")
    plt.savefig(plot_filename, bbox_inches='tight', dpi=300)

    # Close the figure after saving
    plt.close(fig)  



def plot_bar_stacked(df_bar, path, fname, color_stacks , xlab='', ylab ='', ymax=None, width_bar=None, stacked=True):
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
    df_bar.plot.bar(ax=ax, stacked=stacked, rot=90, width=width_bar, color=color_stacks,figsize=(6, 5.27)) 

    # set y-axis limits
    if ymax == None:
        ax.set_ylim(0, )
    else:
        ax.set_ylim(0, ymax)

    # Set axis labels
    ax.set(xlabel=xlab, ylabel=ylab)
    
    # make legend
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(
        handles,
        labels,
        loc='upper left',
        bbox_to_anchor=(1.02, 1),
        borderaxespad=0,
    )

    plt.savefig(os.path.join(path, fname), bbox_inches='tight', dpi=300) #using the matplotlib function to save the figure
    
    plt.close(fig)
    

def plot_bar_grouped_stacked(data, path, fname, color_groups, xlab='', ylab=''):
    """Plot one stacked bar per column, grouped by the DataFrame index."""
    if not data:
        raise ValueError("At least one stack is required")
    frames = list(data.values())
    if frames[0].empty:
        raise ValueError("The provided data is empty")
    if any(not frame.index.equals(frames[0].index)
           or not frame.columns.equals(frames[0].columns) for frame in frames[1:]):
        raise ValueError("All stacks must have the same index and columns")

    soils = frames[0].index
    compounds = frames[0].columns
    hatches = ('//', '', '..')
    if len(data) > len(hatches):
        raise ValueError("Not enough hatch patterns for the requested stacks")
    x = np.arange(len(soils))
    width = 0.8 / len(compounds)
    fig, ax = plt.subplots(figsize=(max(8, len(soils) * 1.5), 5.27),
                           constrained_layout=True, dpi=300)

    for i, compound in enumerate(compounds):
        positions = x - 0.4 + (i + 0.5) * width
        values = np.column_stack([frame[compound].to_numpy(dtype=float) for frame in frames])
        available = np.isfinite(values).all(axis=1)
        positive_bottom = np.zeros(len(soils))
        negative_bottom = np.zeros(len(soils))
        for stack_index, (stack_name, _) in enumerate(data.items()):
            heights = values[:, stack_index]
            bottom = np.where(heights >= 0, positive_bottom, negative_bottom)
            ax.bar(positions[available], heights[available], width,
                   bottom=bottom[available], color=color_groups[compound],
                   hatch=hatches[stack_index], edgecolor='black', linewidth=0.4)
            positive_bottom += np.where(available & (heights > 0), heights, 0)
            negative_bottom += np.where(available & (heights < 0), heights, 0)
        for position in positions[~available]:
            ax.text(position, 0, 'n/a', rotation=90, ha='center', va='bottom', fontsize=6)

    ax.axhline(100, color='black', linestyle='--', linewidth=0.8)
    ax.set_xticks(x, soils, rotation=90)
    ax.set(xlabel=xlab, ylabel=ylab)
    #lower, upper = ax.get_ylim()
    ax.set_ylim(0,100)

    compound_legend = ax.legend(
        handles=[Patch(facecolor=color_groups[compound], label=compound) for compound in compounds],
        loc='upper left', bbox_to_anchor=(1.02, 1),
    )
    ax.add_artist(compound_legend)
    ax.legend(
        handles=[Patch(facecolor='white', edgecolor='black', hatch=hatch, label=name)
                 for name, hatch in zip(data, hatches)],
       loc='lower left', bbox_to_anchor=(1.02, 0),
    )
    plt.savefig(os.path.join(path, fname), bbox_inches='tight', dpi=300)
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
    
    