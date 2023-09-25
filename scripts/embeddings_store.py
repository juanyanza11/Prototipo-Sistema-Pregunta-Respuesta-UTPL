# proyecto_embeddings/embedding_pinecone/embeddings.py
import os
from langchain.document_loaders import TextLoader
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import pinecone
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Pinecone
from langchain.embeddings import CohereEmbeddings
from dotenv import load_dotenv
from langchain.document_loaders.csv_loader import CSVLoader

def almacenar_embeddings(index, directorio):
    load_dotenv()

    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
    COHERE_API_KEY = os.getenv("COHERE_API_KEY")
    # HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")
    
    loader = CSVLoader(file_path=os.path.abspath(directorio), csv_args={'delimiter': '|'}, encoding='utf-8')
    print(os.path.abspath(directorio))

    # Carga todos los rows del csv como documentos
    documentos = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
    docs = text_splitter.split_documents(documentos)
    print(f"Se obtuvieron {len(docs)} documentos.")

    # 4096 Dimensiones
    cohere = CohereEmbeddings(model="embed-english-v2.0", cohere_api_key = COHERE_API_KEY) 
    
    # Inicializar PineCone
    pinecone.init(
        api_key=PINECONE_API_KEY,
        environment=PINECONE_ENVIRONMENT
    )

    # Subir embeddings a pinecone con el nombre de la variable index, el objeto doocsearch esta listo para buscar vectores similares
    Pinecone.from_texts([t.page_content for t in docs], cohere, index_name=index)
