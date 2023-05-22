from langchain.schema import Document
from langchain.indexes.vectorstore import VectorstoreIndexCreator, VectorStoreIndexWrapper
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.vectorstores import Chroma
from langchain.embeddings  import OpenAIEmbeddings
from dataclasses import dataclass, field
import typing
import os
from langchain.llms.openai import OpenAI
import pandas as pd
import yaml
from yaml import SafeLoader


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
        self.file_source_mapping: dict[str,str] = {}
        # check if OpenAI API key is set
        

    def load_csv_file(self, file: FileToEmbed) -> list[Document]:

        df = pd.read_csv(file.file_path)
        
        documents = []
        for _, row in df.iterrows():
            title = str(row["title"])
            content = str(row["content"])
            content = title + " " + content
            document = Document(page_content=content, metadata=dict(title=title, content=content, source="https://info.tradera.com/"))
            documents.append(document)
            
        #loader = CSVLoader(file_path=file.file_path, csv_args=file.args, encoding="utf-8")
        #documents = loader.load()

        return documents

    def embed_csv_file(self, file: FileToEmbed):
        documents = self.load_csv_file(file=file)
        # uses Chroma by default
        self.vector_store = self.vector_store.from_documents(documents=documents)

    def get_relevant_documents(self, query: str) -> list[Document]:
        relevant_documents = self.vector_store.similarity_search(query=query, k=5)
        return relevant_documents



        """
        res = self.vector_store.query_with_sources(question=query, llm=OpenAI(model_name="gpt-3.5-turbo"))

        answer = res["answer"]
        sources = res["sources"]

        if sources == "N/A":
            return answer

        if type(sources) == str:
            sources = [sources]

        
        links = ""
        if len(sources) > 1:
            links = f"\n\nLäs mer på: {', '.join(sources)}"
        if len(sources) == 1:
            if sources[0]:
                links = f"\n\nLäs mer på: {sources[0]}"
        return answer+links
        """

