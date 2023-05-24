from langchain.schema import Document
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from dataclasses import dataclass, field

from typing import List, Dict
import os
import pandas as pd
import yaml
from yaml import SafeLoader
import requests
from bs4 import BeautifulSoup

from read_xml import read_xml, save_html_content


@dataclass
class FileToEmbed:
    file_path: str
    source: str = None
    args: dict = field(default_factory=dict)


class DocumentEmbeddingStore:
    def __init__(self):
        with open("./secrets.yml", "r") as credentials_file:
            secrets = yaml.load(credentials_file, SafeLoader)
            os.environ["OPENAI_API_KEY"] = secrets["key"]

        self.vector_store = Chroma(embedding_function=OpenAIEmbeddings())

    def load_csv_file(self, file: FileToEmbed, sep: str) -> List[Document]:
        try:
            df = pd.read_csv(file.file_path, on_bad_lines="skip", sep=sep)
        except:
            save_html_content(read_xml()[3:])
            df = pd.read_csv(file.file_path, on_bad_lines="skip", sep=sep)

        documents = []
        for _, row in df.iterrows():
            title = str(row["title"])
            content = str(row["content"])
            source = row.get("source", "https://info.tradera.com/")
            full_content = title + " " + content
            document = Document(
                page_content=full_content,
                metadata=dict(
                    title=title,
                    content=content,
                    source=source,
                ),
            )
            documents.append(document)

        return documents

    def embed_documents(self, documents: List[Document]):
        self.vector_store = self.vector_store.from_documents(
            documents=documents, embedding=OpenAIEmbeddings()
        )

    def get_relevant_documents(self, query: str) -> List[Document]:
        relevant_documents = self.vector_store.similarity_search(query=query, k=7)
        return relevant_documents
