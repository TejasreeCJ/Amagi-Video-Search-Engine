"""
Query preprocessing service for Phase 4
Handles abbreviation expansion, synonym handling, and query normalization
"""
import re
from typing import List, Dict, Set


class QueryPreprocessor:
    def __init__(self):
        # Common abbreviations and their expansions
        self.abbreviations = {
            'oop': ['object-oriented programming', 'object oriented programming'],
            'api': ['application programming interface'],
            'sql': ['structured query language'],
            'html': ['hypertext markup language'],
            'css': ['cascading style sheets'],
            'js': ['javascript'],
            'http': ['hypertext transfer protocol'],
            'https': ['hypertext transfer protocol secure'],
            'url': ['uniform resource locator'],
            'uri': ['uniform resource identifier'],
            'json': ['javascript object notation'],
            'xml': ['extensible markup language'],
            'rest': ['representational state transfer'],
            'soap': ['simple object access protocol'],
            'crud': ['create read update delete'],
            'mvc': ['model view controller'],
            'orm': ['object relational mapping'],
            'dbms': ['database management system'],
            'rdbms': ['relational database management system'],
            'nosql': ['not only sql'],
            'ai': ['artificial intelligence'],
            'ml': ['machine learning'],
            'dl': ['deep learning'],
            'nlp': ['natural language processing'],
            'cv': ['computer vision'],
            'cnn': ['convolutional neural network'],
            'rnn': ['recurrent neural network'],
            'lstm': ['long short-term memory'],
            'gpu': ['graphics processing unit'],
            'cpu': ['central processing unit'],
            'ram': ['random access memory'],
            'rom': ['read only memory'],
            'os': ['operating system'],
            'ide': ['integrated development environment'],
            'sdk': ['software development kit'],
            'cli': ['command line interface'],
            'gui': ['graphical user interface'],
            'ui': ['user interface'],
            'ux': ['user experience'],
            'tcp': ['transmission control protocol'],
            'udp': ['user datagram protocol'],
            'ip': ['internet protocol'],
            'dns': ['domain name system'],
            'ftp': ['file transfer protocol'],
            'ssh': ['secure shell'],
            'ssl': ['secure sockets layer'],
            'tls': ['transport layer security'],
        }
        
        # Common synonyms (query term -> synonyms to also search for)
        self.synonyms = {
            'function': ['method', 'procedure', 'routine'],
            'variable': ['var', 'identifier'],
            'class': ['type', 'object'],
            'array': ['list', 'collection'],
            'loop': ['iteration', 'repeat'],
            'condition': ['if', 'statement'],
            'algorithm': ['procedure', 'method'],
            'data structure': ['structure', 'container'],
            'database': ['db', 'data store'],
            'server': ['host', 'node'],
            'client': ['user', 'browser'],
        }
    
    def preprocess(self, query: str) -> str:
        """
        Preprocess query: expand abbreviations, handle synonyms, normalize
        Returns expanded query string
        """
        if not query or not query.strip():
            return query
        
        original_query = query.strip()
        query_lower = original_query.lower()
        
        # Step 1: Expand abbreviations
        expanded_terms = []
        words = query_lower.split()
        
        for word in words:
            # Remove punctuation for matching
            clean_word = re.sub(r'[^\w]', '', word)
            
            if clean_word in self.abbreviations:
                # Add original word
                expanded_terms.append(word)
                # Add expansions
                for expansion in self.abbreviations[clean_word]:
                    expanded_terms.append(expansion)
            else:
                expanded_terms.append(word)
        
        # Step 2: Add synonyms for key terms
        synonym_terms = []
        for word in words:
            clean_word = re.sub(r'[^\w]', '', word)
            if clean_word in self.synonyms:
                synonym_terms.extend(self.synonyms[clean_word])
        
        # Combine: original + expansions + synonyms
        all_terms = expanded_terms + synonym_terms
        
        # Step 3: Remove duplicates while preserving order
        seen = set()
        unique_terms = []
        for term in all_terms:
            if term not in seen:
                seen.add(term)
                unique_terms.append(term)
        
        # Step 4: Reconstruct query
        # If we expanded, use expanded version; otherwise keep original
        if len(unique_terms) > len(words):
            # Use expanded query
            expanded_query = ' '.join(unique_terms)
            # Keep original query first, then add expansions
            # This ensures original terms have higher weight
            final_query = f"{original_query} {' '.join([t for t in unique_terms if t not in words])}"
        else:
            final_query = original_query
        
        return final_query.strip()
    
    def get_expanded_terms(self, query: str) -> List[str]:
        """
        Get list of all expanded terms for a query
        Useful for debugging or advanced use cases
        """
        preprocessed = self.preprocess(query)
        return preprocessed.split()
    
    def is_abbreviation(self, term: str) -> bool:
        """Check if a term is a known abbreviation"""
        clean_term = re.sub(r'[^\w]', '', term.lower())
        return clean_term in self.abbreviations

