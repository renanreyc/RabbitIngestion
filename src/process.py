import os

from rabbitmq.ConfigRabbit import ConsumeRabbit

queue_dpvisibilidadevarejo = os.environ.get("preprod_rabbit_queue", '.env')

if __name__ == "__main__":
    ct_threads = os.environ.get("ct_threads")
    list_queues = [queue_dpvisibilidadevarejo] * int(ct_threads)

    cr = ConsumeRabbit()
    cr.consume_from_multiple_queues(list_queues)
