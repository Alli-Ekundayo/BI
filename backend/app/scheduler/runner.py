import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from app.scheduler.jobs import register_all_jobs

logger = logging.getLogger(__name__)

class SchedulerRunner:
    """Manages the APScheduler instance and lifecycle."""
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self._setup_listeners()

    def _setup_listeners(self):
        """Setup event listeners for job monitoring."""
        def job_listener(event):
            if event.exception:
                logger.error(f"Job {event.job_id} failed: {event.exception}")
                # TODO: Trigger system notification for job failure
            else:
                logger.debug(f"Job {event.job_id} executed successfully.")

        self.scheduler.add_listener(
            job_listener, 
            EVENT_JOB_ERROR | EVENT_JOB_EXECUTED
        )

    def start(self):
        """Register jobs and start the scheduler."""
        logger.info("Initializing analytics scheduler...")
        # Register all our 25+ analytics jobs
        register_all_jobs(self.scheduler)
        
        self.scheduler.start()
        logger.info(f"Scheduler started with {len(self.scheduler.get_jobs())} jobs.")

    def shutdown(self):
        """Gracefully shutdown the scheduler."""
        logger.info("Shutting down analytics scheduler...")
        self.scheduler.shutdown()

runner = SchedulerRunner()
