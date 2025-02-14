# DTU CareerHub Scraper

This project is a web scraper and analyzer for job postings from the DTU CareerHub. It fetches job postings, processes them, and saves the results in a structured format.
 It uses AI to summarize and structure job description HTML pages.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/dtu_careerhub.git
    cd dtu_careerhub
    ```

2. Create a virtual environment and activate it:
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Set up environment variables:
    - Create a `.env` file in the root directory.
    - Add your API keys and other necessary environment variables to the `.env` file:
        ```
        DEEPSEEK_API_KEY=your_deepseek_api_key
        OPENAI_API_KEY=your_openai_api_key
        ```

## Usage

1. Add your cookies to the `dtu_scraper.py` file in the headers section.

2. Fetch job postings:
    ```bash
    python dtu_scraper.py --url [url with search filters on the platform] --out [output file with urls]
    ```

3. Analyze job postings:
    ```bash
    python analyze.py -f path_to_file_with_job_uris
    ```

2. Analyze job postings:
    ```bash
    python analyze.py -f path_to_file_with_job_uris
    ```

## Project Structure

- `dtu_scraper.py`: Contains functions to fetch job postings from the DTU CareerHub.
- `analyze.py`: Analyzes the fetched job postings and saves the results.
- `job.py`: Defines the `Job` and `JobList` models.
- `job_posting.py`: Contains the `DTUJobPosting` class for extracting job descriptions.
- `jobrepository.py`: Manages the storage of job postings.
- `prompt.py`: Handles the interaction with the OpenAI API for processing job descriptions.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.