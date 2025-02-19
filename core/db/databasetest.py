# core/db/database.py
import os
from pymongo import MongoClient
from pymongo.encryption import ClientEncryption
from pymongo.encryption_options import AutoEncryptionOpts
from pymongo.errors import EncryptionError
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from typing import Optional, Dict, Any

class EncryptionLevel:
    NONE = "none"
    QUERYABLE = "queryable"
    FULL = "full"

class EncryptedField:
    def __init__(self, level: str = EncryptionLevel.FULL, key_id: Optional[bytes] = None):
        self.level = level
        self.key_id = key_id

class MongoDBConnection:
    _instance = None
    _data_key_id = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        # Configuration
        self.uri = os.getenv("mongodb+srv://agangwar0009:rDRC7JFeDYswSlSc@cluster0.hl9mt.mongodb.net", "mongodb://localhost:27017")
        self.db_name = os.getenv("design_pattern_poc", "myapp")
        self.key_vault_db = "encryption"
        self.key_vault_coll = "__keyVault"
        self.key_vault_namespace = f"{self.key_vault_db}.{self.key_vault_coll}"
        self.master_key_path = "master-key.pem"
        
        # Generate or load master key
        self._generate_master_key()
        
        # Configure KMS providers
        self.kms_providers = {
            "local": {
                "key": self._load_master_key()
            }
        }
        
        # Generate data key
        self._generate_data_key()
        
        # Configure auto encryption
        self.auto_encryption_opts = AutoEncryptionOpts(
            kms_providers=self.kms_providers,
            key_vault_namespace=self.key_vault_namespace,
            schema_map=self._build_schema_map(),
            bypass_auto_encryption=False
        )
        
        # Create MongoDB client
        self.client = MongoClient(self.uri, auto_encryption_opts=self.auto_encryption_opts)
        self.db = self.client[self.db_name]
    
    def _generate_master_key(self):
        if not os.path.exists(self.master_key_path):
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            )
            with open(self.master_key_path, "wb") as f:
                f.write(pem)
    
    def _load_master_key(self) -> bytes:
        with open(self.master_key_path, "rb") as f:
            return f.read()
    
    def _generate_data_key(self):
        client_encryption = ClientEncryption(
            self.kms_providers,
            self.key_vault_namespace,
            MongoClient(self.uri),
            self.db.codec_options
        )
        
        # Check if data key already exists
        key_vault = self.client[self.key_vault_db][self.key_vault_coll]
        if key_vault.count_documents({}) == 0:
            self._data_key_id = client_encryption.create_data_key(
                "local",
                key_alt_names=["app-data-key"]
            )
        else:
            key = key_vault.find_one({"keyAltNames": "app-data-key"})
            self._data_key_id = key["_id"]
    
    def _build_schema_map(self) -> Dict[str, Any]:
        return {
            f"{self.db_name}.users": {
                "bsonType": "object",
                "encryptMetadata": {
                    "keyId": [self._data_key_id],
                    "algorithm": "AEAD_AES_256_CBC_HMAC_SHA_512-Deterministic"
                },
                "properties": {
                    "email": {
                        "encrypt": {
                            "bsonType": "string",
                            "algorithm": "AEAD_AES_256_CBC_HMAC_SHA_512-Deterministic"
                        }
                    },
                    "full_name": {
                        "encrypt": {
                            "bsonType": "string",
                            "algorithm": "AEAD_AES_256_CBC_HMAC_SHA_512-Random"
                        }
                    }
                }
            }
        }
    
    def get_collection_with_encryption(self, collection_name: str, model):
        return self.db[collection_name]

    async def close(self):
        self.client.close()

# Singleton instance
mongodb_connection = MongoDBConnection()
def get_db_connection() -> MongoDBConnection:
    return mongodb_connection