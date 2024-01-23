import os
from typing import List, Optional, Dict
from marshmallow_dataclass import class_schema
from dataclasses import dataclass
import yaml


@dataclass
class NetworkSettings:
    bot_token: str
    host: Optional[str]
    port: Optional[str]
    user: Optional[str]
    password: Optional[str]
    endpoint: Optional[str]
    address: Optional[str]
    decimals: Optional[int]


@dataclass
class Settings:
    NETWORKS: Dict[str, NetworkSettings]
    BALANCE_CHECKER_TIMEOUT: int
    WARNING_LEVELS: List[int]
    REDIS_HOST: str
    REDIS_PORT: int
    
    
config_path = "/../config.yaml"
if os.getenv("IS_TEST", False):
    config_path = "/../config.example.yaml"

with open(os.path.dirname(__file__) + config_path) as f:
    config_data = yaml.safe_load(f)

config: Settings = class_schema(Settings)().load(config_data)
