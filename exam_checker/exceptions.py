"""
Custom exception classes for the Exam Checker application
"""


class ExamCheckerException(Exception):
    """Base exception for all exam checker errors"""
    pass


class FileUploadException(ExamCheckerException):
    """Exception raised for file upload errors"""
    pass


class OCRException(ExamCheckerException):
    """Exception raised for OCR processing errors"""
    pass


class EvaluationException(ExamCheckerException):
    """Exception raised for evaluation errors"""
    pass


class SBERTException(EvaluationException):
    """Exception raised for SBERT model errors"""
    pass


class GPTException(EvaluationException):
    """Exception raised for GPT API errors"""
    pass


class TextExtractionException(ExamCheckerException):
    """Exception raised for text extraction errors"""
    pass


class ModelLoadException(ExamCheckerException):
    """Exception raised when models fail to load"""
    pass
