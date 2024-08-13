import requests
import os

from utils.utils import Utils

class ConnectionManager:
    """
    A class to connect to the NCS API.
    """

    def __init__(self):
        """
        Initialize ConnectionManager

        conn = ConnectionManager()

        Returns 
        -------
        new ConnectionManager class

        """
        self.get_url = os.environ.get('ncs_get_url', '.env') 
        self.post_url = os.environ.get('ncs_post_url', '.env')
        self._utils = Utils()
        self._utils.start_logging('start logging ConnectionManager.')

        pass

    def download_file(self, full_path_output, path, layout, file_id):
        url = self.get_url + path + layout + file_id

        try:
            self._utils.logging_status(f'downloading NCS File: {full_path_output}')
            response = requests.get(url)
            if response.status_code == 200:
                directory = os.path.dirname(full_path_output)
                try: 
                    if not os.path.exists(directory):
                        os.makedirs(directory)
                except PermissionError:
                    print(f"Permissão negada: não é possível criar o diretório/diretório já existe: {directory}")

                with open(full_path_output, "wb") as file:
                    file.write(response.content)
                
                self._utils.logging_status(f'downloaded NCS File: {full_path_output}')
                return response.content
            
            else:
                self._utils.logging_status(f'Falha no download. Código de status: {response.status_code}')
                return False
        except requests.exceptions.RequestException as e:
            self._utils.logging_status(f'Erro ao fazer solicitação: {e}')
            return False
