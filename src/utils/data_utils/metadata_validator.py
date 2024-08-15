import os

class MetadataValidator:
    def __init__(self, metadata, required_fields):
        """
        Inicializa o validador de metadados.

        :param metadata: dicionário contendo os metadados
        :param required_fields: lista de campos obrigatórios
        """
        self.metadata = metadata
        self.required_fields = required_fields

    def validate_fields(self):
        """
        Valida se todos os campos obrigatórios estão presentes nos metadados.

        :return: False se todos os campos obrigatórios estiverem presentes, False caso contrário retorna os campos faltando.
        """
        missing_fields = [field for field in self.required_fields if field not in self.metadata]
        if missing_fields:
            print(f"Campos faltando nos metadados: {', '.join(missing_fields)}")
            return missing_fields
        return False

    def validate_filename_extension(self):
        """
        Valida se o originalFilename possui extensão.

        :return: False se a extensão for válida, True caso contrário
        """
        filename = self.metadata.get('originalFilename', '')
        if not filename:
            message_error = "originalFilename não está presente nos metadados."
            return message_error

        ext = os.path.splitext(filename)[1].lower()
        if not ext:
            message_error = f"Extensão de arquivo esperada, mas não há extensão: {filename}"
            return message_error
        return False

