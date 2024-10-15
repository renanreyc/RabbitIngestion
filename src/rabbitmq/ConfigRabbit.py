import json
import uuid
import pika
import os
import threading
from datetime import datetime

from obs.ConfigOBS import OBS
from utils.data_utils.file_converter import FileConverter
from utils.data_utils.metadata_validator import MetadataValidator
from ncs.ConnectionManager import ConnectionManager
from utils.utils import Utils

class ConsumeRabbit:
    def __init__(self): 
        self.__temp_root = os.environ.get("ncs_output_root_path")
        self.__aws_root = os.environ.get("aws_root_path")
        self.__username = os.environ.get("rabbit_username")
        self.__password = os.environ.get("rabbit_password")
        self.__host = os.environ.get("rabbit_host")
        self.__port = os.environ.get("rabbit_port")
        self.__virtual_host = os.environ.get("rabbit_virtual_host")

        self._utils = Utils()
        self._utils.start_logging('start logging ConsumeRabbit')

    def __create_connection_rabbit(self):
        # Configurações de conexão
        
        credentials = pika.PlainCredentials(username=self.__username, password=self.__password)
        parameters = pika.ConnectionParameters( host=self.__host,
                                                port=str(self.__port),
                                                virtual_host=self.__virtual_host,
                                                credentials=credentials)
        # Conectando ao servidor RabbitMQ com autenticação
        connection = pika.BlockingConnection(parameters)
 
        return connection

    def consume_messages(self, queue):
        connection = self.__create_connection_rabbit()
        channel = connection.channel()
        self._utils.logging_status('created connection rabbit')

        # Declarando a fila
        channel.queue_declare(queue=queue, durable=True, exclusive=False, auto_delete=False)

        channel.basic_qos(prefetch_count=1) # adicionado para equilibrar a fila de mensagens entre os consumidores.
        channel.basic_consume(queue=queue, on_message_callback=self.file_to_obs)
        
        print(' [*] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()

    def file_to_obs(self, ch, method, properties, body):
        extraction_date = datetime.now()  

        rabbit_json = json.loads(body.decode())
        exchange_name = method.exchange
        routing_key = method.routing_key
        print("Mensagem recebida da exchange:", exchange_name)
        print("Routing key:", routing_key)
        print(rabbit_json)

        # -----------------------------------------------------------------------------------------
        # --Validate Metadata----------------------------------------------------------------------
        # -----------------------------------------------------------------------------------------
        required_fields = ['repositoryId', 'layout', 'originalFilename', 'tenant', 'documentType', 'dataType', 'format', 'origin']
        metadatavalidator = MetadataValidator(rabbit_json, required_fields)

        result_validate_fields = metadatavalidator.validate_fields()
        if result_validate_fields:
            self._utils.logging_status(f"Campos faltando nos metadados: {', '.join(result_validate_fields)}")
            self._utils.logging_status('returned to RabbitMQ with errors.')
            ch.basic_ack(delivery_tag = method.delivery_tag)

            return None
        
        result_validate_filename_ext = metadatavalidator.validate_filename_extension()
        if result_validate_filename_ext:
            self._utils.logging_status(result_validate_filename_ext)
            self._utils.logging_status('returned to RabbitMQ with errors.')
            ch.basic_ack(delivery_tag = method.delivery_tag)

            return None

        # -----------------------------------------------------------------------------------------
        # --Get Metadata---------------------------------------------------------------------------
        # -----------------------------------------------------------------------------------------
        rx_resource = str(uuid.uuid4())  # Gerar um código aleatório para rxResource
        idDeliveryQueue = rabbit_json.get('idDeliveryQueue', 0)
        layout = str(rabbit_json["layout"])  # "NGP001#PROCESS#17132107640011222798"
        layout_formated = layout.replace("#", "%23")
        original_filename = rabbit_json["originalFilename"]  # "/dawda/32231204876292000181550010000338271782107024-nfe.ngp"
        tenant = str(rabbit_json["tenant"])  # "trimak"
        document_type = str(rabbit_json["documentType"])  # 143
        repository_id = rabbit_json["repositoryId"]
        origin = rabbit_json['origin']

        print(f'idDeliveryQueue: {idDeliveryQueue}')
        print(f'tenant: {tenant}')
        print(f'rx_resource: {rx_resource}')
        
        system = str(routing_key.split('.')[1])
        # -----------------------------------------------------------------------------------------
        # --Download NCS---------------------------------------------------------------------------
        # -----------------------------------------------------------------------------------------       
        if "params" in rabbit_json and "path_default" in rabbit_json["params"]:
            if "ngmapping" in rabbit_json["params"]:
                ngmapping = rabbit_json["params"]["ngmapping"]
                file_path_out = "/".join([self.__aws_root, system, tenant, document_type, ngmapping, original_filename]) 
            else:
                file_path_out = "/".join([self.__aws_root, system, tenant, document_type, original_filename])
        else:
            file_path_out = "/".join([self.__aws_root, original_filename])
        

        
        temp_file_path_out = "/".join([self.__temp_root, file_path_out])

        connectionmanager = ConnectionManager()
        content_file = connectionmanager.download_file(full_path_output=temp_file_path_out,
                                                path='api/v1/file/',
                                                layout=layout_formated + '/',
                                                file_id=repository_id)

        # -----------------------------------------------------------------------------------------
        # --Convert File---------------------------------------------------------------------------
        # -----------------------------------------------------------------------------------------
        fc = FileConverter(temp_file_path_out)
        temp_file_compressed_path = fc.convert_and_compress()

        new_filename = temp_file_compressed_path.split('/')[-1]
        file_path_out = file_path_out.replace(original_filename.split('/')[-1], new_filename)
        # -----------------------------------------------------------------------------------------
        # --Envio para o OBS-----------------------------------------------------------------------
        # -----------------------------------------------------------------------------------------
        
        # system/tenant/document_type/ngmapping/extraction_year/extraction_month/original_filename
        obs = OBS()
        obs.upload_file(file_path_in=temp_file_compressed_path, file_path_out=file_path_out)

        # -----------------------------------------------------------------------------------------
        # --Envia a mensagem de confirmação ao RabbitMQ--------------------------------------------
        # -----------------------------------------------------------------------------------------
        
        self.send_ack_message(
            system_code=system,
            status=0,  # Status 0 para sucesso
            id_delivery_queue=idDeliveryQueue, 
            rx_resource=rx_resource,
            tenant_code=tenant
        )

        # -----------------------------------------------------------------------------------------
        # --Confirma ao rabbitMQ que a mensagem foi processada e pode ser excluída.----------------
        # -----------------------------------------------------------------------------------------
        self._utils.logging_status('returned to RabbitMQ that message was delivered.')
        ch.basic_ack(delivery_tag = method.delivery_tag)

        return None

    def send_ack_message(self, system_code, status, id_delivery_queue, rx_resource, tenant_code):
        # Defina a conexão com o RabbitMQ
        connection = self.__create_connection_rabbit()
        channel = connection.channel()

        # Defina o nome da rota (Routing Key)
        routing_key = f'ngpc.{system_code}.in.ack.route'

        properties = pika.BasicProperties(
            content_type='application/json',
            headers={
                '__TypeId__': 'com.neogrid.ngproxy.dto.ngpc.ConnectorToNgpAckDto'
            }
        )

        message = {
            "status": status,
            "idDeliveryQueue": id_delivery_queue,
            "rxResource": rx_resource[:64], 
            "tenantCode": tenant_code
        }

        channel.basic_publish(
            exchange=f'ngpc.{tenant_code}.topic',
            routing_key=routing_key,
            body=json.dumps(message),
            properties=properties
        )

        print(f"Mensagem enviada para a rota {routing_key}: {message}")
        
        connection.close()


    def consume_from_multiple_queues(self, queues):
        threads = []
        for queue in queues:
            thread = threading.Thread(target=self.consume_messages, args=(queue,))
            thread.start()
            threads.append(thread)
        
        for thread in threads:
            thread.join()