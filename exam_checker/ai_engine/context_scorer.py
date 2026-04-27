"""
Deterministic context scoring module.
Implements rule-based context evaluation without external APIs.
"""

import re
from collections import Counter


class DeterministicContextScorer:
    """Rule-based context scorer for keyword coverage, adequacy, and structure."""

    STOPWORDS = {
        'a', 'an', 'the', 'and', 'or', 'but', 'if', 'then', 'else', 'when', 'while',
        'of', 'in', 'on', 'at', 'to', 'for', 'from', 'by', 'with', 'about', 'into',
        'is', 'am', 'are', 'was', 'were', 'be', 'been', 'being', 'it', 'this', 'that',
        'these', 'those', 'as', 'not', 'no', 'yes', 'can', 'could', 'should', 'would',
        'will', 'shall', 'may', 'might', 'must', 'do', 'does', 'did', 'done', 'have',
        'has', 'had', 'i', 'you', 'he', 'she', 'they', 'we', 'my', 'your', 'his',
        'her', 'their', 'our', 'me', 'him', 'them', 'us', 'what', 'which', 'who',
        'whom', 'why', 'how', 'than', 'too', 'very'
    }

    def _normalize(self, text):
        text = (text or '').lower()
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _tokenize(self, text):
        return [t for t in self._normalize(text).split() if t]

    def _content_tokens(self, text):
        return [
            t for t in self._tokenize(text)
            if t not in self.STOPWORDS and len(t) > 2
        ]

    def _extract_keywords(self, model_answer, max_keywords=25):
        tokens = self._content_tokens(model_answer)
        if not tokens:
            return []

        counts = Counter(tokens)
        # Frequency-first ranking keeps scoring deterministic and lightweight.
        ranked = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
        return [word for word, _ in ranked[:max_keywords]]

    def _keyword_coverage(self, student_answer, model_answer):
        keywords = self._extract_keywords(model_answer)
        if not keywords:
            return {
                'keyword_score': 0.0,
                'matched_keywords': [],
                'total_keywords': 0,
                'matched_count': 0,
            }

        student_tokens = set(self._content_tokens(student_answer))
        matched = [kw for kw in keywords if kw in student_tokens]

        score = (len(matched) / len(keywords)) * 100
        return {
            'keyword_score': round(min(100.0, max(0.0, score)), 2),
            'matched_keywords': matched,
            'total_keywords': len(keywords),
            'matched_count': len(matched),
        }

    def _length_adequacy(self, student_answer, model_answer):
        student_words = len(self._tokenize(student_answer))
        model_words = len(self._tokenize(model_answer))

        if model_words == 0:
            return {
                'length_score': 0.0,
                'student_word_count': student_words,
                'model_word_count': model_words,
                'length_ratio': 0.0,
            }

        ratio = student_words / model_words
        score = min(ratio, 1.0) * 100

        return {
            'length_score': round(min(100.0, max(0.0, score)), 2),
            'student_word_count': student_words,
            'model_word_count': model_words,
            'length_ratio': round(ratio, 3),
        }

    def _structure_quality(self, student_answer):
        text = (student_answer or '').strip()
        if not text:
            return {
                'structure_score': 30.0,
                'sentence_count': 0,
                'punctuation_present': False,
                'readability_band': 'poor',
            }

        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        sentence_count = len(sentences)
        punctuation_present = any(ch in text for ch in '.!?;,')
        words = self._tokenize(text)
        avg_sentence_len = (len(words) / sentence_count) if sentence_count > 0 else 0

        if sentence_count >= 2 and punctuation_present and 6 <= avg_sentence_len <= 35:
            score = 92.0
            band = 'good'
        elif sentence_count >= 2 and punctuation_present:
            score = 82.0
            band = 'good'
        elif sentence_count >= 1 and punctuation_present:
            score = 72.0
            band = 'moderate'
        elif sentence_count >= 1:
            score = 58.0
            band = 'moderate'
        else:
            score = 40.0
            band = 'poor'

        return {
            'structure_score': score,
            'sentence_count': sentence_count,
            'punctuation_present': punctuation_present,
            'readability_band': band,
        }

    def compute_context_score(self, student_answer, model_answer):
        """
        Final context score formula:
        context = 0.4*keyword + 0.3*length + 0.3*structure
        """
        keyword = self._keyword_coverage(student_answer, model_answer)
        length = self._length_adequacy(student_answer, model_answer)
        structure = self._structure_quality(student_answer)

        context_score = (
            (0.4 * keyword['keyword_score'])
            + (0.3 * length['length_score'])
            + (0.3 * structure['structure_score'])
        )
        context_score = round(min(100.0, max(0.0, context_score)), 2)

        return {
            'context_score': context_score,
            'keyword_score': keyword['keyword_score'],
            'length_score': length['length_score'],
            'structure_score': structure['structure_score'],
            'matched_keywords': keyword['matched_keywords'],
            'matched_count': keyword['matched_count'],
            'total_keywords': keyword['total_keywords'],
            'student_word_count': length['student_word_count'],
            'model_word_count': length['model_word_count'],
            'length_ratio': length['length_ratio'],
            'sentence_count': structure['sentence_count'],
            'punctuation_present': structure['punctuation_present'],
            'readability_band': structure['readability_band'],
        }
