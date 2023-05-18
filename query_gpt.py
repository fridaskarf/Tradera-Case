import yaml
from yaml.loader import SafeLoader
import openai
from add_context import add_faq_context


def query_gpt(messages: list) -> dict:
    with open("./secrets.yml") as credentials_file:
        secrets = yaml.load(credentials_file, SafeLoader)

    openai.organization = "org-wAmGkOif5fmluOzslipK8k9B"
    openai.api_key = secrets["key"]

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=1024,
        temperature=0.8,
    )

    return completion.get("choices")[0].get("message").get("content")


# messages = add_faq_context()
# message = [
#     {
#         "role": "user",
#         "content": "Vad är Samfrakt?",
#     }
# ]

# print(query_gpt(messages=messages + message))
