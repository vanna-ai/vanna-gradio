import os

from dotenv import load_dotenv
from vanna.remote import VannaDefault


def setup_vanna(vn):
    load_dotenv()

    if "EMAIL" in os.environ:
        vn = VannaDefault(model="chinook", api_key=vn.get_api_key(os.getenv("EMAIL")))
    elif "VANNA_API_KEY" in os.environ:
        vn = VannaDefault(
            model="chinook", api_key=vn.get_api_key(os.getenv("VANNA_API_KEY"))
        )

    vn.connect_to_sqlite("Chinook.sqlite")

    return vn
