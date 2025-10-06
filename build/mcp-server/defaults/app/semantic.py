import os
import numpy as np
import pickle

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List

from settings import CORPUS_PATH_DOCS, CORPUS_PATH_EMBEDDING

# pip install sentence-transformers scikit-learn numpy

# os.environ['HF_HOME'] = '/app/huggingface'
# os.environ['TRANSFORMERS_CACHE'] = '/app/huggingface'


class SemanticChapterSearch:
    def __init__(self, model_name='embaas/sentence-transformers-multilingual-e5-large'):
        self.model = SentenceTransformer(model_name, cache_folder='/app/model_cache', local_files_only=True)
        self.chunks = []
        self.embeddings = None
        self.file_embedding = f'{CORPUS_PATH_EMBEDDING}/docs.pkl'
        if not os.path.exists(self.file_embedding):
            self.create_embeddings(CORPUS_PATH_DOCS)
        else:
            self.load_embeddings()

    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
        """Versión simple y robusta"""
        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size

            # Si es el último chunk, tomar todo lo que queda
            if end >= len(text):
                chunks.append(text[start:].strip())
                break

            # Buscar un punto final para cortar mejor
            chunk_candidate = text[start:end]
            last_period = chunk_candidate.rfind('.')

            if last_period > chunk_size * 0.7:  # Solo si está en el último 30%
                actual_end = start + last_period + 1
            else:
                actual_end = end

            chunks.append(text[start:actual_end].strip())

            # Avanzar con overlap
            start = actual_end - overlap

            # Evitar retroceso excesivo
            if start < 0:
                start = 0

        return chunks

    def create_embeddings(self, chapters_dir: str):
        """Procesa todos los archivos chapters_dir y crea embeddings"""
        all_chunks = []

        for filename in os.listdir(chapters_dir):
            filepath = os.path.join(chapters_dir, filename)

            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Crear chunks del capítulo
                chapter_chunks = self.chunk_text(content)

                # Añadir metadatos a cada chunk
                for j, chunk in enumerate(chapter_chunks):
                    chunk_info = {
                        'text': chunk,
                        'chunk_id': j,
                        'filename': filename
                    }
                    all_chunks.append(chunk_info)

        self.chunks = all_chunks
        # Crear embeddings
        texts = [chunk['text'] for chunk in all_chunks]
        self.embeddings = self.model.encode(texts)

        chapter_count = len([f for f in os.listdir(chapters_dir) if f.startswith('chapter')])
        print(
            f"Procesados {len(all_chunks)} chunks de {chapter_count} capítulos"
        )

        # Guardar automáticamente
        self.save_embeddings()

    def save_embeddings(self):
        os.makedirs(CORPUS_PATH_EMBEDDING, exist_ok=True)

        """Guarda embeddings y chunks"""
        data = {
            'chunks': self.chunks,
            'embeddings': self.embeddings
        }
        with open(self.file_embedding, 'wb') as f:
            pickle.dump(data, f)

    def load_embeddings(self):
        """Carga embeddings y chunks"""
        try:
            with open(self.file_embedding, 'rb') as f:
                data = pickle.load(f)
            self.chunks = data['chunks']
            self.embeddings = data['embeddings']
            return True
        except FileNotFoundError:
            print(f"Archivo {self.file_embedding} no encontrado. Necesitas crear los embeddings primero.")
            return False

    def search_chunks_with_context(self, query: str, top_k: int = 10, similarity_threshold: float = 0.3) -> List[dict]:
        """
        Busca chunks relevantes con contexto (chunk anterior y posterior)

        Args:
            query: Pregunta o texto a buscar
            top_k: Número de chunks a devolver
            similarity_threshold: Umbral mínimo de similitud

        Returns:
            Lista de diccionarios con chunk principal y contexto
        """
        if self.embeddings is None:
            if not self.load_embeddings():
                return []

        # Crear embedding de la consulta
        query_embedding = self.model.encode([query])

        # Calcular similitudes
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]

        # Obtener chunks que superan el umbral
        relevant_indices = np.where(similarities >= similarity_threshold)[0]

        if len(relevant_indices) == 0:
            return []

        # Ordenar por similitud (mayor a menor)
        sorted_indices = relevant_indices[np.argsort(similarities[relevant_indices])[::-1]]

        # Tomar solo los top_k
        top_indices = sorted_indices[:top_k]

        # Construir resultado con contexto
        results = []

        for idx in top_indices:
            main_chunk = self.chunks[idx]
            filename = main_chunk['filename']
            chunk_id = main_chunk['chunk_id']

            # Buscar chunks del mismo fichero
            chapter_chunks = [
                (i, chunk) for i, chunk in enumerate(self.chunks)
                if chunk['filename'] == filename
            ]

            # Ordenar por chunk_id para obtener secuencia correcta
            chapter_chunks.sort(key=lambda x: x[1]['chunk_id'])

            # Encontrar posición del chunk principal
            main_position = None
            for pos, (global_idx, chunk) in enumerate(chapter_chunks):
                if global_idx == idx:
                    main_position = pos
                    break

            # Obtener contexto
            context_before = ""
            context_after = ""

            if main_position is not None:
                # Chunk anterior
                if main_position > 0:
                    context_before = chapter_chunks[main_position - 1][1]['text']

                # Chunk posterior
                if main_position < len(chapter_chunks) - 1:
                    context_after = chapter_chunks[main_position + 1][1]['text']

            # Construir resultado
            result = {
                'similarity': similarities[idx],
                'chunk_id': chunk_id,
                'filename': main_chunk['filename'],
                'main_text': main_chunk['text'],
                'context_before': context_before,
                'context_after': context_after,
                'full_text': f"{context_before}\n\n{main_chunk['text']}\n\n{context_after}".strip()
            }
            results.append(result)

        return results

    def search_text_with_context(self, query: str, top_k: int = 10, similarity_threshold: float = 0.3) -> str:
        """
        Versión simplificada que devuelve solo el texto concatenado con contexto

        Returns:
            String con todos los chunks y contexto concatenados
        """
        results = self.search_chunks_with_context(query, top_k, similarity_threshold)

        if not results:
            return "No se encontraron chunks relevantes."

        text_parts = []
        for i, result in enumerate(results):
            text_parts.append(f"=== RESULTADO {i+1} ===")
            text_parts.append(f"Chunk {result['chunk_id']} (Similitud: {result['similarity']:.4f})")
            text_parts.append(f"Archivo: {result['filename']}")
            text_parts.append("")
            text_parts.append(result['full_text'])
            text_parts.append("")
            text_parts.append("=" * 50)
            text_parts.append("")

        return "\n".join(text_parts)


if __name__ == "__main__":
    # Ejemplo de uso
    searcher = SemanticChapterSearch()

    text = searcher.search_text_with_context("huevo frito")
    print(text)
    exit(0)
