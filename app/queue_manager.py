from redis import Redis
from rq import Queue
import json

redis_conn = Redis(host='localhost', port=6379)
task_queue = Queue(connection=redis_conn)

class QueueManager:
    def __init__(self):
        self.queue = task_queue

    async def add_job(self, scraper_config, run_config):
        job = self.queue.enqueue(
            'scraping_engine.process_job',
            args=(scraper_config, run_config),
            job_timeout='1h'
        )
        return job.id

    async def get_job_status(self, job_id):
        job = self.queue.fetch_job(job_id)
        if job is None:
            return None
        return {
            'id': job.id,
            'status': job.get_status(),
            'result': job.result,
            'error': job.exc_info
        }

queue_manager = QueueManager() 