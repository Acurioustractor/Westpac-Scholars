#!/usr/bin/env python3
"""
Westpac Scholars Simple Data Analysis

This script analyzes the scraped scholar data and generates basic statistics and insights.
"""

import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("analysis.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants
# Updated paths to use parent directory for input
PARENT_DIR = os.path.dirname(os.getcwd())
INPUT_DIR = os.path.join(PARENT_DIR, "data")
OUTPUT_DIR = "analysis"
SCHOLARS_CSV = os.path.join(INPUT_DIR, "all_westpac_scholars.csv")
ANALYSIS_DIR = os.path.join(OUTPUT_DIR, "figures")

def load_data(filename):
    """Load scholar data from CSV file."""
    try:
        data = pd.read_csv(filename)
        logger.info(f"Loaded {len(data)} scholar records from {filename}")
        return data
    except Exception as e:
        logger.error(f"Error loading data from {filename}: {e}")
        return pd.DataFrame()

def ensure_output_dir(directory):
    """Ensure the output directory exists."""
    os.makedirs(directory, exist_ok=True)
    logger.info(f"Ensured output directory exists: {directory}")

def analyze_year_distribution(df):
    """
    Analyze the distribution of scholars by year.
    
    Args:
        df: DataFrame with scholar data
        
    Returns:
        DataFrame with year distribution
    """
    year_counts = df['year'].value_counts().sort_index()
    
    # Create plot
    plt.figure(figsize=(12, 6))
    ax = year_counts.plot(kind='bar', color='skyblue')
    
    plt.title('Number of Westpac Scholars by Year', fontsize=16)
    plt.xlabel('Year', fontsize=14)
    plt.ylabel('Number of Scholars', fontsize=14)
    plt.xticks(rotation=45)
    
    # Add count labels on top of bars
    for i, count in enumerate(year_counts):
        plt.text(i, count + 1, str(count), ha='center', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(ANALYSIS_DIR, 'scholars_by_year.png'))
    plt.close()
    
    logger.info(f"Analyzed distribution of scholars across {len(year_counts)} years")
    return year_counts

def analyze_scholarship_distribution(df):
    """
    Analyze the distribution of scholarship types.
    
    Args:
        df: DataFrame with scholar data
        
    Returns:
        DataFrame with scholarship type distribution
    """
    # Filter out rows with missing scholarship_type
    filtered_df = df[df['scholarship_type'].notna()]
    
    scholarship_counts = filtered_df['scholarship_type'].value_counts()
    
    # Create plot
    plt.figure(figsize=(14, 8))
    ax = scholarship_counts.plot(kind='bar', color='lightgreen')
    
    plt.title('Distribution of Westpac Scholarship Types', fontsize=16)
    plt.xlabel('Scholarship Type', fontsize=14)
    plt.ylabel('Number of Scholars', fontsize=14)
    plt.xticks(rotation=45, ha='right')
    
    # Add count labels on top of bars
    for i, count in enumerate(scholarship_counts):
        plt.text(i, count + 1, str(count), ha='center', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(ANALYSIS_DIR, 'scholarship_types.png'))
    plt.close()
    
    logger.info(f"Analyzed distribution of {len(scholarship_counts)} scholarship types")
    return scholarship_counts

def analyze_focus_area_distribution(df):
    """
    Analyze the distribution of focus areas.
    
    Args:
        df: DataFrame with scholar data
        
    Returns:
        DataFrame with focus area distribution
    """
    # Filter out rows with missing focus_area
    filtered_df = df[df['focus_area'].notna()]
    
    focus_area_counts = filtered_df['focus_area'].value_counts()
    
    # Create plot
    plt.figure(figsize=(14, 8))
    ax = focus_area_counts.plot(kind='bar', color='salmon')
    
    plt.title('Distribution of Westpac Scholar Focus Areas', fontsize=16)
    plt.xlabel('Focus Area', fontsize=14)
    plt.ylabel('Number of Scholars', fontsize=14)
    plt.xticks(rotation=45, ha='right')
    
    # Add count labels on top of bars
    for i, count in enumerate(focus_area_counts):
        plt.text(i, count + 1, str(count), ha='center', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(ANALYSIS_DIR, 'focus_areas.png'))
    plt.close()
    
    logger.info(f"Analyzed distribution of {len(focus_area_counts)} focus areas")
    return focus_area_counts

def analyze_university_distribution(df):
    """
    Analyze the distribution of universities.
    
    Args:
        df: DataFrame with scholar data
        
    Returns:
        DataFrame with university distribution
    """
    # Filter out rows with missing university
    filtered_df = df[df['university'].notna()]
    
    # Get top 15 universities
    university_counts = filtered_df['university'].value_counts().head(15)
    
    # Create plot
    plt.figure(figsize=(14, 8))
    ax = university_counts.plot(kind='bar', color='lightblue')
    
    plt.title('Top 15 Universities of Westpac Scholars', fontsize=16)
    plt.xlabel('University', fontsize=14)
    plt.ylabel('Number of Scholars', fontsize=14)
    plt.xticks(rotation=45, ha='right')
    
    # Add count labels on top of bars
    for i, count in enumerate(university_counts):
        plt.text(i, count + 1, str(count), ha='center', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(ANALYSIS_DIR, 'top_universities.png'))
    plt.close()
    
    logger.info(f"Analyzed distribution of top {len(university_counts)} universities")
    return university_counts

def create_trend_analysis(df):
    """
    Create trend analysis of scholars over time by scholarship type.
    
    Args:
        df: DataFrame with scholar data
    """
    # Filter out rows with missing scholarship_type
    filtered_df = df[df['scholarship_type'].notna()]
    
    # Create pivot table: years as index, scholarship types as columns
    pivot_df = pd.pivot_table(
        filtered_df, 
        values='id',
        index='year', 
        columns='scholarship_type', 
        aggfunc='count',
        fill_value=0
    )
    
    # Plot
    plt.figure(figsize=(16, 10))
    pivot_df.plot(kind='line', marker='o', linewidth=3, markersize=8)
    
    plt.title('Westpac Scholarship Trends Over Time', fontsize=16)
    plt.xlabel('Year', fontsize=14)
    plt.ylabel('Number of Scholars', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(title='Scholarship Type', fontsize=12, title_fontsize=14)
    
    plt.tight_layout()
    plt.savefig(os.path.join(ANALYSIS_DIR, 'scholarship_trends.png'))
    plt.close()
    
    logger.info("Created scholarship trend analysis")
    return pivot_df

def create_state_distribution(df):
    """
    Create distribution analysis of scholars by state.
    
    Args:
        df: DataFrame with scholar data
    """
    # Filter out rows with missing state
    filtered_df = df[df['state'].notna()]
    
    state_counts = filtered_df['state'].value_counts()
    
    # Create plot
    plt.figure(figsize=(12, 8))
    ax = state_counts.plot(kind='bar', color='purple', alpha=0.7)
    
    plt.title('Distribution of Westpac Scholars by State/Territory', fontsize=16)
    plt.xlabel('State/Territory', fontsize=14)
    plt.ylabel('Number of Scholars', fontsize=14)
    plt.xticks(rotation=45, ha='right')
    
    # Add count labels on top of bars
    for i, count in enumerate(state_counts):
        plt.text(i, count + 1, str(count), ha='center', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(ANALYSIS_DIR, 'scholars_by_state.png'))
    plt.close()
    
    logger.info("Created state distribution analysis")
    return state_counts

def save_summary_stats(df, output_file):
    """
    Save summary statistics to a text file.
    
    Args:
        df: DataFrame with scholar data
        output_file: Path to output file
    """
    with open(output_file, 'w') as f:
        f.write("Westpac Scholars Analysis Summary\n")
        f.write("================================\n\n")
        
        f.write(f"Total number of scholars: {len(df)}\n\n")
        
        f.write("Scholars by Year:\n")
        year_counts = df['year'].value_counts().sort_index()
        for year, count in year_counts.items():
            f.write(f"  {year}: {count} scholars\n")
        f.write("\n")
        
        f.write("Scholarship Types:\n")
        scholarship_counts = df['scholarship_type'].value_counts()
        for scholarship, count in scholarship_counts.items():
            f.write(f"  {scholarship}: {count} scholars\n")
        f.write("\n")
        
        f.write("Focus Areas:\n")
        focus_area_counts = df['focus_area'].value_counts()
        for focus_area, count in focus_area_counts.items():
            f.write(f"  {focus_area}: {count} scholars\n")
        f.write("\n")
        
        f.write("Top 10 Universities:\n")
        university_counts = df['university'].value_counts().head(10)
        for university, count in university_counts.items():
            if isinstance(university, str):
                f.write(f"  {university}: {count} scholars\n")
        f.write("\n")
        
        f.write("Scholars by State/Territory:\n")
        state_counts = df['state'].value_counts()
        for state, count in state_counts.items():
            if isinstance(state, str):
                f.write(f"  {state}: {count} scholars\n")
    
    logger.info(f"Saved summary statistics to {output_file}")

def main():
    """Main function to run the analysis."""
    # Ensure output directories exist
    ensure_output_dir(OUTPUT_DIR)
    ensure_output_dir(ANALYSIS_DIR)
    
    # Load scholar data
    df = load_data(SCHOLARS_CSV)
    
    if df.empty:
        logger.error("No data loaded. Analysis cannot continue.")
        return
    
    # Run analyses and create visualizations
    analyze_year_distribution(df)
    analyze_scholarship_distribution(df)
    analyze_focus_area_distribution(df)
    analyze_university_distribution(df)
    create_trend_analysis(df)
    create_state_distribution(df)
    
    # Save summary statistics
    save_summary_stats(df, os.path.join(OUTPUT_DIR, 'summary_statistics.txt'))
    
    logger.info("Analysis completed successfully")

if __name__ == "__main__":
    main() 