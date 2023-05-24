from query_gpt import query_gpt
import itertools
from doc_embedding_store import DocumentEmbeddingStore

CONTEXT = "Du är Traderas chatbot och kan endast svara på frågor rörande Tradera. "
CONTEXT += "Du måste svara på samma språk som användaren använder. "
CONTEXT += "Om svaret på frågan inte finns i chatthistoriken, säg att du inte har svaret på frågan och källhänvisa till hemsidan https://info.tradera.com/."
CONTEXT += "Använd dig endast av länkar som ligger i chatthistoriken när du länkar till en hemsida."


def build_query(
    q: dict, doc_store: DocumentEmbeddingStore, available_sources: list
) -> dict:
    # parse query dict
    user_input = q.get("inputs").get("text")
    past_user_inputs = q.get("inputs").get("past_user_inputs")
    generated_responses = q.get("inputs").get("generated_responses")

    relevant_documents = doc_store.get_relevant_documents(query=user_input)
    messages = []

    print("found relevant documents")
    for doc in relevant_documents:
        content = doc.metadata["content"].replace("\xa0", " ").replace("&amp", "&")
        title = doc.metadata["title"].replace("\xa0", " ").replace("&amp", "&")
        source = doc.metadata.get("source")
        if source is not None:
            content += f" Källa: {source}."

        if doc.metadata["title"]:
            messages.append(
                {
                    "role": "user",
                    "content": title,
                }
            )

            if len(content) > 1000:
                split_doc = content.split(". ")
                messages.append(
                    {
                        "role": "assistant",
                        "content": split_doc[0]
                        .replace("\xa0", " ")
                        .replace("&amp", "&")
                        + ".",
                    }
                )
                for text in split_doc[1:]:
                    messages.append(
                        {
                            "role": "system",
                            "content": text.replace("\xa0", " ").replace("&amp", "&")
                            + ".",
                        }
                    )
            else:
                messages.append(
                    {
                        "role": "assistant",
                        "content": content,
                    }
                )

    for resp, user in itertools.zip_longest(
        generated_responses, past_user_inputs, fillvalue=""
    ):
        messages.append({"role": "assistant", "content": resp})
        messages.append({"role": "user", "content": user})

    messages.append({"role": "system", "content": CONTEXT})
    messages.append({"role": "user", "content": user_input})
    print(messages)

    response = query_gpt(messages=messages)
    print(response)

    response = check_links(response, user_input, available_sources)
    print("query done")

    return {"generated_text": str(response)}


def check_links(response, user_input, links_in_xml):
    response_split = response.split()

    links_in_query = [
        (idx, item)
        for idx, item in enumerate(response_split)
        if item.startswith("https:")
    ]
    for idx, link in links_in_query:
        if link.strip(".") not in links_in_xml:
            pages_in_xml = [
                item.replace("https://info.tradera.com/", "") for item in links_in_xml
            ]

            q = f"Du gav följande länk '{link}' till följande fråga '{user_input}', men den länken är inte giltig. "
            q += f"Snälla välj en av sidorna på https://info.tradera.com/ som finns med i denna lista istället {str(pages_in_xml)}."
            link_response = query_gpt(
                messages=[
                    {
                        "role": "user",
                        "content": q,
                    }
                ],
                max_tokens=200,
            ).split()
            print(link_response)
            links_in_response = [
                item for item in link_response if item.startswith("https:")
            ]
            if len(links_in_response) > 0:
                correct_links_in_response = []
                for link in links_in_response:
                    if link in links_in_xml:
                        correct_links_in_response.append(link)
                if len(correct_links_in_response) > 0:
                    new_link = ", ".join(correct_links_in_response)
                else:
                    new_link = "https://info.tradera.com/"
            else:
                new_link = "https://info.tradera.com/"

            response_split[idx] = new_link
            print(f"replaced incorrect link {link} with {new_link}")

    return " ".join(response_split)
