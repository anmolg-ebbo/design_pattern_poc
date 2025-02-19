import asyncio
import os
import logging
from contextlib import asynccontextmanager
from enum import Enum
from threading import Lock
from typing import Dict, Type

from bson.codec_options import CodecOptions
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from pymongo.encryption import AutoEncryptionOpts, ClientEncryption
from pydantic import BaseModel, Field

from core.config import config

logger = logging.getLogger(__name__)

class EncryptionLevel(str, Enum):
    NONE = "none"
    STANDARD = "standard"
    QUERYABLE = "queryable"

def EncryptedField(level: EncryptionLevel = EncryptionLevel.STANDARD, **kwargs):
    """Returns a Pydantic Field with encryption metadata"""
    return Field(..., metadata={"encrypt": True, "encryption_level": level}, **kwargs)

class MongoDBConnection:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(MongoDBConnection, cls).__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        with self._lock:
            if not self._initialized:
                try:
                    self.client = None
                    self.encryption_client = None
                    self.key_vault_client = None
                    self._client_pool = {}
                    
                    self._setup_encryption()
                    self._initialized = True
                    logger.info("MongoDB connection initialized successfully")
                except Exception as e:
                    logger.error(f"Failed to initialize MongoDB connection: {str(e)}")
                    self._initialized = False  # Ensure it remains uninitialized on failure
                    raise

    def _setup_encryption(self):
        """Set up encryption configurations and create master key if needed."""
        try:
            logger.debug(f"Setting up MongoDB connection with URI: {config.MONGO_URI}")
            self.key_vault_client = MongoClient(config.MONGO_URI)
            self.key_vault_db = self.key_vault_client['encryption']
            self.key_vault_coll = self.key_vault_db['key_vault']
            
            master_key_path = Path('config/master_key.bin')
            
            with self._lock:
                if not master_key_path.exists():
                    logger.info("Master key not found, creating new one")
                    master_key = os.urandom(96)
                    master_key_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(master_key_path, 'wb') as f:
                        f.write(master_key)
                    self.local_master_key = master_key
                else:
                    logger.debug("Loading existing master key")
                    with open(master_key_path, 'rb') as f:
                        self.local_master_key = f.read()

            self.kms_providers = { 'local': { 'key': self.local_master_key } }

            logger.debug("Creating client encryption instance")
            self.encryption_client = ClientEncryption(
                self.kms_providers,
                'encryption.key_vault',
                self.key_vault_client,
                CodecOptions()
            )
            logger.debug("Encryption setup completed successfully")
        except Exception as e:
            logger.error(f"Error during encryption setup: {str(e)}")
            raise
    
    def _build_schema_map(self, model: Type[BaseModel]) -> Dict:
        """Build MongoDB schema map from Pydantic model with encryption metadata"""
        try:
            schema_map = { "bsonType": "object", "properties": {} }
            
            for field_name, field in model.model_fields.items():  # Use model_fields in Pydantic V2
                encrypt_meta = field.metadata.get("encrypt") if field.metadata else None
                encryption_level = field.metadata.get("encryption_level") if field.metadata else EncryptionLevel.STANDARD

                if encrypt_meta:
                    schema_map["properties"][field_name] = {
                        "encrypt": {
                            "bsonType": "string",
                            "algorithm": "AEAD_AES_256_CBC_HMAC_SHA_512-Random" if encryption_level == EncryptionLevel.STANDARD
                                    else "AEAD_AES_256_CBC_HMAC_SHA_512-Deterministic"
                        }
                    }
            
            return schema_map
        except Exception as e:
            logger.error(f"Error building schema map: {str(e)}")
            raise

    @asynccontextmanager
    async def get_collection_with_encryption(self, collection_name: str, model: Type[BaseModel]):
        """Async context manager for getting encrypted collection"""
        try:
            schema_map = self._build_schema_map(model)
            db_name = config.MONGO_URI.rsplit('/', 1)[-1]
            client_key = f"{collection_name}_{model.__name__}"
            
            logger.debug(f"Getting encrypted collection: {collection_name} for model: {model.__name__}")
            
            with self._lock:
                if client_key not in self._client_pool:
                    logger.debug(f"Creating new client for {client_key}")
                    auto_encryption_opts = AutoEncryptionOpts(
                        kms_providers=self.kms_providers,
                        key_vault_namespace='encryption.key_vault',
                        schema_map={ f"{db_name}.{collection_name}": schema_map },
                    )
                    new_client = AsyncIOMotorClient(
                        config.MONGO_URI,
                        auto_encryption_opts=auto_encryption_opts,
                        maxPoolSize=100,
                        minPoolSize=10,
                    )
                    self._client_pool[client_key] = new_client  # Assign new client before releasing lock

            client = self._client_pool[client_key]  # Use the assigned client outside the lock
            collection = client[db_name][collection_name]
            yield collection

        except Exception as e:
            logger.error(f"Error getting collection with encryption: {str(e)}")
            raise

    async def close(self):
        """Close all MongoDB connections."""
        logger.info("Closing all MongoDB connections")
        with self._lock:
            for client in self._client_pool.values():
                asyncio.create_task(client.close())
            
            if self.key_vault_client:
                self.key_vault_client.close()
            
            if self.encryption_client:
                self.encryption_client.close()
            
            self._client_pool.clear()
            logger.debug("All MongoDB connections closed")
