from urllib.parse import quote, urlparse


def encode_url(url):
    if not url:
        return url
    url_parser = urlparse(url)
    url_parser = url_parser._replace(
        path=quote(url_parser.path),
        params=quote(url_parser.params),
        query=quote(url_parser.query),
        fragment=quote(url_parser.fragment)
    )
    return url_parser.geturl()
