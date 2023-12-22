def model_to_dict(instance):
    """Convert a Django model instance to a dictionary"""
    model_dict = {}
    for field in instance._meta.fields:
        field_name = field.name
        field_value = getattr(instance, field_name)
        model_dict[field_name] = field_value
    return model_dict
