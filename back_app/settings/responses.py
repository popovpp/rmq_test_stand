from back_app.settings.schema import Error, ErrorNotFound, ErrorAction, ErrorUnauthorized

response_401 = {
    'description': 'Unauthorized',
    'model': ErrorUnauthorized
}

response_404 = {
    'description': 'Not found error',
    'model': ErrorNotFound
}

response_422 = {
    'description': 'Validation Error',
    'model': Error
}

response_501 = {
    'description': 'Action error',
    'model': ErrorAction
}