def add_include_deleted(stmt, include_deleted: bool):
    if include_deleted:
        stmt = stmt.execution_options(include_deleted=True)
    return stmt
