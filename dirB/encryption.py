import os
from typing import Dict, Tuple

import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class Encryption:
    """
    Clase para la encriptación y desencriptación de los datos.
    """

    def __init__(self, password: str = None):
        self.__encriptionEnabled = False
        self.__fernet = None

        self.__passwordProvided = False
        if password:
            print("Todos los datos leídos/escritos con esta instancia se encriptarán con la clave proporcionada.")

            password_byte = password.encode('utf-8')
            salt = os.urandom(16)

            kdf = PBKDF2HMAC(algorithm = hashes.SHA256(), length = 32, salt = salt, iterations = 1000000)
            key = base64.urlsafe_b64encode(kdf.derive(password_byte))
            self.__fernet = Fernet(key)

            self.__password = password
            self.__passwordProvided = True
    
    def __encriptaString(self, texto: str):
        return self.__fernet.encrypt(str(texto).encode('utf-8')).decode('utf-8')

    def claveProporcionada(self) -> bool:
        return self.__passwordProvided

    def encriptaDiccionario(self, diccionario: Dict[str, str] = None, incluyeMetadatos: bool = False) -> Dict[str, str]:
        """
        Encripta el diccionario pasado como parámetro con la clave proporcionada al crear la instancia. Si ninguna clave fue 
        proporcionada, se devuelve el mismo diccionario que se pasó por parámetro
        
        :param Dict[str, str] diccionario: el diccionario a encriptar
        :param bool incluyeMetadatos: usado para añadir metadatos de la encriptación al diccionario. E.g. si el diccionario está
                                   encriptado o no, incluir la clave como un campo adicional en el diccionario resultante, 
                                   útil para futuras comprobaciones en el método desencriptaDiccionario(...), donde se mira 
                                   si la clave es correcta.
        :return Dict[str, str]: el diccionario encriptado, o el mismo diccionario si ninguna clave fue proporcionada.
        """
        
        if not diccionario:
            return {}

        if not self.__fernet:
            diccionario["encrypted"] = "False"
            return diccionario

        diccionario_encrypted = {}
        if incluyeMetadatos:
            diccionario_encrypted["encrypted"] = "True"
            diccionario_encrypted["password"] = self.__encriptaString(self.__password)

        for key, value in diccionario.items():
            key_encrypted = self.__encriptaString(key)
            val_encrypted = self.__encriptaString(value)

            diccionario_encrypted[key_encrypted] = val_encrypted

        return diccionario_encrypted
    
    def claveCorrecta(self, diccionario: Dict) -> bool:
        if "password" not in diccionario:
            print("El diccionario proporcionado no contiene ningún campo \"password\"")
            return None
        
        dictPassword = self.__fernet.decrypt(diccionario["password"]).decode('utf-8')
        if dictPassword == self.__password:
            return True
        
        return False

    def desencriptaDiccionario(self, diccionario: Dict[str, str], soloKeys: bool = False) -> Tuple[bool, Dict[str, str]]:
        """
        Desencripta el diccionario pasado por parámetro con la clave proporcionada al crear la instancia. Asume que la clave 
        que alguna clave fue proporcionada y que además es correcta (no lo comprueba).
        
        :param Dict[str, str] diccionario: el diccionario a desencriptar.
        :param bool soloKeys: si True, tan sólo las claves de los pares <clave, valor> del diccionario retornado estarán 
                              desencriptadas. Si False, el diccionario completo se retornará desencriptado.
        :return Dict[str, str]: el diccionario desencriptado.
        """

        if not diccionario:
            return {}
        
        dicParamsCaso_decrypted: Dict[str, str] = {"encrypted" : "0"}
        for key, value in self.dicParamsCaso.items():
            if key != "encrypted":
                key_decrypted = self.__fernet.decrypt(key).decode('utf-8')
                value_decrypted = self.__fernet.decrypt(value).decode('utf-8')
                
                dicParamsCaso_decrypted[key_decrypted] = value if soloKeys else value_decrypted

        return dicParamsCaso_decrypted