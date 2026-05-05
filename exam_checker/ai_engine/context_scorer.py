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

    def _stem(self, token):
        """Very small deterministic stemmer for matching keywords reliably."""
        if len(token) <= 3:
            return token

        for suffix in ('ing', 'edly', 'edly', 'ed', 'es', 's'):
            if token.endswith(suffix) and len(token) - len(suffix) >= 3:
                return token[: -len(suffix)]
        return token

    def _tokenize(self, text):
        return [self._stem(t) for t in self._normalize(text).split() if t]

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

    def _split_subpoints(self, model_answer, question_text=''):
        """Derive expected subpoints from the model answer and question prompt."""
        text = f"{question_text or ''}. {model_answer or ''}".strip()
        if not text:
            return []

        raw_parts = re.split(r'[\n\.;:•\-]+|\band\b|\balso\b|\bfurther\b|\bmoreover\b|\badditionally\b', text, flags=re.IGNORECASE)
        subpoints = []
        for part in raw_parts:
            cleaned = part.strip()
            tokens = self._content_tokens(cleaned)
            if len(tokens) >= 2:
                subpoints.append(' '.join(tokens[:6]))

        # De-duplicate while preserving order
        unique = []
        seen = set()
        for point in subpoints:
            if point not in seen:
                seen.add(point)
                unique.append(point)
        return unique[:8]

    def _keyword_coverage(self, student_answer, model_answer, question_text=''):
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
        # Per the requested formula, answers shorter than 50% are floored at 50%.
        score = min(max(ratio, 0.5), 1.0) * 100

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

        connective_words = {
            'first', 'second', 'third', 'then', 'next', 'finally', 'because', 'therefore',
            'hence', 'thus', 'also', 'furthermore', 'moreover', 'for example', 'in addition',
            'in summary', 'conclusion', 'overall', 'however'
        }
        connective_count = sum(1 for token in words if token in connective_words)
        bullet_like = bool(re.search(r'(^|\n)\s*(?:[-*•]|\d+[\).])\s+', text))

        sentence_score = min(sentence_count / 3.0, 1.0) * 100
        punctuation_score = 100 if punctuation_present else 55
        connective_score = min(connective_count / 3.0, 1.0) * 100
        bullet_score = 100 if bullet_like else 60

        # Balanced structure score with a small reward for readable formatting.
        score = (
            0.30 * sentence_score +
            0.25 * punctuation_score +
            0.25 * connective_score +
            0.20 * bullet_score
        )

        if sentence_count >= 2 and punctuation_present:
            band = 'good' if avg_sentence_len <= 35 else 'moderate'
        elif sentence_count >= 1:
            band = 'moderate'
        else:
            band = 'poor'

        return {
            'structure_score': round(min(100.0, max(0.0, score)), 2),
            'sentence_count': sentence_count,
            'punctuation_present': punctuation_present,
            'readability_band': band,
            'connective_count': connective_count,
            'bullet_like': bullet_like,
            'avg_sentence_len': round(avg_sentence_len, 2),
        }

    def _completeness_score(self, student_answer, model_answer, question_text=''):
        """Score how much of the expected answer is covered by the student."""
        subpoints = self._split_subpoints(model_answer, question_text)
        if not subpoints:
            keyword = self._keyword_coverage(student_answer, model_answer, question_text)
            structure = self._structure_quality(student_answer)
            return {
                'completeness_score': round((keyword['keyword_score'] + structure['structure_score']) / 2.0, 2),
                'matched_subpoints': [],
                'total_subpoints': 0,
            }

        student_tokens = set(self._content_tokens(student_answer))
        student_text = ' '.join(sorted(student_tokens))
        matched = []

        for point in subpoints:
            point_tokens = [t for t in point.split() if t]
            if not point_tokens:
                continue

            # Match if enough key tokens from the subpoint appear in the student answer.
            matched_tokens = sum(1 for token in point_tokens if token in student_tokens or token in student_text)
            threshold = max(1, round(len(point_tokens) * 0.6))
            if matched_tokens >= threshold:
                matched.append(point)

        score = (len(matched) / len(subpoints)) * 100 if subpoints else 0.0
        return {
            'completeness_score': round(min(100.0, max(0.0, score)), 2),
            'matched_subpoints': matched,
            'total_subpoints': len(subpoints),
        }

    def _clarity_score(self, student_answer):
        """Approximate readability/clarity as a 0-100 score."""
        text = (student_answer or '').strip()
        if not text:
            return {
                'clarity_score': 30.0,
                'avg_sentence_len': 0.0,
            }

        words = self._tokenize(text)
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        sentence_count = max(1, len(sentences))
        avg_sentence_len = len(words) / sentence_count if sentence_count else len(words)

        # Prefer concise, complete answers around 12-22 words per sentence.
        optimal = 17.0
        deviation = abs(avg_sentence_len - optimal)
        score = 100.0 - min(60.0, deviation * 4.0)

        if sentence_count >= 2:
            score += 5.0
        if any(ch in text for ch in '.!?;,'):
            score += 5.0
        if len(words) >= 12:
            score += 5.0

        return {
            'clarity_score': round(min(100.0, max(0.0, score)), 2),
            'avg_sentence_len': round(avg_sentence_len, 2),
        }

    def compute_context_score(self, student_answer, model_answer, question_text=''):
        """
        Final context score formula:
        context = 0.20*keyword + 0.15*length + 0.15*structure + 0.20*completeness + 0.20*accuracy + 0.10*clarity
        """
        keyword = self._keyword_coverage(student_answer, model_answer, question_text)
        length = self._length_adequacy(student_answer, model_answer)
        structure = self._structure_quality(student_answer)
        completeness = self._completeness_score(student_answer, model_answer, question_text)
        clarity = self._clarity_score(student_answer)

        # Provisional context score returned by the scorer itself.
        # The evaluator recomputes the final context score by injecting the
        # requested accuracy formula (0.6*similarity + 0.4*keyword).
        context_score = (
            (0.25 * keyword['keyword_score'])
            + (0.20 * length['length_score'])
            + (0.20 * structure['structure_score'])
            + (0.20 * completeness['completeness_score'])
            + (0.15 * clarity['clarity_score'])
        )
        context_score = round(min(100.0, max(0.0, context_score)), 2)

        return {
            'context_score': context_score,
            'keyword_score': keyword['keyword_score'],
            'length_score': length['length_score'],
            'structure_score': structure['structure_score'],
            'completeness_score': completeness['completeness_score'],
            'clarity_score': clarity['clarity_score'],
            'matched_keywords': keyword['matched_keywords'],
            'matched_count': keyword['matched_count'],
            'total_keywords': keyword['total_keywords'],
            'matched_subpoints': completeness.get('matched_subpoints', []),
            'total_subpoints': completeness.get('total_subpoints', 0),
            'student_word_count': length['student_word_count'],
            'model_word_count': length['model_word_count'],
            'length_ratio': length['length_ratio'],
            'sentence_count': structure['sentence_count'],
            'punctuation_present': structure['punctuation_present'],
            'readability_band': structure['readability_band'],
            'connective_count': structure.get('connective_count', 0),
            'bullet_like': structure.get('bullet_like', False),
            'avg_sentence_len': structure.get('avg_sentence_len', 0),
        }
