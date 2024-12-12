def create_response_body(message, data = {}):
    response_body = {
        "message": message,
        "data": data
    }
    return response_body
