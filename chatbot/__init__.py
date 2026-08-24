"""
CityCare Chatbot Module

A modular, portable chatbot system for patient interactions using Gemini AI.
Supports appointment booking, viewing appointments, and prescription inquiries.
"""

__version__ = "1.0.0"
__author__ = "CityCare"

from chatbot.api.routes import create_chatbot_router
from chatbot.core.controller import ChatbotController
from chatbot.core.rag_service import RAGService

__all__ = [
    "create_chatbot_router",
    "ChatbotController",
    "RAGService",
]
