import os
import pandas as pd
from langchain.text_splitter import RecursiveCharacterTextSplitter
import pinecone
from dotenv import load_dotenv
from langchain.embeddings import CohereEmbeddings
import matplotlib.pyplot as plt
import numpy as np
from langchain.vectorstores import Pinecone


def almacenar_embeddings(index, directorio):
    load_dotenv()

    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
    # COHERE_API_KEY = os.getenv("COHERE_API_KEY")

    # Use pandas to load the CSV file
    df = pd.read_csv(os.path.abspath(directorio), delimiter='|', encoding='utf-8',
                     names=["Pagina", 'Topic', "Contenido", "Fecha_Modificacion"])

    # Extract the 'Contenido' column as a list of documents (strings)
    documentos = df['Contenido'].tolist()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200, chunk_overlap=0)

    # Split the documents into chunks
    chunks = [text_splitter.split_text(doc) for doc in documentos[1:]]

    # Flatten the list of chunks
    chunks_flat = [chunk for sublist in chunks for chunk in sublist]

    # cohere = CohereEmbeddings(model="embed-english-v2.0", cohere_api_key = COHERE_API_KEY) <--- Descomentar instanciar el modelo de Cohere

    total_chunks = 0

    data_hist = []
    count = 0

    for c in chunks_flat:
        count += 1 if len(c) >= 1199 else 0
        data_hist.append(len(c))
        print(f'Chunk de {len(c)} caracteres')
        total_chunks += len(c)
        print(c)
        print('-' * 150)

    print(f"Total de caracteres: {total_chunks}")
    print(f"Media de chunks: {total_chunks/len(chunks_flat)}")
    print(f"Se obtuvieron {len(chunks_flat)} chunks.")
    print(f"Se obtuvieron {count} chunks superiores o iguales a 1199.")

    plt.hist(data_hist, bins='auto')
    plt.show()

    # Initialize PineCone
    pinecone.init(
        api_key=PINECONE_API_KEY,
        environment=PINECONE_ENVIRONMENT
    )

    # Upload embeddings to PineCone with the name of the variable index
    # You can process 'chunks_flat' here or access their content directly as needed
    # Pinecone.from_texts(chunks_flat, cohere, index_name=index) # <--- Descomentar esta línea para guardar los embeddings en PineCone
