import streamlit as st
from streamlit_chat import message
import requests
from query_gpt import query_gpt
from doc_embedding_store import DocumentEmbeddingStore, FileToEmbed
import itertools

# Embedding our documents
if "doc_store" not in st.session_state:
    doc_store = DocumentEmbeddingStore()
    csv_files = [
        (FileToEmbed(
            file_path="./faq.csv",
            source="https://info.tradera.com/",
        ), ","),
        (FileToEmbed(
            file_path="./xml_content.csv",
            source="https://info.tradera.com/",
        ), ";")
    ]

    csv_docs = []
    for file, sep in csv_files:
        csv_docs += doc_store.load_csv_file(file, sep)
    print("done loading")
    doc_store.embed_documents(csv_docs)
    print("done embedding")
    st.session_state["doc_store"] = doc_store
else:
    doc_store = st.session_state["doc_store"]


# Init app
st.set_page_config(page_title="Tradera chatbot", page_icon="./tradera_icon.png")

st.header("Tradera Chatbot - Case")
st.markdown("[Tradera](https://tradera.se)")

if "generated" not in st.session_state:
    st.session_state["generated"] = ["Hej! Vad kan jag hjälpa dig med?"]

if "past" not in st.session_state:
    st.session_state["past"] = []

context = "Du är Traderas chatbot och kan endast svara på frågor rörande Tradera. "
context += "Du måste svara på samma språk som användaren använder. "
context += "Om svaret på frågan inte finns i chatthistoriken, säg att du inte har svaret på frågan och källhänvisa till hemsidan https://info.tradera.com/"
context += "Länka aldrig till en websida som du inte explicit ombeds att källhänvisa till"

def query(q: dict) -> dict:
    # parse query dict
    user_input = q.get("inputs").get("text")
    past_user_inputs = q.get("inputs").get("past_user_inputs")
    generated_responses = q.get("inputs").get("generated_responses")

    #response = agent.run(user_input)

    relevant_documents = doc_store.get_relevant_documents(query=user_input)
    messages = [{"role": "system", "content": context}]
    print("found relevant documents")
    for resp, user in itertools.zip_longest(
        generated_responses, past_user_inputs, fillvalue=""
    ):
        messages.append({"role": "assistant", "content": resp})
        messages.append({"role": "user", "content": user})

    for doc in relevant_documents:
        content = doc.metadata["content"].replace("\xa0", " ").replace("&amp", "&")
        title = doc.metadata["title"].replace("\xa0", " ").replace("&amp", "&")

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
        else:
            messages.append(
                {
                    "role": "system",
                    "content": f"Om frågan är relaterat till följande rubrik, '{content}',\
                      lägg till en källhänvisning till svaret genom att skriva 'Läs mer på {doc.metadata['source']}'"
                }
            )

    messages.append({"role": "user", "content": user_input})
    print(messages)
    response = query_gpt(messages=messages)
    print("query done")
    return {"generated_text": str(response)}


user_input = st.text_input("Skriv frågor här: ", "", key="input")

if user_input:
    output = query(
        {
            "inputs": {
                "past_user_inputs": st.session_state.past,
                "generated_responses": st.session_state.generated,
                "text": user_input,
            },
        }
    )

    st.session_state.past.append(user_input)
    st.session_state.generated.append(output["generated_text"])

if st.session_state["generated"]:
    conversation = itertools.zip_longest(
        st.session_state["generated"], st.session_state["past"]
    )

    bot_started = len(st.session_state["generated"]) > len(st.session_state["past"])

    conversation = list(conversation)[::-1]
    for i, (generated, past) in enumerate(conversation):
        if bot_started:
            if past:
                message(past, is_user=True, key=str(i) + "_user")
            if generated:
                message(generated, key=str(i))
        else:
            if generated:
                message(generated, key=str(i))
            if past:
                message(past, is_user=True, key=str(i) + "_user")
