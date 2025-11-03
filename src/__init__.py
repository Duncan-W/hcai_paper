"""
HCAI Paper - LLM-Based Taxonomy Generation for University Module Learning Outcomes

This package provides tools to automatically generate taxonomies of learning outcomes
and skills from university module directories using Large Language Models.
"""

from .scraper import UCDModuleScraper
from .taxonomy_generator import TaxonomyGenerator
from .visualizer import TaxonomyVisualizer
from .analysis import TaxonomyAnalyzer

__version__ = "0.1.0"
__all__ = [
    'UCDModuleScraper',
    'TaxonomyGenerator',
    'TaxonomyVisualizer',
    'TaxonomyAnalyzer',
]
