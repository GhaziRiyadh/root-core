from enum import Enum


class PermissionActions(str, Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    FORCE_DELETE = "force_delete"
    RESTORE = "restore"
    LOGS = "logs"
    MANAGE = "manage"
    COPY = "copy"
    EXPORT = "export"
