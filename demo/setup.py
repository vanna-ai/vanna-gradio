import os

from dotenv import load_dotenv
from vanna.remote import VannaDefault


def setup_vanna(vn):
    load_dotenv()

    if "EMAIL" in os.environ:
        vn = VannaDefault(model="chinook", api_key=vn.get_api_key(os.getenv("EMAIL")))
        vn.connect_to_sqlite("https://vanna.ai/Chinook.sqlite")
    elif "VANNA_API_KEY" in os.environ:
        vn = VannaDefault(
            model="chinook", api_key=vn.get_api_key(os.getenv("VANNA_API_KEY"))
        )
        vn.connect_to_sqlite("https://vanna.ai/Chinook.sqlite")
    else:
        vn = VannaDefault(model="chinook", api_key=None)
        vn.connect_to_sqlite("Chinook.sqlite")

        print(
            "WARNING: Neither EMAIL nor VANNA_API_KEY were found in the '.env' file. Setting api_key=None."
        )

    return vn
