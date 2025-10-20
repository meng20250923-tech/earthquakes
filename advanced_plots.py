"""
Advanced Earthquake Data Visualization
Creating map-based visualizations with optional year filtering and animations
"""

from datetime import date, datetime
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from collections import defaultdict
import earthquakes


def get_year(earthquake):
    """Extract the year from an earthquake record."""
    timestamp = earthquake['properties']['time']
    return date.fromtimestamp(timestamp/1000).year


def get_date(earthquake):
    """Extract the full date from an earthquake record."""
    timestamp = earthquake['properties']['time']
    return datetime.fromtimestamp(timestamp/1000)


def get_magnitude(earthquake):
    """Get the magnitude of an earthquake."""
    return earthquake['properties']['mag']


def get_location(earthquake):
    """Get the longitude and latitude of an earthquake."""
    coords = earthquake['geometry']['coordinates']
    longitude = coords[0]
    latitude = coords[1]
    return longitude, latitude


def filter_by_year(earthquakes, year=None):
    """
    Filter earthquakes by year.
    
    Parameters:
        earthquakes: List of earthquake records
        year: Optional year to filter by. If None, returns all earthquakes.
    
    Returns:
        Filtered list of earthquakes
    """
    if year is None:
        return earthquakes
    
    return [eq for eq in earthquakes if get_year(eq) == year]


