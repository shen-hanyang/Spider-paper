import re
import os
import csv
import time
import json
import random
import requests

def crawl_meta(config, max_retries=5):
    """
    Function to crawl metadata from a URL with retry logic and pagination support.
    
    Args:
    - config: Configuration object containing URL, timeout, start/stop times, and save path.
    - max_retries (int): Maximum number of retry attempts in case of a request failure.
    """
    retry_count = 0  # Track the current retry attempt count

    while retry_count <= max_retries:
        try:
            # Wait for a random delay between requests to avoid server overload
            time.sleep(random.randint(config.start_time, config.stop_time))
            
            # Send the initial GET request and parse the JSON response
            res = requests.get(url=config.url, timeout=config.timeout).json()
            count = res['count']  # Total number of items to process
            
            # Prepare the final result dictionary with initial data
            final_result = {
                'notes': res['notes'],  # First batch of data
                'count': res['count']
            }
            
            # Handle pagination if the count exceeds the batch size (1000)
            while count > 1000:
                count -= 1000  # Reduce count by 1000 for each batch
                # Update the URL to reflect the offset and limit
                config.url = re.sub(r'offset=\d+', 'offset=1000', config.url)
                
                if count > 1000:
                    # If more than 1000 items are still remaining, set limit to 1000
                    config.url = re.sub(r'limit=\d+', f'limit=1000', config.url)
                else:
                    # For the last batch, set limit to the remaining count
                    config.url = re.sub(r'limit=\d+', f'limit={count}', config.url)
                
                # Send the next request and update the final result
                time.sleep(random.randint(config.start_time, config.stop_time))  # Delay between requests
                res = requests.get(url=config.url, timeout=config.timeout).json()
                
                # Append the notes from the current batch to the final result
                final_result['notes'].extend(res['notes'])

            # Save the final aggregated data to a JSON file
            with open(config.save_json, "w", encoding="utf-8") as json_file:
                json.dump(final_result, json_file, ensure_ascii=False, indent=4)
            
            print("Data has been saved.")  # Notify success
            break  # Exit retry loop after successful execution

        except requests.exceptions.RequestException as e:
            # Handle request exceptions (e.g., timeout, connection errors)
            retry_count += 1
            print(f"Attempt {retry_count}/{max_retries} failed. Error: {e}")
            
            # Introduce a delay before retrying (simple backoff strategy)
            time.sleep(random.randint(config.start_time, config.stop_time))
    
    # If the retry limit is exceeded, notify the user
    if retry_count > max_retries:
        print("Max retries reached. Exiting.")

