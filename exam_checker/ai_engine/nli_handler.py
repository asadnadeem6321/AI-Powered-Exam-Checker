"""
NLI Handler - lightweight wrapper around Hugging Face NLI models

Provides an `analyze(premise, hypothesis)` method that returns
probabilities for `entailment`, `neutral`, and `contradiction`.
This is intentionally lazy-loaded and non-fatal if transformers or model
are unavailable; the evaluator will continue to work without NLI.
"""
from typing import Dict
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class NLIUnavailable(Exception):
    pass


class NLIHandler:
    def __init__(self, model_name: str = None):
        self.model_name = model_name or getattr(settings, 'NLI_MODEL_NAME', 'facebook/bart-large-mnli')
        self.pipeline = None
        try:
            from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
            import torch

            # Use CPU by default; pipeline will select GPU automatically if available
            self.pipeline = pipeline(
                task='text-classification',
                model=self.model_name,
                tokenizer=self.model_name,
                return_all_scores=True,
                device=0 if torch.cuda.is_available() else -1,
            )
            logger.info(f"NLIHandler loaded model: {self.model_name}")
        except Exception as e:
            logger.warning(f"NLIHandler unavailable: {e}")
            self.pipeline = None

    def analyze(self, premise: str, hypothesis: str) -> Dict[str, float]:
        """
        Analyze entailment between premise (student answer) and hypothesis (model answer).

        Returns dict: {'entailment': float, 'neutral': float, 'contradiction': float}
        If pipeline unavailable, returns zeros.
        """
        if not self.pipeline:
            return {'entailment': 0.0, 'neutral': 0.0, 'contradiction': 0.0}

        try:
            # The pipeline accepts pairs if passed as tuples
            out = self.pipeline([(premise or "", hypothesis or "")])
            if not out or not isinstance(out, list):
                return {'entailment': 0.0, 'neutral': 0.0, 'contradiction': 0.0}

            scores = out[0]
            # Map labels to probabilities (labels vary by model - normalize by common names)
            mapping = {'ENTAILMENT': 'entailment', 'NEUTRAL': 'neutral', 'CONTRADICTION': 'contradiction'}
            result = {'entailment': 0.0, 'neutral': 0.0, 'contradiction': 0.0}
            for entry in scores:
                label = entry.get('label') or entry.get('score')
                score = float(entry.get('score', 0.0))
                if isinstance(label, str):
                    key = mapping.get(label.upper(), None)
                    if key:
                        result[key] = score

            return result

        except Exception as e:
            logger.warning(f"NLI analysis failed: {e}")
            return {'entailment': 0.0, 'neutral': 0.0, 'contradiction': 0.0}
