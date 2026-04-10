import base64
import sys

if sys.argv[1] is None:
    print("Usage: python encode_icon.py <path_to_image>")
    sys.exit(1)
else:
    with open(sys.argv[1], "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
        print(encoded_string.decode("utf-8"))

