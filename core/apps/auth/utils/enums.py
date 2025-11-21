from enum import Enum


class PermissionActions(str, Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "DELETE"
    FORCE_DELETE = "force_delete"
    RESTORE = "restore"
    LOGS = "logs"
    MANAGE = "management"
    COPY = "copy"
    EXPORT = "export"
