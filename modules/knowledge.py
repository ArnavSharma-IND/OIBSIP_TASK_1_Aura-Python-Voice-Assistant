"""
General Knowledge and Question Answering Module for ArnavSharma_Task1.
Provides dual-layer QA: an offline curated encyclopedia of scientific, historical,
and computational facts, supplemented by online Wikipedia search and DuckDuckGo API.
"""

import re
from typing import Dict, Optional, Tuple

from utils.logger import get_logger

logger = get_logger("Knowledge")

HAVE_WIKIPEDIA = False
try:
    import wikipedia
    HAVE_WIKIPEDIA = True
except ImportError:
    wikipedia = None
    logger.warning("wikipedia library is not installed.")


# Comprehensive Offline Curated Knowledge Base
OFFLINE_KNOWLEDGE_BASE: Dict[str, str] = {
    "python": (
        "Python is a high-level, interpreted programming language created by Guido van Rossum "
        "and first released in 1991. It emphasizes code readability and supports multiple paradigms."
    ),
    "artificial intelligence": (
        "Artificial Intelligence is the simulation of human intelligence processes by computer systems, "
        "including learning, reasoning, problem-solving, and perception."
    ),
    "machine learning": (
        "Machine Learning is a subset of artificial intelligence focused on building applications that learn "
        "from data and improve their accuracy over time without being explicitly programmed."
    ),
    "deep learning": (
        "Deep Learning is a specialized branch of machine learning based on artificial neural networks "
        "with multiple layers, inspired by the structure and function of the human brain."
    ),
    "quantum computing": (
        "Quantum computing is a rapidly-emerging technology that harnesses the laws of quantum mechanics, "
        "such as superposition and entanglement, to solve complex problems exponentially faster than classical computers."
    ),
    "albert einstein": (
        "Albert Einstein was a German-born theoretical physicist widely acknowledged as one of the greatest "
        "physicists of all time. He is best known for developing the theory of relativity and the mass-energy equivalence formula E = mc²."
    ),
    "alan turing": (
        "Alan Turing was an English mathematician, computer scientist, and cryptanalyst widely considered "
        "the father of modern computer science and artificial intelligence."
    ),
    "ada lovelace": (
        "Ada Lovelace was an English mathematician and writer, chiefly known for her work on Charles Babbage's "
        "Analytical Engine. She is recognized as the world's first computer programmer."
    ),
    "photosynthesis": (
        "Photosynthesis is the biological process used by plants and other organisms to convert light energy "
        "into chemical energy, using sunlight, water, and carbon dioxide to produce glucose and oxygen."
    ),
    "gravity": (
        "Gravity is a fundamental natural phenomenon by which all things with mass or energy are attracted "
        "toward one another, first mathematically described by Sir Isaac Newton."
    ),
    "speed of light": (
        "The speed of light in a vacuum is approximately 299,792 kilometers per second, or about 186,282 miles per second."
    ),
    "capital of france": "The capital of France is Paris, world-renowned for its art, culture, and architecture.",
    "capital of india": "The capital of India is New Delhi, the seat of the executive, legislative, and judicial branches.",
    "capital of usa": "The capital of the United States is Washington, D.C.",
    "capital of japan": "The capital of Japan is Tokyo, one of the most populous metropolitan areas in the world.",
    "mount everest": (
        "Mount Everest is Earth's highest mountain above sea level, located in the Mahalangur Himal sub-range "
        "of the Himalayas, standing at 8,848.86 meters."
    ),
    "dna": (
        "DNA, or deoxyribonucleic acid, is the hereditary material in humans and almost all other organisms, "
        "carrying genetic instructions for development and functioning."
    ),
    "internet": (
        "The Internet is a global network of billions of computers and other electronic devices, "
        "enabling communication and access to almost any information."
    ),
}


class KnowledgeService:
    """Answers general knowledge questions using local offline data and Wikipedia API."""

    def __init__(self, use_online: bool = True):
        self.use_online = use_online

    def query(self, topic: str) -> Tuple[bool, str, str]:
        """
        Retrieves an answer for a general knowledge inquiry.

        Args:
            topic: Concept, person, place, or question topic.

        Returns:
            Tuple of (success: bool, spoken_answer: str, source: str)
        """
        clean_topic = topic.strip().lower()
        if not clean_topic:
            return False, "Please tell me what you would like to know.", "none"

        # Remove common question prefix words
        clean_topic = re.sub(
            r"^(who\s+is|who\s+was|what\s+is|what\s+was|what\s+are|tell\s+me\s+about|information\s+about|where\s+is|define)\s+",
            "",
            clean_topic,
        ).strip()
        clean_topic = clean_topic.rstrip("?").strip()

        logger.info(f"Knowledge lookup for: '{clean_topic}'")

        # 1. Check local offline knowledge base first
        for key, answer in OFFLINE_KNOWLEDGE_BASE.items():
            if key == clean_topic or key in clean_topic or clean_topic in key:
                logger.info(f"Resolved from offline knowledge base: '{key}'")
                return True, answer, "offline_kb"

        # 2. Check online Wikipedia if enabled
        if self.use_online and HAVE_WIKIPEDIA:
            try:
                # Set English language
                wikipedia.set_lang("en")
                # Retrieve concise 2-sentence summary
                summary = wikipedia.summary(clean_topic, sentences=2, auto_suggest=True)
                # Clean up pronunciation keys or citation brackets
                summary = re.sub(r"\([^)]*\)", "", summary)
                summary = re.sub(r"\[\d+\]", "", summary)
                summary = re.sub(r"\s+", " ", summary).strip()

                if summary:
                    logger.info(f"Resolved via Wikipedia for: '{clean_topic}'")
                    return True, summary, "wikipedia"

            except wikipedia.exceptions.DisambiguationError as dis_err:
                # Pick the first suggested option if possible
                options = dis_err.options[:3]
                try:
                    summary = wikipedia.summary(options[0], sentences=2, auto_suggest=False)
                    summary = re.sub(r"\([^)]*\)", "", summary)
                    return True, summary, "wikipedia"
                except Exception:
                    options_str = ", ".join(options)
                    msg = f"'{clean_topic}' may refer to multiple topics, such as: {options_str}. Could you be more specific?"
                    return False, msg, "disambiguation"

            except wikipedia.exceptions.PageError:
                logger.info(f"Wikipedia page not found for: '{clean_topic}'")

            except Exception as err:
                logger.warning(f"Wikipedia lookup error for '{clean_topic}': {err}")

        # 3. Fallback message
        fallback = (
            f"I could not find a verified answer for '{clean_topic}' in my knowledge base. "
            f"Would you like me to search the web for it?"
        )
        return False, fallback, "not_found"

