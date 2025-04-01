import uuid
# uuid validation
def is_valid_uuid(value):
    try:
        uuid.UUID(str(value))  # Vérifie la conversion
        return True
    except ValueError:
        return False
