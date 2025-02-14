import os
from typing import Set
from .Job import Job, JobType

class JobRepository:
    paths = {
        JobType.CYBERSECURITY: "results/jobs/cybersecurity",
        JobType.SOFTWARE_DEVELOPMENT: "results/jobs/software_development",
        JobType.IT_CONSULTANT: "results/jobs/it_consultant",
        JobType.IT_SUPPORT: "results/jobs/it_support",
        JobType.CUSTOMER_SERVICE: "results/jobs/customer_service",
        JobType.OTHER: "results/jobs/other"
    }

    def __init__(self):
        # Create a dictionary to store jobs by type
        self.jobs_by_type: dict[JobType, list[Job]] = {
            job_type: [] for job_type in JobType
        }
        self._ensure_directories_exist()

    def _ensure_directories_exist(self) -> None:
        """Ensure all directories for storing job JSON files exist."""
        for path in self.paths.values():
            os.makedirs(path, exist_ok=True)

    def add_job(self, job: Job) -> bool:
        """
        Add a job to the repository in its corresponding job type set.
        Returns True if job was added.
        """
        self.jobs_by_type[job.job_type].append(job)
        return True

    def _save_job_to_file(self, job: Job) -> None:
        """Save a job as a JSON file in the appropriate directory."""
        filename = "".join(c if c.isalnum() else "_" for c in job.published + "_" + job.job_title) + ".json"
        file_path = os.path.join(self.paths[job.job_type], filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(job.model_dump_json(indent=2))

    def save_jobs(self) -> None:
        """Save all jobs in the repository to JSON files."""
        for job_type, jobs in self.jobs_by_type.items():
            for job in jobs:
                self._save_job_to_file(job)

    def clear(self):
        """Remove all jobs from the repository."""
        for jobs in self.jobs_by_type.values():
            jobs.clear()