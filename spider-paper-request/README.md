# Spider-Paper-Request

**Spider-Paper-Request** is a Python-based tool for scraping, processing, and visualizing metadata from academic conferences (such as NeurIPS, ICML, and ICLR). This tool extracts paper information, including title, authors, keywords, abstracts, and PDFs, and stores the data in JSON and CSV formats. It also generates Markdown files for easy browsing and visualizing the extracted data.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Data Processing](#data-processing)
- [Visualization](#visualization)
- [Contributing](#contributing)
- [License](#license)

## Features
- **Metadata Scraping**: Extract paper metadata from the OpenReview API.
- **Data Storage**: Save data in JSON and CSV formats.
- **Markdown Generation**: Generate Markdown files for browsing accepted papers.
- **Keyword and Title Analysis**: Process and visualize extracted keywords and titles from papers.
- **Pagination Support**: Handle large datasets with pagination in API requests.
- **Retry Logic**: Implement retry logic to handle API request failures.

## Installation

Clone the repository:

```bash
git clone https://github.com/shen-hanyang/Spider-paper.git
cd spider-paper-request
```
Install the required dependencies:

```bash
pip install -r requirements.txt
```
Make sure you have Python 3.7 or higher installed.

## Usage
### Custom Configuration
Modify the `config.py` file to change the conference name, year, display level, and URL settings.

**Set Conference Name Example**: NeurIPS

```python
parser.add_argument('--conference', type=str, default='NeurIPS')
```

**Set Year Example**: 2024

```python
parser.add_argument('--year', type=str, default='2024')
```

**Set Display Level Example**: Oral

```python
parser.add_argument('--level', type=str, default='oral')
```

**Set URL Example**:

For NeurIPS 2024, first find the URL for the NeurIPS 2024 OpenReview webpage (e.g., https://openreview.net/group?id=NeurIPS.cc/2024/Conference#tab-accept-oral). This page shows accepted oral-level papers.

![image-20241225124917818](/assets/image-20241225124917818.png)

To scrape papers for all levels (Oral, Spotlight, Poster), set the level parameter accordingly. The URL can be retrieved by inspecting the network request in the browser's developer tools.

Open the "Network" tab, click the "Next" button on the page, and find the URL of the data request.

![image-20241225125232970](/assets/image-20241225125232970.png)

![image-20241225125510661](/assets/image-20241225125510661.png)

The request URL we found is: https://api2.openreview.net/notes?content.venue=NeurIPS%202024%20oral&details=replyCount%2Cpresentation&domain=NeurIPS.cc%2F2024%2FConference&limit=25&offset=25.

![image-20241225125641982](/assets/image-20241225125641982.png)

Note:
- The limit parameter represents the maximum number of papers per request and can be set to 1000.
- The offset parameter represents the starting index for scraping.

For scraping NeurIPS 2024 Oral papers, set the URL as:

https://api2.openreview.net/notes?content.venue=NeurIPS%202024%20oral&details=replyCount%2Cpresentation&domain=NeurIPS.cc%2F2024%2FConference&limit=1000&offset=0

```python
parser.add_argument('--url', type=str, default='https://api2.openreview.net/notes?content.venue=NeurIPS%202024%20oral&details=replyCount%2Cpresentation&domain=NeurIPS.cc%2F2024%2FConference&limit=1000&offset=0')
```

### Run `Main Script`

Run the script to crawl paper metadata based on the configuration in config.py.

```bash
python main.py
```

### Run `Test Script`

Run the test script for data analysis based on the configuration.

```bash
python test.py
```
**<font color="red">!!!Some meeting metadata may not contain keywords!!!</font>**

## Config

The config.py file contains the configuration settings for the tool. You can modify the following parameters:

- Conference: The conference name (e.g., NeurIPS, ICML, ICLR).
- Year: The conference year (e.g., 2024).
- Level: The paper presentation level (e.g., Oral, Spotlight, Poster).
- URL: The base URL for the OpenReview API.
- Start Time/Stop Time: The range of random delays between API requests.
- Timeout: The timeout duration for API requests.
- Save Paths: The directory to save the JSON and CSV files.

## Data Processing
The tool processes the extracted data in the following steps:

### Scrape Metadata
- The `crawl_meta` function uses retry logic and pagination support to fetch metadata from the OpenReview API.
- The data is saved as a JSON file.

### Extract Information
- The `crawl_json` function processes the JSON file to extract titles, authors, keywords, abstracts, PDFs, and other relevant information.
- The extracted data is saved as a CSV file.
- **<font color="red">!!!Temporarily unavailable!!!</font>**

### Keyword and Title Analysis
- The `get_keywords` and `get_titles` functions extract keywords and titles from the JSON file.
- The `process_keywords` and `process_titles` functions clean and standardize the extracted data.

## Visualization
The tool provides the following visualization features:

### Keyword Frequency
The `visualize_keywords` function generates horizontal bar charts displaying the most frequent keywords.

### Title Word Frequency
The `visualize_titles` function generates horizontal bar charts displaying the most frequent words in paper titles.

### Json File
The `save_data_as_json` function generates a Json file summarizing the accepted papers, including title, keywords, authors, and PDF links.

### Markdown File
The `generate_markdown_from_json` function generates a Markdown file summarizing the accepted papers, including title, keywords, authors, and PDF links.

## Contributing
Contributions are welcome! If you encounter any issues or have feature requests, feel free to submit a pull request or open an issue.

## License
This project is licensed under the MIT License. See the LICENSE file for details.