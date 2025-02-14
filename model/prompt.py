from openai import OpenAI
import openai

from .batch_request import Message

from model import JobList

class Prompt:

    SYSTEM_PROMPT = "From now on, a user request will contain job description information. Each job description is composed of a URI and a description in Danish or English. You should reply with a JSON object for each job description, translate everything to English. Add all Objects on a JSON Array. For each description, a corresponding response should have the following format:\n\n" \
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
        '"requirements": "list of described job requirements separated",' \
        '"keySkills": "List of critical skills/keywords to put on CV",' \
        '"contacts": "Relevant recruiter/manager contacts",' \
        '"cvPhotoRequired": "What is mentioned about having a CV photo",' \
        '"applyUri": "Original job posting URL"' \
        '}\n\n' \
        ']\n\n' \
    "If some of the information is missing, please write 'Not mentioned'." \
    "You should only reply with the JSON content, without any additional text."


    def __init__(self, client: OpenAI):
        """Initialize the Prompt class with an OpenAI client."""
        if client is None:
            raise ValueError("OpenAI client must be provided")

        self.client = client

    def prompt(self, user_messages: list[Message], model: str = "gpt-4o") -> str:
        """
        Send a prompt to OpenAI and get the response.
        
        Args:
            message: The message to send to the model
            model: The model to use (defaults to gpt-3.5-turbo)
            
        Returns:
            str: The model's response
        """
        system_message = Message("system", self.SYSTEM_PROMPT)
        messages = [system_message] + user_messages
        messages = [message.to_dict() for message in messages]
        
        response = self.client.beta.chat.completions.parse(model=model,messages=messages,max_tokens=15000,response_format=JobList)

        if response.choices is None or len(response.choices) == 0:
            raise ValueError("No response received from OpenAI")
    
        return response.choices[0].message.content