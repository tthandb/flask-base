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


class InvalidParamerters(Exception):
    pass


class OtherPaymentProcessing(Exception):
    pass


class OrderPaidError(Exception):
    pass


class UTimeoutError(Exception):
    pass
