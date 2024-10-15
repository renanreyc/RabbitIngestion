import os
from dotenv import load_dotenv 

from rabbitmq.ConfigRabbit import ConsumeRabbit

load_dotenv()

queue_dpvisibilidadevarejo = os.environ.get("rabbit_queue", '.env')
ct_threads = os.environ.get("ct_threads")

if __name__ == "__main__":
    list_queues = [queue_dpvisibilidadevarejo] * int(ct_threads)

    cr = ConsumeRabbit()
    cr.consume_from_multiple_queues(list_queues)
