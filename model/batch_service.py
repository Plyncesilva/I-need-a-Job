import json
import os
from pathlib import Path
from openai import OpenAI
from openai.types import Batch, FileObject
from typing import List, Dict, Any
from .batch_request import BatchRequest, RequestBody, Message
import uuid

class BatchService:
    REQUEST = Path(__file__).parent.parent / '.data' / 'batch' / 'request'
    RESPONSE = Path(__file__).parent.parent / '.data' / 'batch' / 'response'
    OBJECT = Path(__file__).parent.parent / '.data' / 'batch' / 'object'

    def __init__(self, id: str, client: OpenAI | None = None) -> None:
        if id is None:
            raise ValueError("Batch ID must be provided")
        if client is None:
            raise ValueError("OpenAI client must be provided")

        self.client = client
        self.id = id

    @staticmethod
    def __system_setup_message() -> Message:
        prompt = "From now on, a user request will contain job description information. Each job description is composed of a URI and a description in Danish or English. You should reply with a JSON object for each job description, translate everything to English. Add all Objects on a JSON Array. For each description, a corresponding response should have the following format:\n\n" \
            '[' \
            '{' \
            '"type": "The position type, available values are CYBERSECURITY, SOFTWARE_DEVELOPMENT, IT_CONSULTANT, IT_SUPPORT, CUSTOMER_SERVICE and OTHER",' \
            '"published": "When the job posting was published, format should be Day-Month Numeric code-Year",' \
            '"deadline": "Expected deadline to apply for this job",' \
            '"contractType": "The contract type (full-time, part-time, student job, etc.)",' \
            '"start": "When the candidate is expected to start",' \
            '"language": "Original posting language (Danish/English)",' \
            '"jobTitle": "Position title",' \
            '"companyName": "Hiring organization",' \
            '"location": "Job location",' \
            '"description": "Summarized job description",' \
            '"requirements": "Described job requirements separated with commas",' \
            '"keySkills": "Critical skills/keywords to put on CV separated by commas",' \
            '"contacts": "Relevant recruiter/manager contacts",' \
            '"cvPhotoRequired": "What is mentioned about having a CV photo",' \
            '"applyUri": "Original job posting URL"' \
            '}\n\n' \
            ']\n\n' \
        "If some of the information is missing, please write 'Not mentioned'."
        "You should only reply with the JSON content, without any additional text."

        return Message("system", prompt)

    @staticmethod
    def create_from_messages(messages: List[Message], client: OpenAI) -> 'BatchService':
        """Create a new batch service from a list of request objects."""
        
        # Generate unique filename
        requests_id = uuid.uuid4().hex
        filename = f"batch_{requests_id}.jsonl"
        
        # Create request data directory if it doesn't exist
        data_path = BatchService.REQUEST
        data_path.mkdir(parents=True, exist_ok=True)

        messages = [BatchService.__system_setup_message()] + messages 
        request = BatchRequest.from_messages(requests_id, messages)

        # Write requests to file
        file_path = data_path / filename
        with open(file_path, 'w') as f:
            f.write(str(request) + '\n')
        
        return BatchService(requests_id, client)

    def __request_file_path(self) -> str:
        return str(BatchService.REQUEST / f"batch_{self.id}.jsonl")

    def __object_file_path(self) -> str:
        return str(BatchService.OBJECT / f"batch_{self.id}.json")
    
    def __response_file_path(self) -> str:
        return str(BatchService.RESPONSE / f"batch_{self.id}_response.txt")

    def upload_batch(self) -> None:
        """Upload the batch requests file to OpenAI and store the output batch object."""

        # Upload the file
        try:
            file_path = self.__request_file_path()
            file_object: FileObject = self.client.files.create(
                file=open(file_path, "rb"),
                purpose="batch"
            )
            # Create the batch
            batch_object: Batch = self.client.batches.create(
                input_file_id=file_object.id,
                endpoint="/v1/chat/completions",
                completion_window="24h",
                metadata={
                    "description": "job analysis batch"
                }
            )
            # Save the batch object to a file
            self.__save_batch_object(batch_object)
        except Exception as e:
            raise Exception(f"Failed to upload batch: {e.message}")

    def __load_batch_object(self) -> Batch:
        """Load the batch object from stored file if it exists."""
        batch_file_path = self.OBJECT / f"batch_{self.id}.json"
        with open(batch_file_path, 'r') as f:
            batch_data = json.load(f)
            return self.client.batches.retrieve(batch_data['id'])

    def __save_batch_object(self, batch_object: Batch) -> None:
        """Save the batch object to a file."""
        batch_object_path = self.OBJECT / f"batch_{self.id}.json"
        
        with open(batch_object_path, 'w') as f:
            json.dump(batch_object.to_dict(), f, indent=2)

    def status(self) -> bool:
        """Check if the batch is ready. Returns True if batch is completed, False otherwise.
        Raises exception if batch has failed, expired, or cancelled."""
        batch_object = self.__load_batch_object()

        if batch_object.status in ["failed", "expired", "cancelled"]:
            self._cleanup()
            raise Exception(f"Batch {batch_object.status}")
        
        self.__save_batch_object(batch_object)

        return batch_object.status == "completed"
    
    def _cleanup(self) -> None:
        """Remove the request and object files."""
        request_file = Path(self.__request_file_path())
        object_file = Path(self.__object_file_path())

        if request_file.exists():
            request_file.unlink()
        if object_file.exists():
            object_file.unlink()

    def download_results(self) -> str:
        """Retrieve the batch results and store them in a text file.
        Returns the path to the results file."""
        batch_object = self.__load_batch_object()
        file_response = self.client.files.content(batch_object.output_file_id)
        
        # Create results file
        response_filename = f"batch_{self.id}_response.json"
        response_path = self.RESPONSE / response_filename
        
        # Read the content of the file response
        results = file_response.read().decode('utf-8')

        # Parse the JSON string and extract the message content
        parsed_results = json.loads(results)
        message_content = parsed_results['response']['body']['choices'][0]['message']['content']

        # Remove the first and last line of the message content
        message_lines = message_content.split('\n')
        if len(message_lines) > 2:
            message_content = '\n'.join(message_lines[1:-1])

        # Write the message content to the response file
        with open(response_path, 'w') as f:
            f.write(message_content)

        # Cleanup the request and object files
        self._cleanup()
        
        return response_path