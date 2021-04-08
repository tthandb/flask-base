class UPermissionDenied(Exception):
    pass


class UNotFound(Exception):
    """ Raise when not found upinus resource
    """
    pass


class UUnprocessableEntity(Exception):
    pass


class UConflict(Exception):
    pass


class UKafkaProduceError(Exception):
    pass


class UBadRequest(Exception):
    pass
