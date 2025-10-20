"""
Earthquake Data Analysis and Visualization
Program to plot earthquake data following the course template
"""

from datetime import date
import matplotlib.pyplot as plt
import numpy as np


def get_data():
    """Retrieve the data we will be working with."""
    # Import earthquakes module to get data
    import earthquakes
    return earthquakes.get_data()


def get_year(earthquake):
    """Extract the year in which an earthquake happened."""
    timestamp = earthquake['properties']['time']
    # The time is given in a strange-looking but commonly-used format.
    # To understand it, we can look at the documentation of the source data:
    # https://earthquake.usgs.gov/data/comcat/index.php#time
    # Fortunately, Python provides a way of interpreting this timestamp:
    # (Question for discussion: Why do we divide by 1000?)
    # Answer: USGS API returns timestamps in milliseconds, but Python's fromtimestamp() expects seconds
    year = date.fromtimestamp(timestamp/1000).year
    return year


def get_magnitude(earthquake):
    """Retrive the magnitude of an earthquake item."""
    # Magnitude is stored in the 'mag' field under 'properties'
    return earthquake['properties']['mag']


# This is function you may want to create to break down the computations,
# although it is not necessary. You may also change it to something different.
def get_magnitudes_per_year(earthquakes):
    """Retrieve the magnitudes of all the earthquakes in a given year.
    
    Returns a dictionary with years as keys, and lists of magnitudes as values.
    """
    magnitudes_per_year = {}
    
    for earthquake in earthquakes:
        year = get_year(earthquake)
        magnitude = get_magnitude(earthquake)
        
        # If this year hasn't been recorded yet, create an empty list
        if year not in magnitudes_per_year:
            magnitudes_per_year[year] = []
        
        # Add magnitude to the corresponding year's list
        if magnitude is not None:  # Ensure magnitude is not None
            magnitudes_per_year[year].append(magnitude)
    
    return magnitudes_per_year


def plot_average_magnitude_per_year(earthquakes):
    """Plot the average earthquake magnitude per year."""
    # Get magnitude data for each year
    magnitudes_per_year = get_magnitudes_per_year(earthquakes)
    
    # Calculate average magnitude for each year
    years = sorted(magnitudes_per_year.keys())
    average_magnitudes = [np.mean(magnitudes_per_year[year]) for year in years]
    
    # Create line plot
    plt.figure(figsize=(12, 6))
    plt.plot(years, average_magnitudes, marker='o', linestyle='-', 
             color='crimson', linewidth=2, markersize=6,
             markerfacecolor='orange', markeredgecolor='darkred', markeredgewidth=1.5)
    
    # Add overall average line
    overall_avg = np.mean(average_magnitudes)
    plt.axhline(y=overall_avg, color='green', linestyle='--', 
                linewidth=1.5, alpha=0.7, 
                label=f'Overall Average: {overall_avg:.2f}')
    
    # Set labels and title
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Average Magnitude', fontsize=12)
    plt.title('Average Earthquake Magnitude per Year (UK Region, 2000-2018)', 
              fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.legend()
    
    # Ensure x-axis shows integers
    plt.gca().xaxis.set_major_locator(plt.MaxNLocator(integer=True))
    
    # Save the plot
    plt.tight_layout()
    plt.savefig('earthquake_avg_magnitude.png', dpi=300, bbox_inches='tight')
    print("✅ Average magnitude plot saved: earthquake_avg_magnitude.png")


def plot_number_per_year(earthquakes):
    """Plot the number of earthquakes per year."""
    # Count earthquakes per year
    year_counts = {}
    
    for earthquake in earthquakes:
        year = get_year(earthquake)
        if year not in year_counts:
            year_counts[year] = 0
        year_counts[year] += 1
    
    # Sort and prepare data for plotting
    years = sorted(year_counts.keys())
    counts = [year_counts[year] for year in years]
    
    # Create bar plot
    plt.figure(figsize=(12, 6))
    bars = plt.bar(years, counts, color='steelblue', alpha=0.7, edgecolor='navy')
    
    # Add count labels on top of bars
    for bar, count in zip(bars, counts):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(count)}',
                ha='center', va='bottom', fontsize=9)
    
    # Set labels and title
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Number of Earthquakes', fontsize=12)
    plt.title('Earthquake Frequency per Year (UK Region, 2000-2018)', 
              fontsize=14, fontweight='bold')
    plt.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Ensure x-axis shows integers
    plt.gca().xaxis.set_major_locator(plt.MaxNLocator(integer=True))
    
    # Save the plot
    plt.tight_layout()
    plt.savefig('earthquake_frequency.png', dpi=300, bbox_inches='tight')
    print("✅ Frequency plot saved: earthquake_frequency.png")


# ============================================================
# Main Program
# ============================================================

if __name__ == '__main__':
    print("=" * 60)
    print("Earthquake Data Analysis - UK Region (2000-2018)")
    print("=" * 60)
    
    # Get the data we will work with
    print("\n📡 Fetching data...")
    data = get_data()
    quakes = data['features']
    print(f"✅ Successfully loaded {len(quakes)} earthquake records")
    
    # Display basic statistics
    print("\n📊 Data Statistics:")
    years_set = set(get_year(q) for q in quakes)
    print(f"   Year range: {min(years_set)} - {max(years_set)}")
    print(f"   Total years: {len(years_set)} years")
    
    magnitudes = [get_magnitude(q) for q in quakes if get_magnitude(q) is not None]
    print(f"   Magnitude range: {min(magnitudes):.2f} - {max(magnitudes):.2f}")
    print(f"   Average magnitude: {np.mean(magnitudes):.2f}")
    
    # Plot the results - this is not perfect since the x axis is shown as real
    # numbers rather than integers, which is what we would prefer!
    print("\n🎨 Generating plots...")
    print("   Creating frequency plot...")
    plot_number_per_year(quakes)
    
    plt.clf()  # This clears the figure, so that we don't overlay the two plots
    
    print("   Creating average magnitude plot...")
    plot_average_magnitude_per_year(quakes)
    
    print("\n" + "=" * 60)
    print("✅ All plots generated successfully!")
    print("=" * 60)
    print("\nGenerated files:")
    print("  📈 earthquake_frequency.png - Earthquake frequency per year")
    print("  📉 earthquake_avg_magnitude.png - Average magnitude per year")
    print("\nPlease check the plots and submit to GitHub!")