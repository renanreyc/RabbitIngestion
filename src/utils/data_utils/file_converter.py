import gzip
import codecs
import os

from utils.utils import Utils

class FileConverter:
    def __init__(self, sourceFileName, targetFileName = None, source_encoding = 'UTF-8'):
        self.sourceFileName = sourceFileName
        self.source_encoding = source_encoding

        if targetFileName:
            self.targetFileName = targetFileName
            self.compressed_file = targetFileName + ".gz"
        else: 
            self.targetFileName = sourceFileName
            self.target_compressed_file_name = sourceFileName + ".gz"

        self._utils = Utils()
        self._utils.start_logging('File Converter Tool')

    def convert_to_utf8(self):
        """
        Método para conversão de arquivo para UTF-8.

        :return: True se a conversão for bem-sucedida, False caso contrário
        """
        try:
            BLOCKSIZE = 1048576 # or some other, desired size in bytes
            with codecs.open(self.sourceFileName, "r", self.source_encoding) as sourceFile:
                with codecs.open(self.targetFileName, "w", "utf-8") as targetFile:
                    while True:
                        contents = sourceFile.read(BLOCKSIZE)
                        if not contents:
                            break
                        targetFile.write(contents)
                    
                    print(f'{self.targetFileName} salved with success!')
                
            self._utils.logging_status(f"Converted file {self.sourceFileName} to UTF-8 successfully.")
            return True
        except Exception as e:
            self._utils.logging_status("Error:", e)
            return False

    def compress_file(self):
        """
        Compacta o arquivo se ele ainda não estiver compactado.

        :return: True se a compactação for bem-sucedida, False caso contrário
        """        
        try:
            with open(self.targetFileName, 'rb') as f_in:
                with gzip.open(self.target_compressed_file_name, 'wb') as f_out:
                    f_out.writelines(f_in)
            
            self._utils.logging_status(f"Compressed file {self.sourceFileName} successfully.")
            return True
        except Exception as e:
            print("Error:", e)
            return False
    
    def is_compressed(self):
        """
        Verifica se o arquivo já está compactado.

        :return: True se o arquivo já estiver compactado, False caso contrário
        """
        compressed_extensions = ('.gz', '.zip')
        return self.targetFileName.endswith(compressed_extensions)


    def convert_and_compress(self):
        """
        Converte o arquivo para UTF-8 e o compacta, se necessário.

        :return: Nome do arquivo compactado se bem-sucedido, None caso contrário
        """
        # to do: validar a necessidade de conversão de arquivos nessa etapa do processo.
        # if self.convert_to_utf8():
        # else:
        #     self._utils.logging_status(f"Conversion to UTF-8 failed.")
        #     return False

        if self.is_compressed():
            self._utils.logging_status(f"O arquivo {self.targetFileName} já está compactado.")
            return self.targetFileName
        elif self.compress_file():
            os.remove(self.targetFileName)
            return self.target_compressed_file_name
        else:
            self._utils.logging_status(f"Compression failed.")
            return False





