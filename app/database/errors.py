class EntityDoesNotExist(Exception):
    """Raised when entity was not found in database."""


class ConflictWhenInsert(Exception):
    """Raised when insert new entity in database raising a unique violation or exclusion constraint violation error."""


class ConflictWhenUpdate(Exception):
    """Raised when update entity in database raising a unique violation or exclusion constraint violation error."""


class ConflictWhenDelete(Exception):
    """Raised when delete entity in database raising a unique violation or exclusion constraint violation error."""


class ResponsePageNotExist(Exception):
    """Raised when requested page was not found in query results."""
