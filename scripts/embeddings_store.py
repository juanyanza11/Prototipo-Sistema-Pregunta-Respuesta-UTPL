# Client
import pinecone

# Utilis
import os
from dotenv import load_dotenv
import string
import pandas as pd

# Vector store
from langchain.vectorstores import Pinecone

# Embeddings tested
from langchain.embeddings import HuggingFaceEmbeddings

# Text splitters tested
from langchain.text_splitter import SentenceTransformersTokenTextSplitter
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.text_splitter import CharacterTextSplitter
from langchain.text_splitter import NLTKTextSplitter
from langchain.text_splitter import TokenTextSplitter
from langchain.text_splitter import SpacyTextSplitter
from transformers import GPT2TokenizerFast

# DBSCAN clustering and PCA
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
from sklearn.cluster import DBSCAN

# Visualization
import seaborn as sns
import matplotlib.pyplot as plt


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
    # print(df.head())

    embeddings = HuggingFaceEmbeddings(model_name='BAAI/bge-base-en-v1.5')

    # All text splitters tested

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_overlap=0, separators=[" "])

    # tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
    # text_splitter = CharacterTextSplitter.from_huggingface_tokenizer(
    # tokenizer, chunk_overlap=0)

    # text_splitter = NLTKTextSplitter()

    # text_splitter = SentenceTransformersTokenTextSplitter(chunk_overlap=0)

    # text_splitter = SpacyTextSplitter(separator=" ", chunk_overlap=0, chunk_size=256)

    # text_splitter = TokenTextSplitter(chunk_overlap=0)

    # text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
    #     chunk_overlap=0, chunk_size=1000)

    # Separar los documentos en chunks
    chunks = [text_splitter.split_text(doc) for doc in documentos]

    # Chunks en una sola lista
    chunks_flat = [chunk for sublist in chunks for chunk in sublist]

    # Convertir los documentos a lista de textos
    documents_text = [preprocess_text(chunk) for chunk in chunks_flat]

    # Vectorizar los documentos con TF-IDF
    vectorizer = TfidfVectorizer(min_df=0.1, max_df=0.9)
    X = vectorizer.fit_transform(documents_text)
    print(f"Matriz de {X.shape[0]} documentos y {X.shape[1]} características.")

    # DBSCAN clustering
    dbscan = DBSCAN(eps=0.5, min_samples=5)
    clusters = dbscan.fit_predict(X)

    pollution_documents = []

    for i, doc_chunk in enumerate(chunks_flat):
        print(f"Chunk {i} pertennece al cluster {clusters[i]}")
        # Si el chunk pertenece al cluster 1, agregarlo a la lista de documentos relacionados con Pollution
        if clusters[i] == 1:
            pollution_documents.append(doc_chunk)

    total_chunks_char = 0
    total_chunks_word = 0
    data_hist = []
    count = 0
    count_word_range = 0
    count_word = 0

    for a in pollution_documents:

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

    print("Media de tokens por palabras: {:,.2f}".format(
        total_chunks_word/len(pollution_documents)))
    print(f"Se obtuvieron {count_word} documentos, tokens por palabras.")
    print(f"Se obtuvieron {count_word_range} documentos entre 60 y 256.")
    print("-" * 150)

    # Reducción de dimensionalidad con PCA (opcional)
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
    print(f"Documentos Originales: {len(chunks_flat)}")
    print(f"Documentos relacionados a Pollution: {len(pollution_documents)}")

    print('----------- DBSCAN Evaluación -----------')
    eps_values = [0.1, 0.2, 0.3, 0.4, 0.5]
    silhouette_scores = []

    for eps in eps_values:
        dbscan = DBSCAN(eps=eps, min_samples=5)
        clusters = dbscan.fit_predict(X)
        silhouette_scores.append(silhouette_score(X, clusters))

    for eps, score in zip(eps_values, silhouette_scores):
        print(f"eps={eps}, silhouette_score={score}")

    plt.hist(data_hist, bins='auto')
    plt.show()

    # Trama la gráfica
    plt.figure(figsize=(8, 6))
    plt.plot(eps_values, silhouette_scores, marker='o', linestyle='-')
    plt.xlabel('Valor de eps')
    plt.ylabel('Puntuación de silueta')
    plt.title('Análisis de Codo para Determinar eps en DBSCAN')
    plt.grid(True)
    plt.show()

    # Almacenar nuevos documentos relacionados con Pollution en un CSV
    df['Cluster'] = clusters
    pollution_df = df[df['Cluster'] == 1][['Contenido', 'Cluster']]
    pollution_df.to_csv("data/pollution_documents.csv", index=False)

    # Initialize PineCone
    pinecone.init(
        api_key=PINECONE_API_KEY,
        environment=PINECONE_ENVIRONMENT
    )

    # Upload embeddings to PineCone with the name of the specified index
    # print("Subiendo embeddings a Pinecone...")
    # 1200 - Alto procesamiento CPU ✅
    # Pinecone.from_texts(pollution_documents, embeddings, index_name=index, embeddings_chunk_size=1200)


def preprocess_text(text):
    # Eliminar signos de puntuación y convertir a minúsculas
    text = text.lower().translate(str.maketrans('', '', string.punctuation))
    # Eliminar palabras vacías
    text = ' '.join([word for word in text.split()
                    if word not in ENGLISH_STOP_WORDS])
    return text
