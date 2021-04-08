from common.errors import UBadRequest


def verify_limit_offset(params):
    try:
        limit = int(params.get('limit', 10))
        offset = int(params.get('offset', 0))
        if limit > 100 or limit < 0:
            raise UBadRequest('Limit invalid. Maxinum limit is 100')
        if offset < 0:
            raise UBadRequest('Offset invalid')
        return limit, offset
    except Exception:
        raise UBadRequest('Invalid limit or offset')


def get_limit_from_page(params):
    try:
        page = int(params.get('page', 1))
        per_page = int(params.get('per_page', 10))
    except Exception:
        raise UBadRequest('Invalid limit or offset')
    limit = per_page
    offset = (page - 1) * per_page
    if limit > 100 or limit < 0:
        raise UBadRequest('Limit invalid. Maxinum limit is 100')
    if offset < 0:
        raise UBadRequest('Page info invalid')
    return limit, offset
