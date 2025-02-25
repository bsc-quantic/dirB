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

    def __init__(self):
        self.__fernet = None
        self.__encryptionEnabled = False

    def __initEncryptionInstance(self, password: str, salt: bytes):
        password_byte = password.encode('utf-8')

        kdf = PBKDF2HMAC(algorithm = hashes.SHA256(), length = 32, salt = salt, iterations = 1000000)
        key = base64.urlsafe_b64encode(kdf.derive(password_byte))
        self.__fernet = Fernet(key)

        # For metadata:
        self.__password = password
        self.__salt = salt.decode('ISO-8859-1')

        self.__encryptionEnabled = True

    def createNewEncryption(self, password: str):
        """
        Initialize encryption instance with a password.

        :param password str: the password to be used to initialize the Fernet instance.
        """

        self.__initEncryptionInstance(password, os.urandom(16))
    
    def loadEncryption(self, password: str, saltString: str):
        """
        Initialize encryption with a password and a salt parameters.

        :param password str: the password to be used to initialize the Fernet instance.
        :param salt str: the salt used to initialize the Fernet instance.
        """

        self.__initEncryptionInstance(password, saltString.encode('ISO-8859-1'))

    def __encriptaString(self, texto: str) -> str:
        return self.__fernet.encrypt(str(texto).encode('utf-8')).decode('utf-8')
    
    def __desencriptaString(self, texto: str) -> str:
        return self.__fernet.decrypt(texto).decode('utf-8')

    def encriptacionHabilitada(self) -> bool:
        return self.__encryptionEnabled

    def claveCorrecta(self, encryptedPassword: str) -> bool:
        """
        Retorna True si la clave proporcionada para initializar la instancia se corresponde con la pasada por argumento, False en cualquier otro caso.

        :param str encryptedPassword: la clave encriptada.
        """

        if not self.encriptacionHabilitada():
            print("Método claveCorrecta(...) - Encriptación no habilitada.")
            return None
        
        try:
            dictPassword = self.__desencriptaString(encryptedPassword)
        except Exception as e:
            print(e)
            return False
        if dictPassword == self.__password:
            return True
        
        return False

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
        
        if not self.encriptacionHabilitada():
            if incluyeMetadatos:
                diccionario["encrypted"] = "False"
            return diccionario
        
        diccionario_encrypted = {}
        if incluyeMetadatos:
            diccionario_encrypted["encrypted"] = "True"
            diccionario_encrypted["password"] = self.__encriptaString(self.__password)
            diccionario_encrypted["salt"] = self.__salt

        for key, value in diccionario.items():
            key_encrypted = self.__encriptaString(key)
            val_encrypted = self.__encriptaString(value)

            diccionario_encrypted[key_encrypted] = val_encrypted

        return diccionario_encrypted

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
        
        if not self.encriptacionHabilitada():
            print("Método desencriptaDiccionario(...) - Encriptación no habilitada.")
            return None

        dicParamsCaso_decrypted: Dict[str, str] = {}
        for key, value in diccionario.items():
            if key == "encrypted":
                if soloKeys: 
                    dicParamsCaso_decrypted["encrypted"] = "True"
                else:
                    dicParamsCaso_decrypted["encrypted"] = "False"
            elif key == "password" or key == "salt":
                dicParamsCaso_decrypted[key] = value
            else:
                key_decrypted = self.__desencriptaString(key)

                dicParamsCaso_decrypted[key_decrypted] = value if soloKeys else self.__desencriptaString(value)

        return dicParamsCaso_decrypted

    def desencriptaTexto(self, texto: str) -> str:
        if not self.encriptacionHabilitada():
            print("Método desencriptaText(...) - Encriptación no habilitada.")
            return None
        
        return self.__desencriptaString(str(texto).encode('utf-8'))