def crawl_json(config):
    """
    Function to process a JSON file containing notes and extract relevant information into a structured format.
    
    Args:
    - config: Configuration object with paths and settings for loading and saving data.
    """
    # Load the JSON file
    try:
        with open(config.save_json, 'r', encoding='utf-8') as file:
            res = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        # Handle file not found or invalid JSON format
        print(f"Error loading JSON file: {e}")
        return
    
    # Extract notes from the JSON
    notes = res.get('notes', [])
    print(f"Total notes to process: {len(notes)}")
    
    # Initialize data structure to store extracted information
    data = {
        "titles": [],
        "authors": [],
        "keywords": [],
        "abstracts": [],
        "pdfs": [],
        "urls": [],
        "ids": [],
        "ratings": [],
        "confidences": []
    }

    # Iterate through each note and extract required fields
    for idx, note in enumerate(notes):
        print(f"Processing note {idx + 1} of {len(notes)}...")
        content = note.get('content', {})  # Get the content dictionary
        
        # Try to extract information from the content
        try:
            title = content['title']['value']           # Extract title
            author = content['authors']['value']        # Extract authors
            keyword = content['keywords']['value']      # Extract keywords
            abstract = content['abstract']['value']     # Extract abstract
            pdf = 'https://openreview.net/' + content['pdf']['value']  # Build PDF link
            id = note['id']                              # Extract note ID
            url = f'https://openreview.net/forum?id={id}'  # Build URL for the note
        except KeyError as e:
            # Handle missing keys in the content
            print(f"Missing key in note {idx + 1}: {e}")
            continue
        
        # Get the rating and confidence for the current note
        rating, confidence = crawl_rate_conf(id, config)
        
        # Append the extracted data to respective lists
        data["titles"].append(title)
        data["authors"].append(author)
        data["keywords"].append(keyword)
        data["abstracts"].append(abstract)
        data["pdfs"].append(pdf)
        data["urls"].append(url)
        data["ids"].append(id)
        data["ratings"].append(rating)
        data["confidences"].append(confidence)

    # Write the extracted data to a CSV file
    try:
        with open(config.save_informations, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Write header row
            writer.writerow(["Title", "Authors", "Keywords", "Abstract", "PDF", "URL", "ID", "Ratings", "Confidences"])
            
            # Write each row of data
            for i in range(len(data["titles"])):
                writer.writerow([
                    data["titles"][i],
                    data["authors"][i],
                    data["keywords"][i],
                    data["abstracts"][i],
                    data["pdfs"][i],
                    data["urls"][i],
                    data["ids"][i],
                    data["ratings"][i],
                    data["confidences"][i]
                ])
        print("Data successfully saved to CSV.")  # Notify success
    except IOError as e:
        # Handle errors during file write
        print(f"Error writing to CSV: {e}")

def crawl_rate_conf(id, config, max_retries=5):
    """
    Function to fetch ratings and confidence scores for a given paper (note) from the OpenReview API.
    
    Args:
    - id (str): The unique identifier of the paper (note).
    - config: Configuration object containing settings like conference, year, timeouts, etc.
    - max_retries (int): Maximum number of retry attempts in case of a request failure.
    
    Returns:
    - ratings (list): A list of rating values for the paper.
    - confidences (list): A list of confidence values for the ratings.
    """
    ratings = []  # List to store extracted ratings
    confidences = []  # List to store extracted confidence scores
    
    # Construct the API endpoint URL
    url = (
        f"https://api2.openreview.net/notes?details=writable%2Csignatures%2Cinvitation%2Cpresentation%2Ctags"
        f"&domain={config.conference}.cc%2F{config.year}%2FConference&forum={id}&limit=1000&trash=true"
    )
    print(f"Fetching ratings and confidences from URL: {url}")
    
    try:
        # Retry logic for fetching data
        for attempt in range(max_retries):  # Retry up to `max_retries` times
            try:
                # Introduce a random delay between requests to avoid overloading the server
                time.sleep(random.randint(config.start_time, config.stop_time))
                
                # Send a GET request to the API
                res = requests.get(url, timeout=config.timeout)
                res.raise_for_status()  # Raise an exception for HTTP error responses
                
                # Parse the JSON response to extract notes
                notes = json.loads(res.text)['notes']
                
                # Process each sub-note to extract ratings and confidences
                for idx, note in enumerate(notes):
                    print(f"Processing sub-note {idx + 1} of {len(notes)}...")
                    content = note.get('content', {})  # Get the content dictionary
                    if "rating" in content:
                        # Append rating and confidence values to the respective lists
                        ratings.append(content['rating']['value'])
                        confidences.append(content['confidence']['value'])
                
                # Exit retry loop after successful execution
                break
            except requests.exceptions.RequestException as e:
                # Log request exceptions (e.g., connection errors, timeouts)
                print(f"Attempt {attempt + 1} failed. Error: {e}")
                # Introduce a delay before retrying
                time.sleep(random.randint(config.start_time, config.stop_time))
        else:
            # Log failure if all retry attempts are exhausted
            print("Failed to fetch ratings and confidences after 3 attempts.")
    except json.JSONDecodeError as e:
        # Log JSON decoding errors
        print(f"Error decoding JSON response: {e}")
    
    # Return the extracted ratings and confidences
    return ratings, confidences

def get_keywords(json_path, conference, year):
    """
    Extract all keywords from a JSON file.

    Args:
        json_path (str): Path to the JSON file containing paper data.

    Returns:
        list: A list of all keywords extracted from the JSON file.
    """
    json_path = json_path + conference + '-' + year + '.json'
    if not os.path.isfile(json_path):
        print(f"No JSON data found. Please save the data first.")
        return []

    with open(json_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    keywords = []
    for paper in data:
        if 'keywords' in paper:
            keywords.extend(paper['keywords'])

    return keywords

def process_keywords(all_keywords):
    """
    Process a list of keyword strings, splitting them into individual keywords, counting their occurrences,
    merging plural and -ing duplicates, and standardizing their format.

    Args:
        all_keywords (list of str): List of keyword strings, where each string may contain multiple keywords separated by ', '.

    Returns:
        dict: A dictionary with standardized keywords as keys and their counts as values, after merging duplicates.
    """
    import re
    from collections import Counter

    # Define stop words to be removed
    stop_words = {"and", "or", "of", "the", "in", "on", "for", "with", "by", "at", "a", "an", "to", ""}
    
    # Split keywords and clean up
    keywords = []
    for i, keyword in enumerate(all_keywords):
        # Split by comma and strip any extra spaces or symbols
        for k in keyword.split(', '):
            cleaned_keyword = re.sub(r'[^a-zA-Z0-9\s-]', '', k.strip())  # Remove special characters
            if cleaned_keyword.lower() not in stop_words:
                keywords.append(cleaned_keyword.lower())  # Convert to lowercase for consistent processing

    # Count occurrences of keywords
    keywords_hist = Counter(keywords)

    # Remove empty entries
    if '' in keywords_hist:
        del keywords_hist['']
    print(f"{len(keywords_hist)} different keywords before merging")

    # Merge plural duplicates (e.g., 'model' and 'models')
    duplicates = []
    for k in list(keywords_hist.keys()):
        if k.endswith('s') and k[:-1] in keywords_hist:
            duplicates.append(k[:-1])
            keywords_hist[k[:-1]] += keywords_hist[k]
            del keywords_hist[k]

    # Merge -ing and non-ing duplicates (e.g., 'learn' and 'learning')
    ing_duplicates = []
    for k in list(keywords_hist.keys()):
        if k.endswith('ing') and k[:-3] in keywords_hist:
            ing_duplicates.append(k[:-3])
            keywords_hist[k[:-3]] += keywords_hist[k]
            del keywords_hist[k]

    # Standardize format: Capitalize the first letter of each word
    formatted_keywords = Counter()
    for k, v in keywords_hist.items():
        formatted_key = ' '.join([word.capitalize() for word in k.split()])  # Capitalize each word
        formatted_keywords[formatted_key] = v

    print(f"{len(formatted_keywords)} different keywords after merging")
    return formatted_keywords

def visualize_keywords(keywords_hist, num_keyword, path):
    """
    Visualize the top N most common keywords and their frequencies using a horizontal bar chart.

    Args:
        keywords_hist (Counter): A dictionary-like object with keywords as keys and their frequencies as values.
        num_keyword (int): Number of top keywords to visualize.
        path (str): Directory path to save the generated chart image.
    """
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib import cm

    # Get the top N keywords
    keywords_hist_vis = keywords_hist.most_common(num_keyword)

    # Set up the plot
    plt.rcdefaults()
    fig, ax = plt.subplots(figsize=(10, 14), dpi=300)

    # Prepare data for the chart
    key = [k[0] for k in keywords_hist_vis]
    value = [k[1] for k in keywords_hist_vis]
    y_pos = np.arange(len(key)) 

    # Use a colormap for gradient colors
    colors = cm.magma(np.linspace(0.3, 0.7, len(key)))

    # Draw horizontal bar chart
    bars = ax.barh(y_pos, value, align='center', color=colors, ecolor='black', log=True)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(key, rotation=0, fontsize=5)
    ax.invert_yaxis()  # Reverse Y-axis

    # Add text labels to each bar
    for i, (bar, v) in enumerate(zip(bars, value)):
        ax.text(bar.get_width() + 0.2, i, str(v), color='black', ha='left', va='center', fontsize=5)

    # Add title and labels
    ax.set_xlabel('Frequency', fontsize=6)
    ax.set_title(f'Top {num_keyword} Keywords', fontsize=10)

    # Adjust layout to fit everything properly
    plt.subplots_adjust(left=0.18, right=0.95, top=0.95, bottom=0.05)

    # Show and save the plot
    plt.show()
    
    if not os.path.exists(f'{path}/assets'):
        os.makedirs(f'{path}/assets')
        
    fig.savefig(f'{path}/assets/keyword_frequency.png', dpi=300, bbox_inches='tight')

def get_titles(json_path, conference, year):
    """
    Extract all titles from a JSON file.

    Args:
        json_path (str): Path to the directory containing the JSON file with paper data.
        conference (str): Name of the conference.
        year (str): Year of the conference.

    Returns:
        list: A list of all titles extracted from the JSON file.
    """
    # Construct the full path to the JSON file
    json_file_path = os.path.join(json_path, f"{conference}-{year}.json")
    
    if not os.path.isfile(json_file_path):
        print(f"No JSON data found at {json_file_path}. Please save the data first.")
        return []

    # Open and load the JSON file
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Extract titles
    titles = []
    for paper in data:
        if 'title' in paper:
            titles.append(paper['title'])

    return titles

def process_titles(all_titles):
    """
    Process a list of titles, tokenize them into individual words, 
    remove stop words, handle stemming (e.g., 'ing' forms), and normalize casing.

    Args:
        all_titles (list of str): List of paper titles.

    Returns:
        dict: A dictionary with processed words as keys and their counts as values.
    """
    from collections import Counter
    import re
    from nltk.corpus import stopwords

    # Load English stop words
    stop_words = set(stopwords.words('english'))

    # Initialize word count dictionary
    word_counts = Counter()

    for title in all_titles:
        # Tokenize the title (split into words)
        words = re.findall(r'\b\w+\b', title.lower())

        for word in words:
            # Skip stop words
            if word in stop_words:
                continue
            # Add word to the counter
            word_counts[word] += 1

    # Merge singular/plural and 'ing' variations
    merged_counts = Counter()
    for word, count in word_counts.items():
        # Normalize 'ing' forms
        if word.endswith('ing') and word[:-3] in word_counts:
            merged_counts[word[:-3]] += count
        # Normalize plural forms
        elif word.endswith('s') and word[:-1] in word_counts:
            merged_counts[word[:-1]] += count
        else:
            merged_counts[word] += count

    # Normalize casing (capitalize first letter of each word)
    final_counts = {word.capitalize(): count for word, count in merged_counts.items()}

    print(f"{len(final_counts)} unique words after processing")
    return final_counts

def visualize_titles(titles_hist, num_title, path):
    """
    Visualize the top N most common words in titles and their frequencies using a horizontal bar chart.

    Args:
        titles_hist (Counter): A dictionary-like object with title words as keys and their frequencies as values.
        num_title (int): Number of top title words to visualize.
        path (str): Directory path to save the generated chart image.
    """
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib import cm
    from collections import Counter
    
    titles_hist = Counter(titles_hist)
    # Get the top N title words
    titles_hist_vis = titles_hist.most_common(num_title)

    # Set up the plot
    plt.rcdefaults()
    fig, ax = plt.subplots(figsize=(10, 14), dpi=300)

    # Prepare data for the chart
    key = [k[0] for k in titles_hist_vis]
    value = [k[1] for k in titles_hist_vis]
    y_pos = np.arange(len(key))

    # Use a colormap for gradient colors
    colors = cm.viridis(np.linspace(0.2, 0.8, len(key)))

    # Draw horizontal bar chart
    bars = ax.barh(y_pos, value, align='center', color=colors, ecolor='black', log=True)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(key, rotation=0, fontsize=5)
    ax.invert_yaxis()  # Reverse Y-axis

    # Add text labels to each bar
    for i, (bar, v) in enumerate(zip(bars, value)):
        ax.text(bar.get_width() + 0.2, i, str(v), color='black', ha='left', va='center', fontsize=5)

    # Add title and labels
    ax.set_xlabel('Frequency', fontsize=8)
    ax.set_title(f'Top {num_title} Words in Titles', fontsize=10)

    # Adjust layout to fit everything properly
    plt.subplots_adjust(left=0.15, right=0.99, top=0.95, bottom=0.05)

    # Show and save the plot
    plt.show()

    if not os.path.exists(f'{path}/assets'):
        os.makedirs(f'{path}/assets')

    fig.savefig(f'{path}/assets/title_frequency.png', dpi=300, bbox_inches='tight')

def process_and_visualize_title_keywords(all_titles, num_keyword, path):
    """
    Extract keywords from titles, filter out common stopwords, and visualize the most common keywords.

    Args:
        all_titles (list of str): List of paper titles.
        num_keyword (int): Number of top keywords to visualize.
        path (str): Directory path to save the generated chart image.

    Returns:
        Counter: A Counter object containing keywords and their frequencies.
    """
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib import cm
    from collections import Counter

    # Define stopwords
    stop_words = {'of', 'for', 'and', 'the', 'a', 'to', 'in', 'on', 'at', 'by', 'with', 'as', 'from', 'is'}
    
    # Extract and filter keywords
    title_words = []
    for title in all_titles:
        words = title.split(' ')
        filtered_words = [word for word in words if word.lower() not in stop_words]
        title_words.extend(filtered_words)
    
    # Count keyword frequencies
    keywords_hist = Counter(title_words)
    
    # Visualize the top N keywords
    keywords_hist_vis = keywords_hist.most_common(num_keyword)
    plt.rcdefaults()
    fig, ax = plt.subplots(figsize=(8, 12), dpi=300)

    # Prepare data for visualization
    key = [k[0] for k in keywords_hist_vis]
    value = [k[1] for k in keywords_hist_vis]
    y_pos = np.arange(len(key))

    # Use a colormap for gradient colors
    colors = cm.plasma(np.linspace(0.2, 0.8, len(key)))

    # Draw horizontal bar chart
    bars = ax.barh(y_pos, value, align='center', color=colors, ecolor='black', log=True)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(key, rotation=0, fontsize=10)
    ax.invert_yaxis()  # Reverse Y-axis

    # Add text labels to each bar
    for i, (bar, v) in enumerate(zip(bars, value)):
        ax.text(bar.get_width() + 0.2, i, str(v), color='black', ha='left', va='center', fontsize=9)

    # Add title and labels
    ax.set_xlabel('Frequency', fontsize=12)
    ax.set_title(f'Top {num_keyword} Keywords from Titles', fontsize=14)

    # Adjust layout to fit everything properly
    plt.tight_layout()
    plt.subplots_adjust(left=0.3, right=0.95, top=0.95, bottom=0.05)

    # Show and save the plot
    plt.show()
    fig.savefig(f'{path}/assets/titles_frequency.png', dpi=300, bbox_inches='tight')

    return keywords_hist

def generate_markdown_and_json(conference, year, levels, output_path):
    """
    Generate a Markdown file summarizing accepted papers and save all data in a JSON file.

    Args:
        conference (str): Conference name.
        year (str): Year of the conference.
        levels (list of str): List of paper presentation levels (e.g., Oral, Spotlight, Poster).
        output_path (str): Directory to save the output Markdown and JSON files.

    Returns:
        dict: A dictionary containing all the extracted paper data.
    """
    import os
    import json

    md_path = os.path.join(output_path, f"{conference}-{year}.md")
    all_data = []

    # Open the Markdown file for writing
    with open(md_path, 'w', encoding='utf-8') as md_file:

        md_file.write(f"# {conference} {year} Accepted Papers\n\n")

        for level in levels:
            json_path = os.path.join(output_path, level, f"{level}.json")
            if not os.path.isfile(json_path):
                continue

            # Open and read the JSON file
            with open(json_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

                if 'notes' in data:
                    venue_written = False
                    for idx, note in enumerate(data['notes']):
                        paper_data = {}
                        content = note['content']
                        # 只写入一次 Venue Year Level 标题
                        if len(levels) >= 2 and not venue_written:
                            md_file.write(f"## {level} Accepted paper\n")
                            venue_written = True
                        
                        # Process 'title'
                        if 'title' in content:
                            title = content['title'].get('value', content['title'])
                            paper_data['title'] = title
                            md_file.write(f"### {idx + 1}. {title}\n")

                        # Process 'keywords'
                        if 'keywords' in content:
                            keywords = content['keywords'].get('value', content['keywords'])
                            paper_data['keywords'] = keywords
                            keywords_str = ', '.join(keywords)
                            md_file.write(f"- **Keywords**: {keywords_str}\n")

                        # Process 'authors'
                        if 'authors' in content:
                            authors = content['authors'].get('value', content['authors'])
                            paper_data['authors'] = authors
                            authors_str = ', '.join(authors)
                            md_file.write(f"- **Authors**: {authors_str}\n")

                        # Process 'pdf'
                        if 'pdf' in content:
                            pdf = 'https://openreview.net' + content['pdf'].get('value', content['pdf'])
                            paper_data['pdf'] = pdf
                            md_file.write(f"- **PDF**: [{title}]({pdf})\n")

                        # Add paper data to the list
                        all_data.append(paper_data)

                        # Add a blank line as a separator
                        md_file.write("\n")

    # Save all data to a JSON file
    json_path = os.path.join(output_path, f"{conference}-{year}.json")
    with open(json_path, 'w', encoding='utf-8') as json_file:
        json.dump(all_data, json_file, indent=4, ensure_ascii=False)

    print(f"Markdown and JSON files have been saved to {output_path}")
    return all_data

def save_data_as_json(conference, year, levels, output_path):
    """
    Save paper data to a JSON file.
    
    Args:
        conference (str): Conference name.
        year (str): Year of the conference.
        levels (list of str): List of paper presentation levels (e.g., Oral, Spotlight, Poster).
        output_path (str): Directory to save the output JSON file.
        
    Returns:
        dict: A dictionary containing all the extracted paper data.
    """
    all_data = []

    for level in levels:
        json_path = os.path.join(output_path, level, f"{level}.json")
        if not os.path.isfile(json_path):
            continue

        # Open and read the JSON file
        with open(json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

            if 'notes' in data:
                for idx, note in enumerate(data['notes']):
                    paper_data = {}
                    content = note['content']

                    # Process paper data
                    if 'title' in content:
                        title = content['title'].get('value', content['title'])
                        paper_data['title'] = title

                    if 'keywords' in content:
                        keywords = content['keywords'].get('value', content['keywords'])
                        paper_data['keywords'] = keywords

                    if 'authors' in content:
                        authors = content['authors'].get('value', content['authors'])
                        paper_data['authors'] = authors

                    if 'pdf' in content:
                        pdf = 'https://openreview.net' + content['pdf'].get('value', content['pdf'])
                        paper_data['pdf'] = pdf

                    # Add level information
                    paper_data['level'] = level
                    
                    # Add paper data to the list
                    all_data.append(paper_data)

    # Save all data to a JSON file
    json_output_path = os.path.join(output_path, f"{conference}-{year}.json")
    with open(json_output_path, 'w', encoding='utf-8') as json_file:
        json.dump(all_data, json_file, indent=4, ensure_ascii=False)

    print(f"JSON file has been saved to {json_output_path}")
    return all_data

def generate_markdown_from_json(conference, year, levels, output_path):
    """
    Generate a Markdown file from saved JSON data, considering different presentation levels.

    Args:
        conference (str): Conference name.
        year (str): Year of the conference.
        levels (list of str): List of paper presentation levels (e.g., Oral, Spotlight, Poster).
        output_path (str): Directory to save the output Markdown file.

    Returns:
        None
    """
    json_path = os.path.join(output_path, f"{conference}-{year}.json")
    if not os.path.isfile(json_path):
        print(f"No JSON data found for {conference} {year}. Please save the data first.")
        return

    with open(json_path, 'r', encoding='utf-8') as json_file:
        all_data = json.load(json_file)

    md_path = os.path.join(output_path, f"{conference}-{year}.md")

    # Open the Markdown file for writing
    with open(md_path, 'w', encoding='utf-8') as md_file:
        md_file.write(f"# {conference} {year} Accepted Papers\n\n")

        # Track whether we've written the venue-level section header
        for level in levels:
            venue_written = False

            # Filter papers by level
            level_papers = [paper for paper in all_data if paper.get('level') == level]

            if not level_papers:
                continue  # Skip this level if no papers are available

            # Write the level title
            md_file.write(f"## {level} Accepted Papers\n\n")

            # Write each paper's details
            for idx, paper_data in enumerate(level_papers):
                title = paper_data.get('title', 'No title available')
                md_file.write(f"### {idx + 1}. {title}\n")

                if 'keywords' in paper_data:
                    keywords_str = ', '.join(paper_data['keywords'])
                    md_file.write(f"- **Keywords**: {keywords_str}\n")

                if 'authors' in paper_data:
                    authors_str = ', '.join(paper_data['authors'])
                    md_file.write(f"- **Authors**: {authors_str}\n")

                if 'pdf' in paper_data:
                    pdf = paper_data['pdf']
                    md_file.write(f"- **PDF**: [{title}]({pdf})\n")

                md_file.write("\n")

    print(f"Markdown file has been saved to {md_path}")