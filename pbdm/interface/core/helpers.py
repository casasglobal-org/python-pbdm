def merge_parameters(parameters: dict, key: str, new_parameters: dict) -> dict:
    if not isinstance(new_parameters, dict):
        raise TypeError(f"New parameters must be provided as a dict; received {type(new_parameters)}")
    if not isinstance(parameters, dict):
        raise TypeError(f"Target object must be a dict; received {type(parameters)}")
    dict_at_key = parameters.setdefault(key, {})
    dict_at_key.update(new_parameters)
    parameters[key] = dict_at_key
    return parameters