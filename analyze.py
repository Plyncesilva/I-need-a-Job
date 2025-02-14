#!.venv/bin/python

from openai import OpenAI
from dotenv import load_dotenv

import argparse
import logging
import os
from pathlib import Path

from model import BatchService, DTUJobPosting, JobRepository, JobType, Prompt
import time
from json import load
import openai
from model import Job, JobList
import random
import json

# Load environment variables from .env file
load_dotenv()

# Get API keys from environment variables
deepseek_client = OpenAI(
    api_key=os.getenv('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com"
)
openai_client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY')
)

def create_data_directory():
    base_dir = Path(__file__).parent / '.data'
    directories = [
        base_dir / 'memory'
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        logging.info(f"Created directory at {directory}")
    
    # Create file if does not exist
    memory_file = Path(__file__).parent / '.data' / 'memory' / 'analyzed_uris.txt'
    memory_file.parent.mkdir(parents=True, exist_ok=True)
    if not memory_file.exists():
        memory_file.touch()

    return base_dir

def setup_logging(debug=False):
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def load_input(file_path: str) -> list[str]:
    """
    Read lines from a file and return them as a list of strings.

    Args:
        file_path (str): Path to the input file.

    Returns:
        list[str]: List of strings, with each string representing a line from the file.
    """
    with open(file_path, 'r') as file:
        return [line.strip() for line in file]

def check_if_processed(uri: str) -> bool:
    memory_file = Path(__file__).parent / '.data' / 'memory' / 'analyzed_uris.txt'
    with open(memory_file, 'r') as f:
        for line in f:
            if uri == line.strip():
                return True
    return False

def add_analyzed_uri(uri: str):
    memory_file = Path(__file__).parent / '.data' / 'memory' / 'analyzed_uris.txt'
    with open(memory_file, 'a') as f:
        f.write(f"{uri}\n")

def process_uris(job_listings: list[str]) -> str:

    for uri in job_listings:
        if check_if_processed(uri):
            logging.warning(f"Skipping {uri}: Already processed")
            job_listings.remove(uri)
            continue
    
    messages = []
    successful = 0
    failed = 0
    empty = 0

    for uri in job_listings:
        try:
            posting = DTUJobPosting(uri)
            posting.extract_job_description()

            if posting.job_description == "" or posting.job_description is None:
                logging.warning(f"Skipping {uri}: Empty job description")
                job_listings.remove(uri)
                empty += 1
                continue
            messages.append(posting.to_message())
            successful += 1
            logging.info(f"Successfully processed job listing: {uri}")

            sleep_time = random.randint(60, 300)
            logging.info(f"Sleeping for {sleep_time} seconds to avoid web scraping rate limits")
            for i in range(sleep_time, 0, -1):
                minutes = i // 60
                seconds = i % 60
                print(f"\rTime remaining: {minutes}m {seconds}s", end='', flush=True)
                time.sleep(1)
            print("\rSleep complete.              ")
        except Exception as e:
            logging.error(f"Failed to process {uri}: {str(e)}")
            failed += 1
            continue

    logging.info(f"Processing summary: {successful} successful, {failed} failed, {empty} empty")
    
    if not messages:
        logging.info("No valid job descriptions found, exiting")
        return None
        
    logging.info(f"Prompting ChatGPT-4o with {len(messages)} messages")
    
    try:
        
        response = Prompt(client=openai_client).prompt(messages)
        return response
    
    except openai.BadRequestError as e:
        logging.error(f"Bad Request: {e}")
    except openai.AuthenticationError as e:
        logging.error(f"Authentication Error: {e}")
    except openai.RateLimitError as e:
        logging.error(f"Rate Limit Exceeded: {e}")
    except openai.OpenAIError as e:
        logging.error(f"OpenAI API Error: {e}")
    except Exception as e:
        logging.error(f"Unexpected Error: {str(e)}")

    return None

def save_and_catalog_results(results: str):

    # Convert string to JobList object
    job_list = JobList.model_validate_json(results)

    # Initialize Job repositories
    job_repository = JobRepository()

    # Add jobs to repository
    for job in job_list.jobs:
        job_repository.add_job(job)
        logging.info(f"Added job to repository: {job.job_title}")

    # Save jobs to JSON files
    job_repository.save_jobs()

    logging.info("Successfully saved job data to local repository")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Job Description Analyzer Bot",
        epilog="Example usage:\n"
               "  python analyze_jobs.py -f [file path] \n"
               "  python analyze_jobs.py -b [batch file path] \n",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('-f', '--file', type=str, help='Input file with job URIs', required=True)
    args = parser.parse_args()

    setup_logging(args.debug)
    logging.info("Starting Job Description Analyzer Bot")

    data_dir = create_data_directory()
    logging.info(f"Data directory initialized at: {data_dir}")

    job_listings = load_input(args.file)

    wave_size = 10
    
    for i in range(0, len(job_listings), wave_size):
        wave = job_listings[i:i + wave_size]
        print()
        logging.info(f"Processing wave {i//wave_size + 1} with {len(wave)} listings")
        response = process_uris(wave)
        if response:
            try:
                save_and_catalog_results(response)
                for uri in wave:
                    add_analyzed_uri(uri)
            except Exception as e:
                logging.error(f"Failed to save results: {str(e)}")