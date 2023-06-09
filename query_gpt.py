import yaml
from yaml.loader import SafeLoader
import openai
import os
from openai import error


def query_gpt(messages: list, max_tokens: int = 1024) -> dict:
    with open("./secrets.yml") as credentials_file:
        secrets = yaml.load(credentials_file, SafeLoader)

    openai.organization = secrets["org"]
    openai.api_key = secrets["key"]
    os.environ["OPENAI_API_KEY"] = secrets["key"]

    n_retries = 10
    retry = 0
    while retry <= n_retries:
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.4,
            )
            retry = 11
            return_msg = completion.get("choices")[0].get("message").get("content")
        except error.APIError:
            retry += 1
            return_msg = (
                "Det har uppkommit ett server-fel. Vänligen försök igen senare."
            )
        except error.RateLimitError:
            retry += 1
            return_msg = (
                "Servern är för närvarande överbelastad. Vänligen försök igen senare."
            )

    return return_msg
