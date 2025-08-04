from bson import ObjectId

def to_object_id(id_str: str) -> ObjectId:
    """Converts a string ID to ObjectId."""
    try:
        return ObjectId(id_str)
    except Exception:
        raise ValueError(f"Invalid ObjectId format: {id_str}")

def to_string_id(obj_id: ObjectId) -> str:
    """Converts an ObjectId to a string ID."""
    return str(obj_id)
