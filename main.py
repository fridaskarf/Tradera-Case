import streamlit as st
from streamlit_chat import message
import requests
from build_query import build_query
from read_xml import read_xml
from doc_embedding_store import DocumentEmbeddingStore, FileToEmbed
import itertools
import regex as re

# Embedding our documents
if "doc_store" not in st.session_state:
    doc_store = DocumentEmbeddingStore()
    csv_files = [
        (
            FileToEmbed(
                file_path="./faq.csv",
                source="https://info.tradera.com/",
            ),
            ",",
        ),
        (
            FileToEmbed(
                file_path="./xml_content.csv",
                source="https://info.tradera.com/",
            ),
            ";",
        ),
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

if "links" not in st.session_state:
    links_in_xml = read_xml()
    st.session_state["links"] = links_in_xml
else:
    links_in_xml = st.session_state["links"]

# Init app
st.set_page_config(page_title="Tradera chatbot", page_icon="./tradera_icon.png")

st.header("Tradera Chatbot - Case")
st.markdown("[Tradera](https://tradera.se)")

if "generated" not in st.session_state:
    st.session_state["generated"] = ["Hej! Vad kan jag hjälpa dig med?"]

if "past" not in st.session_state:
    st.session_state["past"] = []


user_input = st.text_input("Skriv frågor här: ", "", key="input")

if user_input:
    output = build_query(
        {
            "inputs": {
                "past_user_inputs": st.session_state.past,
                "generated_responses": st.session_state.generated,
                "text": user_input,
            },
        },
        doc_store,
        links_in_xml,
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
                message(
                    past,
                    is_user=True,
                    key=str(i) + "_user",
                    avatar_style="thumbs",
                )
            if generated:
                message(
                    generated,
                    key=str(i),
                    seed="Willow",
                    avatar_style="bottts",
                )
        else:
            if generated:
                message(generated, key=str(i), seed="Willow", avatar_style="bottts")
            if past:
                message(
                    past,
                    is_user=True,
                    key=str(i) + "_user",
                    avatar_style="thumbs",
                )
