import spacy
from typing import List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from core.ports import NLPServicePort


class TfidfNlpService(NLPServicePort):
    """
    Implementação de Inteligência Artificial com spaCy e scikit-learn.
    """

    def __init__(self):
        # Carrega a rede neural em português do spaCy
        try:
            self._nlp = spacy.load("pt_core_news_sm")
        except OSError:
            raise OSError(
                "Modelo pt_core_news_sm ausente. Execute no terminal: python -m spacy download pt_core_news_sm"
            )

        # Inicia a classe responsável pela matriz do Cosseno
        self._vectorizer = TfidfVectorizer(
            tokenizer=self._spacy_tokenizer,
            token_pattern=None,
            max_df=0.75,  # Ignora palavras que não mudam nada por estarem em todos os cantos
        )
        self._trained_vectors = None

    def _spacy_tokenizer(self, text: str) -> List[str]:
        """Processa a sintaxe e a morfologia da frase"""
        doc = self._nlp(text.lower())
        tokens = []

        # Retém apenas os vocábulos vitais: Substantivos, Adjetivos, Verbos, Nomes
        allowed_pos = {"NOUN", "VERB", "ADJ", "PROPN"}

        for token in doc:
            if token.is_punct or token.is_space or token.is_stop:
                continue  # Descarta stop words ou espaços

            if token.pos_ in allowed_pos:
                # Transforma inflexões verbais/nominais na raíz para agrupar proximidade
                tokens.append(token.lemma_)

        return tokens

    def train(self, documents: List[str]) -> None:
        """Treina a matriz do NLP com as características de todas as doenças unidas."""
        self._trained_vectors = self._vectorizer.fit_transform(documents)

    def find_most_similar(self, query: str) -> Tuple[int, float]:
        """Verifica entre todos os dados de doente qual matriz vetorial está mais próxima (espaço Multidimensional)."""
        if self._trained_vectors is None:
            raise RuntimeError("O modelo TF-IDF não foi treinado.")

        query_vector = self._vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, self._trained_vectors).flatten()

        max_idx = int(similarities.argmax())
        max_score = float(similarities[max_idx])

        return max_idx, max_score
