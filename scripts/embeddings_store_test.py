import os
import uuid
from dotenv import load_dotenv
import pinecone
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import CohereEmbeddings
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Pinecone

def obtener_topic(row):
    # Separar la cadena 'page_content' y 'metadata' usando '\n'
    page_content, metadata_str = row.page_content.split('\n', 1)

    # Parsear la cadena 'metadata' a un diccionario
    metadata = {}
    for line in metadata_str.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            metadata[key.strip()] = value.strip()

    # Obtener el valor de 'Topic' o establecer 'General' si no está presente
    topic = metadata.get('Topic', 'General')
    
    if not topic.strip():
        topic = 'General'
    
    print("TOPIC ----->", topic)
    return topic

def almacenar_embeddings(index, archivo_csv):
    load_dotenv()

    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
    COHERE_API_KEY = os.getenv("COHERE_API_KEY")

    # Inicializar PineCone
    pinecone.init(
        api_key=PINECONE_API_KEY,
        environment=PINECONE_ENVIRONMENT
    )

    # Cargar el archivo CSV
    loader = CSVLoader(file_path=os.path.abspath(archivo_csv), csv_args={'delimiter': '|'}, encoding='utf-8')
    print(f"Cargando CSV desde {os.path.abspath(archivo_csv)}...")

    # Cargar todos los documentos desde el archivo CSV
    documentos = loader.load()

    # Inicializar el text splitter
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)

    # Inicializar Hugging Face Embeddings
    hf_embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
    
    # Inicializar Pinecone Index
    pinecone_index = pinecone.Index(index_name=index)

    # Procesar cada fila del CSV y obtener los embeddings
    for row in documentos:
        # Obtener el campo "Topic" y la metadata
        topic = obtener_topic(row)
        
        # Dividir el contenido del texto en fragmentos
        content_fragments = text_splitter.split_text(row.page_content)
        
        # Generar embeddings para cada fragmento 4096
        cohere = CohereEmbeddings(model="embed-english-v2.0", cohere_api_key = COHERE_API_KEY) 
        # embeddings = hf_embeddings.embed_documents(content_fragments)
        embeddings = cohere.embed_documents(content_fragments)
        
        # Agregar los embeddings y los identificadores a las listas
        for fragment, embedding in zip(content_fragments, embeddings):
            metadata = {'topic': topic}
            try:
                pinecone_index.upsert(vectors=[(str(uuid.uuid4()), embedding, metadata)])
                print(f"Embedding almacenado para '{row.page_content}' (Fragmento: '{fragment}').")
            except Exception as e:
                print(f"Error al actualizar el índice '{index}': {str(e)}")