import streamlit as st
from streamlit_chat import message
import requests
from query_gpt import query_gpt
from add_context import add_faq_context
from doc_embedding_store import DocumentEmbeddingStore, FileToEmbed
import itertools


doc_store = DocumentEmbeddingStore()
files = [FileToEmbed(file_path="./faq.csv", source="https://info.tradera.com/", args={'fieldnames': ['title', 'content']})]
for file in files:
    doc_store.embed_csv_file(file=file)

st.set_page_config(page_title="Streamlit Chat - Demo", page_icon=":robot:")

st.header("Streamlit Chat - Demo")
st.markdown("[Tradera](https://tradera.se)")

if "generated" not in st.session_state:
    st.session_state["generated"] = ["Hej! Vad kan jag hjälpa dig med?"]

if "past" not in st.session_state:
    st.session_state["past"] = []

bot_first = st.session_state["generated"] > st.session_state["past"]

context = "Du är Traderas chatbot och kan endast svara på frågor rörande Tradera. "
context += "Du måste svara på samma språk som användaren använder. " 
context += "Om svaret på frågan inte finns i chatthistoriken, referera till hemsidan https://info.tradera.com/"

def query(q: dict) -> dict:
    # parse query dict
    user_input = q.get("inputs").get("text")
    past_user_inputs = q.get("inputs").get("past_user_inputs")
    generated_responses = q.get("inputs").get("generated_responses")

    relevant_documents = doc_store.get_relevant_documents(query=user_input)
    messages = [{"role": "system", "content":context}]
    for user, resp in itertools.zip_longest(generated_responses, past_user_inputs, fillvalue=""):
        messages.append({"role": "user", "content": user})
        messages.append({"role": "assistant", "content": resp})
    for doc in relevant_documents:
        messages.append({"role": "user", "content": doc.metadata["title"]})
        messages.append({"role": "assistant", "content": doc.metadata["content"]})
    
    messages.append({"role": "user", "content": user_input})
    print(messages)
    response = query_gpt(messages=messages)

    return {"generated_text": response}


def get_text():
    input_text = st.text_input("Skriv frågor här: ", "", key="input")
    return input_text


user_input = get_text()

if user_input:
    output = query(
        {
            "inputs": {
                "past_user_inputs": st.session_state.past,
                "generated_responses": st.session_state.generated,
                "text": user_input,
            },
            "parameters": {"repetition_penalty": 1.33},
        }
    )

    st.session_state.past.append(user_input)
    st.session_state.generated.append(output["generated_text"])

if st.session_state["generated"]:
    
    conversation = itertools.zip_longest(st.session_state["generated"], st.session_state["past"])
    if len(st.session_state["generated"]) > len(st.session_state["past"]):
        # more generated than past -> conversation started with generated response
        bot_started = True
    else:
        bot_started = False
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