def plot_earthquake_map(earthquakes, year=None, save_filename='earthquake_map.png'):
    """
    Create a map showing earthquake locations with magnitude-scaled circles.
    
    Parameters:
        earthquakes: List of earthquake records
        year: Optional year to filter data. If None, shows all years.
        save_filename: Filename to save the plot
    """
    # Filter by year if specified
    filtered_quakes = filter_by_year(earthquakes, year)
    
    if len(filtered_quakes) == 0:
        print(f"No earthquakes found for year {year}")
        return
    
    # Extract data
    lons = []
    lats = []
    mags = []
    
    for eq in filtered_quakes:
        lon, lat = get_location(eq)
        mag = get_magnitude(eq)
        if mag is not None:
            lons.append(lon)
            lats.append(lat)
            mags.append(mag)
    
    # Create figure with map projection
    fig = plt.figure(figsize=(14, 10))
    ax = plt.axes(projection=ccrs.PlateCarree())
    
    # Set map extent (UK region)
    ax.set_extent([-10, 2, 49, 59], crs=ccrs.PlateCarree())
    
    # Add map features
    ax.add_feature(cfeature.COASTLINE, linewidth=1.5)
    ax.add_feature(cfeature.BORDERS, linestyle=':', linewidth=1)
    ax.add_feature(cfeature.LAND, facecolor='lightgray', alpha=0.3)
    ax.add_feature(cfeature.OCEAN, facecolor='lightblue', alpha=0.3)
    
    # Add gridlines
    gl = ax.gridlines(draw_labels=True, linewidth=0.5, alpha=0.5, linestyle='--')
    gl.top_labels = False
    gl.right_labels = False
    
    # Scale marker sizes by magnitude (exponential scaling for better visibility)
    sizes = [50 * (2 ** mag) for mag in mags]
    
    # Create scatter plot
    scatter = ax.scatter(lons, lats, s=sizes, c=mags, cmap='YlOrRd', 
                        alpha=0.6, edgecolors='darkred', linewidth=0.5,
                        transform=ccrs.PlateCarree(), zorder=5)
    
    # Add colorbar
    cbar = plt.colorbar(scatter, ax=ax, orientation='vertical', pad=0.05, shrink=0.8)
    cbar.set_label('Magnitude', fontsize=12, fontweight='bold')
    
    # Add title
    title = f'Earthquake Locations - UK Region'
    if year:
        title += f' ({year})'
        ax.text(0.02, 0.98, f'Year: {year}\nCount: {len(filtered_quakes)}', 
                transform=ax.transAxes, fontsize=11, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    else:
        years = [get_year(eq) for eq in filtered_quakes]
        title += f' ({min(years)}-{max(years)})'
        ax.text(0.02, 0.98, f'Total: {len(filtered_quakes)} earthquakes', 
                transform=ax.transAxes, fontsize=11, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.title(title, fontsize=15, fontweight='bold', pad=20)
    
    # Add legend for sizes
    legend_sizes = [2.0, 3.0, 4.0, 5.0]
    legend_markers = []
    for size in legend_sizes:
        legend_markers.append(plt.scatter([], [], s=50 * (2 ** size), 
                                         c='red', alpha=0.6, edgecolors='darkred'))
    plt.legend(legend_markers, [f'M {s}' for s in legend_sizes], 
              scatterpoints=1, title='Magnitude', loc='upper right', 
              frameon=True, fancybox=True)
    
    # Save plot
    plt.tight_layout()
    plt.savefig(save_filename, dpi=300, bbox_inches='tight')
    print(f" Map saved: {save_filename}")
    plt.close()


def plot_earthquake_map_with_histograms(earthquakes, year=None, 
                                        bin_size=1.0, save_filename='earthquake_map_hist.png'):
    """
    Create a map with marginal histograms showing earthquake distribution.
    
    Parameters:
        earthquakes: List of earthquake records
        year: Optional year to filter data
        bin_size: Bin size for histograms in degrees
        save_filename: Filename to save the plot
    """
    # Filter by year if specified
    filtered_quakes = filter_by_year(earthquakes, year)
    
    if len(filtered_quakes) == 0:
        print(f"No earthquakes found for year {year}")
        return
    
    # Extract data
    lons = []
    lats = []
    mags = []
    
    for eq in filtered_quakes:
        lon, lat = get_location(eq)
        mag = get_magnitude(eq)
        if mag is not None:
            lons.append(lon)
            lats.append(lat)
            mags.append(mag)
    
    # Create figure with subplots
    fig = plt.figure(figsize=(14, 12))
    
    # Define grid
    gs = fig.add_gridspec(3, 3, width_ratios=[1, 4, 0.2], height_ratios=[1, 4, 0.2],
                         hspace=0.05, wspace=0.05)
    
    # Main map (center)
    ax_main = fig.add_subplot(gs[1, 1], projection=ccrs.PlateCarree())
    
    # Histograms
    ax_top = fig.add_subplot(gs[0, 1], sharex=ax_main)  # Top histogram (longitude)
    ax_right = fig.add_subplot(gs[1, 2], sharey=ax_main)  # Right histogram (latitude)
    
    # --- Main Map ---
    ax_main.set_extent([-10, 2, 49, 59], crs=ccrs.PlateCarree())
    ax_main.add_feature(cfeature.COASTLINE, linewidth=1.5)
    ax_main.add_feature(cfeature.BORDERS, linestyle=':', linewidth=1)
    ax_main.add_feature(cfeature.LAND, facecolor='lightgray', alpha=0.3)
    ax_main.add_feature(cfeature.OCEAN, facecolor='lightblue', alpha=0.3)
    
    gl = ax_main.gridlines(draw_labels=True, linewidth=0.5, alpha=0.5, linestyle='--')
    gl.top_labels = False
    gl.right_labels = False
    
    sizes = [50 * (2 ** mag) for mag in mags]
    scatter = ax_main.scatter(lons, lats, s=sizes, c=mags, cmap='YlOrRd', 
                             alpha=0.6, edgecolors='darkred', linewidth=0.5,
                             transform=ccrs.PlateCarree(), zorder=5)
    
    # --- Top Histogram (Longitude distribution) ---
    lon_bins = np.arange(-10, 2 + bin_size, bin_size)
    ax_top.hist(lons, bins=lon_bins, color='steelblue', alpha=0.7, edgecolor='navy')
    ax_top.set_ylabel('Count', fontsize=10)
    ax_top.tick_params(axis='x', labelbottom=False)
    ax_top.grid(axis='y', alpha=0.3)
    ax_top.set_title(f'Earthquake Distribution with Marginal Histograms', 
                    fontsize=14, fontweight='bold', pad=10)
    
    # --- Right Histogram (Latitude distribution) ---
    lat_bins = np.arange(49, 59 + bin_size, bin_size)
    ax_right.hist(lats, bins=lat_bins, orientation='horizontal', 
                 color='coral', alpha=0.7, edgecolor='darkred')
    ax_right.set_xlabel('Count', fontsize=10)
    ax_right.tick_params(axis='y', labelleft=False)
    ax_right.grid(axis='x', alpha=0.3)
    
    # Add info text
    info_text = f'Total: {len(filtered_quakes)} earthquakes\n'
    info_text += f'Bin size: {bin_size}°'
    if year:
        info_text = f'Year: {year}\n' + info_text
    
    ax_main.text(0.02, 0.98, info_text, transform=ax_main.transAxes, 
                fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Save plot
    plt.savefig(save_filename, dpi=300, bbox_inches='tight')
    print(f" Map with histograms saved: {save_filename}")
    plt.close()


def create_yearly_animation(earthquakes, save_filename='earthquake_animation.gif', 
                           fps=2):
    """
    Create an animation showing earthquakes year by year.
    
    Parameters:
        earthquakes: List of earthquake records
        save_filename: Filename to save the animation
        fps: Frames per second
    """
    # Get all years
    years = sorted(set(get_year(eq) for eq in earthquakes))
    
    print(f"\n Creating animation for years {years[0]}-{years[-1]}...")
    
    # Create figure
    fig = plt.figure(figsize=(14, 10))
    ax = plt.axes(projection=ccrs.PlateCarree())
    
    def animate(year_idx):
        """Animation function called for each frame."""
        ax.clear()
        year = years[year_idx]
        
        # Filter earthquakes for this year
        year_quakes = filter_by_year(earthquakes, year)
        
        # Extract data
        lons = []
        lats = []
        mags = []
        
        for eq in year_quakes:
            lon, lat = get_location(eq)
            mag = get_magnitude(eq)
            if mag is not None:
                lons.append(lon)
                lats.append(lat)
                mags.append(mag)
        
        # Setup map
        ax.set_extent([-10, 2, 49, 59], crs=ccrs.PlateCarree())
        ax.add_feature(cfeature.COASTLINE, linewidth=1.5)
        ax.add_feature(cfeature.BORDERS, linestyle=':', linewidth=1)
        ax.add_feature(cfeature.LAND, facecolor='lightgray', alpha=0.3)
        ax.add_feature(cfeature.OCEAN, facecolor='lightblue', alpha=0.3)
        
        gl = ax.gridlines(draw_labels=True, linewidth=0.5, alpha=0.5, linestyle='--')
        gl.top_labels = False
        gl.right_labels = False
        
        # Plot earthquakes
        if len(lons) > 0:
            sizes = [50 * (2 ** mag) for mag in mags]
            ax.scatter(lons, lats, s=sizes, c=mags, cmap='YlOrRd', 
                      alpha=0.6, edgecolors='darkred', linewidth=0.5,
                      transform=ccrs.PlateCarree(), zorder=5)
        
        # Add title and info
        ax.set_title(f'Earthquakes in UK Region - Year {year}', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.text(0.02, 0.98, f'Year: {year}\nCount: {len(year_quakes)}', 
               transform=ax.transAxes, fontsize=12, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
        
        print(f"  Frame {year_idx + 1}/{len(years)}: Year {year} ({len(year_quakes)} earthquakes)")
    
    # Create animation
    anim = animation.FuncAnimation(fig, animate, frames=len(years), 
                                  interval=1000/fps, repeat=True)
    
    # Save animation
    print(f" Saving animation...")
    anim.save(save_filename, writer='pillow', fps=fps, dpi=150)
    print(f" Animation saved: {save_filename}")
    plt.close()


def main():
    """Main function to generate all advanced visualizations."""
    print("=" * 70)
    print("Advanced Earthquake Visualization - UK Region")
    print("=" * 70)
    
    # Load data
    print("\n Fetching earthquake data...")
    data = earthquakes.get_data()
    quakes = data['features']
    print(f" Loaded {len(quakes)} earthquake records")
    
    # Get year range
    years = [get_year(eq) for eq in quakes]
    year_range = f"{min(years)}-{max(years)}"
    print(f" Year range: {year_range}")
    
    # 1. Create basic earthquake map (all years)
    print("\n" + "=" * 70)
    print("1  Creating basic earthquake map (all years)...")
    print("=" * 70)
    plot_earthquake_map(quakes, year=None, save_filename='earthquake_map_all.png')
    
    # 2. Create map for a specific year (e.g., 2008 - peak year)
    print("\n" + "=" * 70)
    print("  Creating earthquake map for year 2008...")
    print("=" * 70)
    plot_earthquake_map(quakes, year=2008, save_filename='earthquake_map_2008.png')
    
    # 3. Create map with histograms (all years)
    print("\n" + "=" * 70)
    print("  Creating map with marginal histograms...")
    print("=" * 70)
    plot_earthquake_map_with_histograms(quakes, year=None, bin_size=1.0,
                                       save_filename='earthquake_map_hist_all.png')
    
    # 4. Create map with histograms for specific year
    print("\n" + "=" * 70)
    print("  Creating map with histograms for year 2008...")
    print("=" * 70)
    plot_earthquake_map_with_histograms(quakes, year=2008, bin_size=1.0,
                                       save_filename='earthquake_map_hist_2008.png')
    
    # 5. Create animation
    print("\n" + "=" * 70)
    print("  Creating yearly animation...")
    print("=" * 70)
    create_yearly_animation(quakes, save_filename='earthquake_animation.gif', fps=2)
    
    # Summary
    print("\n" + "=" * 70)
    print(" All visualizations completed successfully!")
    print("=" * 70)
    print("\nGenerated files:")
    print("   earthquake_map_all.png - Map of all earthquakes")
    print("   earthquake_map_2008.png - Map for year 2008")
    print("   earthquake_map_hist_all.png - Map with histograms (all years)")
    print("   earthquake_map_hist_2008.png - Map with histograms (2008)")
    print("   earthquake_animation.gif - Yearly animation")
    print("\n Next: Review the plots and submit to GitHub!")


if __name__ == '__main__':
    main()
    