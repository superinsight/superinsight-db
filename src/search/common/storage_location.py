from enum import Enum
class StorageLocation(Enum):
    MEMORY_CACHE = "MEMORY_CACHE"
    LOCAL_DISK = "LOCAL_DISK"
    CLOUD_DISK = "CLOUD_DISK"