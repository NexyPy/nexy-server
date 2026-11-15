from nexy.http import PlainTextResponse

TEXT = b"Hello, World!"


async def GET():
    return PlainTextResponse(TEXT)
