# imghdr.py (custom replacement)

def what(file, h=None):
    # Basic fake format detection using file extension
    if isinstance(file, str):
        if file.endswith(".jpg") or file.endswith(".jpeg"):
            return "jpeg"
        elif file.endswith(".png"):
            return "png"
        elif file.endswith(".gif"):
            return "gif"
        elif file.endswith(".webp"):
            return "webp"
    return None
