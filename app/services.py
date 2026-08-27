class ValidationError(ValueError):
    pass


def validate_resource(payload):
    if not isinstance(payload, dict):
        raise ValidationError("JSON body must be an object.")

    name = str(payload.get("name", "")).strip()
    category = str(payload.get("category", "")).strip()
    quantity = payload.get("quantity")

    if not name:
        raise ValidationError("name is required.")
    if not category:
        raise ValidationError("category is required.")

    if isinstance(quantity, bool) or not isinstance(quantity, int):
        raise ValidationError("quantity must be an integer.")
    if quantity < 0:
        raise ValidationError("quantity cannot be negative.")

    return name, category, quantity


def validate_request(payload):
    if not isinstance(payload, dict):
        raise ValidationError("JSON body must be an object.")

    requester = str(payload.get("requester", "")).strip()
    resource_id = payload.get("resource_id")
    quantity = payload.get("quantity")

    if not requester:
        raise ValidationError("requester is required.")
    if isinstance(resource_id, bool) or not isinstance(resource_id, int):
        raise ValidationError("resource_id must be an integer.")
    if resource_id <= 0:
        raise ValidationError("resource_id must be positive.")
    if isinstance(quantity, bool) or not isinstance(quantity, int):
        raise ValidationError("quantity must be an integer.")
    if quantity <= 0:
        raise ValidationError("quantity must be greater than zero.")

    return resource_id, requester, quantity
