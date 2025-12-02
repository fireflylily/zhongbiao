"""
加密工具类

提供多种加密算法支持:
- AES加密/解密
- 3DES加密/解密
- CRC32校验和生成
"""

import base64
import hashlib
import zlib
from Crypto.Cipher import AES, DES3, DES
from Crypto.Util.Padding import pad, unpad
from typing import Optional


class CryptoUtils:
    """加密工具类"""

    @staticmethod
    def aes_encrypt(key: str, iv: str, plaintext: str) -> str:
        """
        AES加密

        Args:
            key: Base64编码的密钥
            iv: 初始化向量(16字节)
            plaintext: 明文

        Returns:
            Base64编码的密文
        """
        try:
            # 解码密钥
            key_bytes = base64.b64decode(key)
            iv_bytes = iv.encode('utf-8')[:16]  # 确保IV是16字节

            # 创建AES cipher
            cipher = AES.new(key_bytes, AES.MODE_CBC, iv_bytes)

            # 加密
            plaintext_bytes = plaintext.encode('utf-8')
            padded_plaintext = pad(plaintext_bytes, AES.block_size)
            ciphertext = cipher.encrypt(padded_plaintext)

            # Base64编码
            return base64.b64encode(ciphertext).decode('utf-8')
        except Exception as e:
            raise ValueError(f"AES加密失败: {str(e)}")

    @staticmethod
    def aes_decrypt(key: str, iv: str, ciphertext: str) -> str:
        """
        AES解密

        Args:
            key: Base64编码的密钥
            iv: 初始化向量(16字节)
            ciphertext: Base64编码的密文

        Returns:
            解密后的明文
        """
        try:
            # 解码密钥和密文
            key_bytes = base64.b64decode(key)
            iv_bytes = iv.encode('utf-8')[:16]
            ciphertext_bytes = base64.b64decode(ciphertext)

            # 创建AES cipher
            cipher = AES.new(key_bytes, AES.MODE_CBC, iv_bytes)

            # 解密
            padded_plaintext = cipher.decrypt(ciphertext_bytes)
            plaintext_bytes = unpad(padded_plaintext, AES.block_size)

            return plaintext_bytes.decode('utf-8')
        except Exception as e:
            raise ValueError(f"AES解密失败: {str(e)}")

    @staticmethod
    def des_encrypt(key: str, iv: str, plaintext: str) -> str:
        """
        DES加密

        Args:
            key: Base64编码的密钥(8字节)
            iv: 初始化向量(8字节)
            plaintext: 明文

        Returns:
            Base64编码的密文
        """
        try:
            # 解码密钥
            key_bytes = base64.b64decode(key)[:8]  # DES需要8字节密钥
            iv_bytes = iv.encode('utf-8')[:8]  # DES的IV是8字节

            # 创建DES cipher
            cipher = DES.new(key_bytes, DES.MODE_CBC, iv_bytes)

            # 加密
            plaintext_bytes = plaintext.encode('utf-8')
            padded_plaintext = pad(plaintext_bytes, DES.block_size)
            ciphertext = cipher.encrypt(padded_plaintext)

            # Base64编码
            return base64.b64encode(ciphertext).decode('utf-8')
        except Exception as e:
            raise ValueError(f"DES加密失败: {str(e)}")

    @staticmethod
    def des_decrypt(key: str, iv: str, ciphertext: str) -> str:
        """
        DES解密

        Args:
            key: Base64编码的密钥(8字节)
            iv: 初始化向量(8字节)
            ciphertext: Base64编码的密文

        Returns:
            解密后的明文
        """
        try:
            # 解码密钥和密文
            key_bytes = base64.b64decode(key)[:8]
            iv_bytes = iv.encode('utf-8')[:8]
            ciphertext_bytes = base64.b64decode(ciphertext)

            # 创建DES cipher
            cipher = DES.new(key_bytes, DES.MODE_CBC, iv_bytes)

            # 解密
            padded_plaintext = cipher.decrypt(ciphertext_bytes)
            plaintext_bytes = unpad(padded_plaintext, DES.block_size)

            return plaintext_bytes.decode('utf-8')
        except Exception as e:
            raise ValueError(f"DES解密失败: {str(e)}")

    @staticmethod
    def des3_encrypt(key: str, iv: str, plaintext: str) -> str:
        """
        3DES加密

        Args:
            key: Base64编码的密钥(24字节)
            iv: 初始化向量(8字节)
            plaintext: 明文

        Returns:
            Base64编码的密文
        """
        try:
            # 解码密钥
            key_bytes = base64.b64decode(key)[:24]  # 3DES需要24字节密钥
            iv_bytes = iv.encode('utf-8')[:8]  # 3DES的IV是8字节

            # 创建3DES cipher
            cipher = DES3.new(key_bytes, DES3.MODE_CBC, iv_bytes)

            # 加密
            plaintext_bytes = plaintext.encode('utf-8')
            padded_plaintext = pad(plaintext_bytes, DES3.block_size)
            ciphertext = cipher.encrypt(padded_plaintext)

            # Base64编码
            return base64.b64encode(ciphertext).decode('utf-8')
        except Exception as e:
            raise ValueError(f"3DES加密失败: {str(e)}")

    @staticmethod
    def des3_decrypt(key: str, iv: str, ciphertext: str) -> str:
        """
        3DES解密

        Args:
            key: Base64编码的密钥(24字节)
            iv: 初始化向量(8字节)
            ciphertext: Base64编码的密文

        Returns:
            解密后的明文
        """
        try:
            # 解码密钥和密文
            key_bytes = base64.b64decode(key)[:24]
            iv_bytes = iv.encode('utf-8')[:8]
            ciphertext_bytes = base64.b64decode(ciphertext)

            # 创建3DES cipher
            cipher = DES3.new(key_bytes, DES3.MODE_CBC, iv_bytes)

            # 解密
            padded_plaintext = cipher.decrypt(ciphertext_bytes)
            plaintext_bytes = unpad(padded_plaintext, DES3.block_size)

            return plaintext_bytes.decode('utf-8')
        except Exception as e:
            raise ValueError(f"3DES解密失败: {str(e)}")

    @staticmethod
    def generate_crc32(data: str) -> int:
        """
        生成CRC32校验和

        Args:
            data: 待计算校验和的数据

        Returns:
            CRC32校验和(无符号整数)
        """
        return zlib.crc32(data.encode('utf-8')) & 0xffffffff

    @staticmethod
    def md5_hash(text: str) -> str:
        """
        MD5哈希(32位大写)

        Args:
            text: 待哈希的文本

        Returns:
            MD5哈希值(32位大写)
        """
        return hashlib.md5(text.encode('utf-8')).hexdigest().upper()

    @staticmethod
    def sha256_hash(text: str) -> str:
        """
        SHA256哈希(64位小写)

        Args:
            text: 待哈希的文本

        Returns:
            SHA256哈希值(64位小写)
        """
        return hashlib.sha256(text.encode('utf-8')).hexdigest().lower()


# 工具函数(兼容旧代码)
def encrypt_aes(key: str, iv: str, plaintext: str) -> str:
    """AES加密的便捷函数"""
    return CryptoUtils.aes_encrypt(key, iv, plaintext)


def decrypt_aes(key: str, iv: str, ciphertext: str) -> str:
    """AES解密的便捷函数"""
    return CryptoUtils.aes_decrypt(key, iv, ciphertext)


def encrypt_3des(key: str, iv: str, plaintext: str) -> str:
    """3DES加密的便捷函数"""
    return CryptoUtils.des3_encrypt(key, iv, plaintext)


def decrypt_3des(key: str, iv: str, ciphertext: str) -> str:
    """3DES解密的便捷函数"""
    return CryptoUtils.des3_decrypt(key, iv, ciphertext)


def generate_sign(data: str) -> int:
    """生成签名(CRC32)的便捷函数"""
    return CryptoUtils.generate_crc32(data)
