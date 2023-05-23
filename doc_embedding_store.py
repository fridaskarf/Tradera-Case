from langchain.schema import Document
from langchain.indexes.vectorstore import (
    VectorstoreIndexCreator,
    VectorStoreIndexWrapper,
)
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from dataclasses import dataclass, field

from typing import List, Dict
import os
from langchain.llms.openai import OpenAI
import pandas as pd
import yaml
from yaml import SafeLoader
import requests
from bs4 import BeautifulSoup


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

    def load_csv_file(self, file: FileToEmbed) -> List[Document]:
        df = pd.read_csv(file.file_path)

        documents = []
        for _, row in df.iterrows():
            title = str(row["title"])
            content = str(row["content"])
            full_content = title + " " + content
            document = Document(
                page_content=full_content,
                metadata=dict(
                    title=title,
                    content=content,
                    source="https://info.tradera.com/",
                ),
            )
            documents.append(document)

        return documents

    def load_html_content(self, file: FileToEmbed) -> dict:
        response = requests.get(file.file_path)
        soup = BeautifulSoup(response.content, "html.parser")
        documents = {}

        for paragraph in soup.find_all("p"):
            content = paragraph.text
            source = file.file_path
            document = Document(
                page_content=content,
                metadata=dict(
                    title="",
                    content=content,
                    source=source,
                ),
            )
            documents[content] = document

        return documents

    def embed_csv_file(self, file: FileToEmbed):
        documents = self.load_csv_file(file=file)
        # uses Chroma by default
        self.vector_store = self.vector_store.from_documents(documents=documents)

    def embed_documents(self, documents: List[Document]):
        self.vector_store = self.vector_store.from_documents(documents=documents)

    def get_relevant_documents(self, query: str) -> List[Document]:
        relevant_documents = self.vector_store.similarity_search(query=query, k=7)
        return relevant_documents
