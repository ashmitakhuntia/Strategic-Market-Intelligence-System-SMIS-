# memory.py
import os
from dotenv import load_dotenv
from hindsight_client import Hindsight

load_dotenv()

client = Hindsight(
    base_url="https://api.hindsight.vectorize.io",
    api_key=os.environ["HINDSIGHT_API_KEY"],
)

BANK_ID = "research-critic-loop"  # you choose this string yourself

client.create_bank(bank_id=BANK_ID)