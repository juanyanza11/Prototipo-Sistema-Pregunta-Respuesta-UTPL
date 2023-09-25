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


def almacenar_embeddings(index, directorio):
    load_dotenv()

    # Crea una instancia de DirectoryLoader
    loader = DirectoryLoader(os.path.abspath(directorio), glob="./*.txt", show_progress=True)

    # Obtén todos los documentos en el directorio
    documentos = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
    docs = text_splitter.split_documents(documentos)

    os.environ["HUGGINGFACEHUB_API_TOKEN"] = "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"
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
    COHERE_API_KEY = os.getenv("COHERE_API_KEY")
    # HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")

    # embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2') # 384 Dimensiones
    cohere = CohereEmbeddings(model="embed-english-v2.0", cohere_api_key = COHERE_API_KEY) # 4096 Dimensiones
    print(PINECONE_API_KEY)
    print(PINECONE_ENVIRONMENT)
    
    # Inicializar PineCone
    pinecone.init(
        api_key=PINECONE_API_KEY,
        environment=PINECONE_ENVIRONMENT
    )

    # Subir embeddings a pinecone con el nombre de la variable index, el objeto doocsearch esta listo para buscar vectores similares
    docsearch = Pinecone.from_texts([t.page_content for t in docs], cohere, index_name=index)
