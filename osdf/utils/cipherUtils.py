#
# -------------------------------------------------------------------------
#   Copyright (C) 2020 Wipro Limited.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# -------------------------------------------------------------------------

from Crypto.Cipher import AES
from osdf.config.base import osdf_config
from Crypto.Util.Padding import unpad
from Crypto.Util.Padding import pad


class AESCipher(object):
    __instance = None

    @staticmethod
    def get_instance(key = None):
        if AESCipher.__instance is None:
            print("Creating the singleton instance")
            AESCipher(key)
        return AESCipher.__instance

    def __init__(self, key=None):
        if AESCipher.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            AESCipher.__instance = self

        self.bs = 32
        if key is None:
            key = osdf_config.deployment["appkey"]

        self.key = key.encode()

    def encrypt(self, data):
        data = data.encode()
        cipher = AES.new(self.key, AES.MODE_CBC)
        ciphered_data = cipher.encrypt(pad(data, AES.block_size))
        enc = (cipher.iv.hex())+(ciphered_data.hex())
        return enc

    def decrypt(self, enc):
        iv = bytes.fromhex(enc[:32])
        ciphered_data = bytes.fromhex(enc[32:])
        cipher = AES.new(self.key, AES.MODE_CBC, iv=iv)
        original_data = unpad(cipher.decrypt(ciphered_data), AES.block_size).decode()
        return original_data
