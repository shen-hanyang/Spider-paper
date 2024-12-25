# Spider-Paper

Spider-Paper is a project designed to scrape and analyze conference paper metadata, such as titles, authors, keywords, and abstracts, from various academic conferences. This repository provides tools for data collection, processing, and visualization.

## Project Structure

The repository is organized into the following directories:

- **data/**: Stores the downloaded conference information, organized by conference name (e.g., ICLR, ICML, MM, NeurIPS).
  - Example:
    - `data/ICLR`
    - `data/ICML`
    - `data/MM`
    - `data/NeurIPS`

- **driver/**: Contains WebDriver executables required for web scraping.
  - Example:
    - `driver/chromedriver.exe`
    - `driver/msedgedriver.exe`

- **spider-paper-request/**: Main directory for crawling and analyzing data.
  - **config/**: Configuration files for the project.
  - **main/**: Scripts for data crawling.
  - **test/**: Scripts for analyzing the collected data.
  - **util/**: Utility functions and scripts.

- **README.md**: This file, providing an overview of the project.
- **requirements.txt**: Python dependencies required to run the project.

## Features

1. **Data Crawling**:
   - Scrape paper metadata, including titles, authors, abstracts, keywords, ratings, and confidences, from academic conferences.
   - Save URLs and paper information in structured formats (e.g., JSON, CSV).

2. **Data Processing**:
   - Extract and process keywords and title information from the collected data.
   - Handle issues like duplicate keywords, plural forms, and stopwords.

3. **Visualization**:
   - Generate bar charts for the most common keywords and title words using Matplotlib.

## Setup Instructions

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/spider-paper.git
   cd spider-paper
   ```

2. **Install Dependencies**:
   Install the required Python libraries using pip:
   ```bash
   pip install -r requirements.txt
   ```

3. **Prepare WebDriver**:
   - Download the appropriate WebDriver for your browser (Chrome or Edge).
   - Place the WebDriver executable in the `driver/` directory.

4. **Configure Settings**:
   - Modify configuration files in the `spider-paper-request/config` directory to set parameters such as conference name, year, and output paths.

## Usage

### Crawling Metadata
Run the main crawling script to collect metadata:
```bash
python spider-paper-request/main/crawl_meta.py
```

### Processing Data
- Extract keywords and titles from the collected JSON files.
- Use the `process_keywords` and `process_titles` functions for cleaning and deduplication.

### Visualization
- Visualize the most common keywords and title words using the `visualize_keywords` and `visualize_titles` functions.

## Examples

### Save Paper Data as JSON
```python
save_data_as_json(conference="ICLR", year="2023", levels=["Oral", "Poster"], output_path="data/ICLR")
```

### Extract Keywords
```python
keywords = get_keywords(json_path="data/ICLR/ICLR-2023.json")
```

### Visualize Keywords
```python
from collections import Counter
keywords_hist = Counter(keywords)
visualize_keywords(keywords_hist, num_keyword=50, path="data/ICLR")
```

### Visualize Titles
```python
titles_hist = Counter(process_titles(get_titles("data/ICLR/ICLR-2023.json")))
visualize_titles(titles_hist, num_title=50, path="data/ICLR")
```

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## Acknowledgments
Special thanks to all contributors and the open-source community for their support.
