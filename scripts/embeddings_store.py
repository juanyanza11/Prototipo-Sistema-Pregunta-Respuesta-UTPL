# Client
import pinecone

# Utilis
import os
import time
import string
import pandas as pd
from dotenv import load_dotenv

# Vector store
from langchain.vectorstores import Pinecone

# Embeddings tested
from langchain.embeddings import HuggingFaceEmbeddings

# Text splitters tested
from langchain.text_splitter import SentenceTransformersTokenTextSplitter
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.text_splitter import CharacterTextSplitter
# from langchain.text_splitter import NLTKTextSplitter
# from langchain.text_splitter import TokenTextSplitter
# from langchain.text_splitter import SpacyTextSplitter
# from transformers import GPT2TokenizerFast

# DBSCAN clustering and PCA
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA
from sklearn.cluster import DBSCAN

# Visualization
import seaborn as sns
import matplotlib.pyplot as plt

def preprocess_text(text):
    # Eliminar signos de puntuación y convertir a minúsculas
    text = text.lower().translate(str.maketrans('', '', string.punctuation))
    
    # Eliminar palabras vacías
    text = ' '.join([word for word in text.split() if word not in ENGLISH_STOP_WORDS])
    return text


def almacenar_embeddings_dbscan(index, directorio):
    load_dotenv()

    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")

    # Cargar contenido actualizado
    df = pd.read_csv(os.path.abspath(directorio), delimiter=',', encoding='utf-8',
                     names=["Seccion", 'Subseccion', "Contenido", "WikipageID", "LastModified"])

    # Documentos a lista
    df = df.drop(0, axis=0)
    documentos = df['Contenido'].tolist()
    print(f"Se obtuvieron {len(documentos)} documentos.")

    # Embeddings size compaibility with Pinecone 768
    embeddings = HuggingFaceEmbeddings(model_name='BAAI/bge-base-en-v1.5')

    # Todos los splitters probados

    text_splitter = SentenceTransformersTokenTextSplitter(chunk_overlap=0, chunk_size=256)

    chunks = []
    
    for doc in documentos:
        
        splited_text = text_splitter.split_text(doc)
        print(f"Contenido: {doc}")
        print(f"Se obtuvieron {len(splited_text)} elementos separados.")
        
        for text_element in splited_text:
            text = {
                'text': text_element,
            }
            chunks.append(text)

    # Chunks en una sola lista
    chunks_flat = [chunk['text'] for chunk in chunks]
    set_chunks_flat = list(set(chunks_flat))
    
    # Chunks_flat: 66632 - Set_chunks_flat: 49590 // Duplicados eliminados
    print(f'Chunks_flat: {len(chunks_flat)} - Set_chunks_flat: {len(set_chunks_flat)}')
    
    # Convertir los documentos a lista de textos // usando set_chunks_flat
    documents_text = [preprocess_text(chunk) for chunk in set_chunks_flat]
    
    print(len(documents_text))

    # Vectorizar los documentos con TF-IDF
    vectorizer = TfidfVectorizer(min_df=0.1, max_df=0.9)
    X = vectorizer.fit_transform(documents_text)

    print(f"Matriz de {X.shape[0]} documentos y {X.shape[1]} características.")

    # DBSCAN clustering
    dbscan = DBSCAN(eps=0.5, min_samples=5)
    clusters = dbscan.fit_predict(X)

    all_documents = []
    text_cluser_0 = []
    text_cluser_1 = []
    
    for i, doc_chunk in enumerate(documents_text):
        row = {
            'text': doc_chunk,
            'cluster': clusters[i]
        }
        
        
        all_documents.append(doc_chunk)
        
        # Agregar el cluster a la metadata
        if clusters[i] == 0:
            text_cluser_0.append(row)
        else:
            text_cluser_1.append(row)
            

    data_hist = []
    total_chunks_char = 0
    total_chunks_word = 0
    count_word_range = 0
    count_word = 0
    count = 0

    for a in all_documents:

        print(f"Chunk de {len(a.split(' '))} palabras")
        print('*' * 70, 'Contenido', '*' * 70)
        print(a)
        print('*' * 150)
        count_word += 1 if len(a.split(' ')) >= 0 else 0
        count += 1 if len(a) >= 1199 else 0
        count_word_range += 1 if 60 <= len(a.split(' ')) <= 256 else 0
        total_chunks_char += len(a)
        total_chunks_word += len(a.split(' '))
        data_hist.append(len(a.split(' ')))

    # Graficar histograma de distribucion de chunks
    plt.hist(data_hist, bins=100)
    plt.title('Histograma de distribución de chunks')
    plt.show()
        
    print("Media de tokens por palabras: {:,.2f}".format(
        total_chunks_word/len(all_documents)))
    print(f"Se obtuvieron {count_word} documentos, tokens por palabras.")
    print(f"Se obtuvieron {count_word_range} documentos entre 60 y 256.")
    print("-" * 150)

    # Reducción de dimensionalidad con PCA
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X.toarray())

    # Graficar los clusters
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x=X_pca[:, 0], y=X_pca[:, 1],
                    hue=clusters, palette='viridis', legend='full')
    plt.title('Clusters DBSCAN')
    plt.xlabel('Componente Principal 1')
    plt.ylabel('Componente Principal 2')
    plt.show()

    print('----------- DBSCAN -----------')
    print(f"Documentos Originales: {len(set_chunks_flat)}")
    print(f"Documentos cluster 1: {len(text_cluser_1)}")
    print(f"Documentos cluster 1: {len(text_cluser_0)}")

    # Guardar metadata en un archivo CSV
    df = pd.DataFrame(text_cluser_0)
    df.to_csv('data/cluster_0.csv', index=False)
    
    df = pd.DataFrame(text_cluser_1)
    df.to_csv('data/cluster_1.csv', index=False)
    
    # CLI Pinecone
    pinecone.init(
        api_key=PINECONE_API_KEY,
        environment=PINECONE_ENVIRONMENT
    )
    
    start_time = time.time()
    print(f'Subiendo un total de {len(all_documents)} embeddings a Pinecone...')
    # Pinecone.from_texts(all_documents, embeddings, index_name=index, )
    elapsed_time = time.time() - start_time   
    print(f'Embeddings subidos en {elapsed_time//3600} horas.')
