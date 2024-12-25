# Import necessary modules and utility functions
from config import Config
from util import (
    visualize_titles,  # Function to visualize paper titles
    process_titles,   # Function to process paper titles
    get_titles,       # Function to fetch paper titles
    save_data_as_json,  # Function to save data as JSON
    generate_markdown_from_json,  # Function to generate Markdown from JSON
    get_keywords,     # Function to fetch keywords
    process_keywords, # Function to process keywords
    visualize_keywords  # Function to visualize keywords
)

# Main entry point of the script
if __name__ == '__main__':
    # Define the conference and year
    conference = 'ICML'  # Name of the conference (e.g., NeurIPS)
    year = '2024'           # Year of the conference (e.g., 2024)

    # Define the path to save the data
    all_json_path = f'./data/{conference}/{year}/'  # Path to store JSON files

    # Define the levels of papers (e.g., Oral, Spotlight, Poster)
    levels = ['Oral', 'Spotlight', 'Poster']

    # Save the data as JSON files
    all_json = save_data_as_json(conference, year, levels, all_json_path)
    # Generate Markdown files from the JSON data
    generate_markdown_from_json(conference, year, levels, all_json_path)

    # Fetch and process keywords
    keywords = get_keywords(all_json_path, conference, year)  # Fetch keywords
    keywords = process_keywords(keywords)  # Process the fetched keywords
    visualize_keywords(keywords, 50, all_json_path)  # Visualize the top 50 keywords

    # Fetch and process paper titles
    titles = get_titles(all_json_path, conference, year)  # Fetch paper titles
    titles = process_titles(titles)  # Process the fetched titles
    visualize_titles(titles, 50, all_json_path)  # Visualize the top 50 titles