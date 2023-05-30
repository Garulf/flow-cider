def get_artwork(url: str, width: int = 32, height: int = 32) -> str:
    return url.format(w=width, h=height)
