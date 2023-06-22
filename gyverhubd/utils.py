
def parse_url(url: str) -> tuple[str, str | None, str | None, str | None, str | None]:
    prefix, *url = url.split('/', maxsplit=4)
    cmd = clid = did = name = None

    if url:
        did, *url = url
    if len(url) == 1:
        print(prefix, url)
        raise ValueError("Invalid data!")
        # return prefix, clid, did, cmd, name
    if url:
        clid, cmd, *url = url
    if url:
        name, = url
    return prefix, clid, did, cmd, name


def generate_did():
    raise ValueError("Missing did and generating not supported!")


def response(typ: str, **kwargs):
    kwargs['type'] = typ
    return kwargs
