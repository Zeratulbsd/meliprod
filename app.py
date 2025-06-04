#!/usr/bin/env python3
"""
Challenge MercadoLibre - Raul Vilchis
"""

import os
import re
import json
import logging
from collections import defaultdict, Counter
from pathlib import Path
from flask import Flask, request, jsonify
from flask_caching import Cache
import unicodedata

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Clase para procesar y gestionar documentos"""
    
    def __init__(self, documents_path="coleccion_2022"):
        self.documents_path = Path(documents_path)
        self.document_frequencies = {}
        self.global_frequency = Counter()
        self.processed = False
        
    def normalize_text(self, text):
        """Normalizar texto: minúsculas, sin acentos, solo letras y números"""
        # Convertir a minúsculas
        text = text.lower()
        # Remover acentos
        text = unicodedata.normalize('NFD', text)
        text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')
        # Extraer solo palabras (letras y números)
        words = re.findall(r'\b[a-zA-Z0-9]+\b', text)
        return words
    
    def process_document(self, file_path):
        """Procesar un documento individual"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
                words = self.normalize_text(content)
                return Counter(words)
        except Exception as e:
            logger.error(f"Error procesando {file_path}: {e}")
            return Counter()
    
    def load_documents(self):
        """Cargar y procesar todos los documentos"""
        if not self.documents_path.exists():
            logger.error(f"Directorio {self.documents_path} no encontrado")
            return
        
        logger.info("Iniciando procesamiento de documentos...")
        
        # Procesar cada documento
        for file_path in self.documents_path.glob("*.txt"):
            doc_name = file_path.name
            logger.info(f"Procesando {doc_name}...")
            
            doc_frequency = self.process_document(file_path)
            self.document_frequencies[doc_name] = doc_frequency
            
            # Actualizar frecuencia global
            self.global_frequency.update(doc_frequency)
        
        self.processed = True
        logger.info(f"Procesamiento completado. {len(self.document_frequencies)} documentos procesados")
    
    def get_term_frequency_in_document(self, doc_name, term):
        """Obtener frecuencia de un término en un documento específico"""
        if not self.processed:
            self.load_documents()
        
        term = term.lower()
        if doc_name in self.document_frequencies:
            return self.document_frequencies[doc_name].get(term, 0)
        return 0
    
    def get_term_frequency_global(self, term):
        """Obtener frecuencia de un término en toda la colección"""
        if not self.processed:
            self.load_documents()
        
        term = term.lower()
        return self.global_frequency.get(term, 0)
    
    def get_document_stats(self):
        """Obtener estadísticas de los documentos procesados"""
        if not self.processed:
            self.load_documents()
        
        total_docs = len(self.document_frequencies)
        total_unique_terms = len(self.global_frequency)
        total_terms = sum(self.global_frequency.values())
        
        return {
            'total_documents': total_docs,
            'total_unique_terms': total_unique_terms,
            'total_terms': total_terms,
            'documents': list(self.document_frequencies.keys())
        }

# Inicializar Flask app
app = Flask(__name__)

# Configurar cache
app.config['CACHE_TYPE'] = 'simple'
cache = Cache(app)

# Inicializar procesador de documentos
processor = DocumentProcessor()

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de health check"""
    return jsonify({
        'status': 'healthy',
        'message': 'API funcionando correctamente'
    })

@app.route('/stats', methods=['GET'])
def get_stats():
    """Endpoint para obtener estadísticas del sistema"""
    stats = processor.get_document_stats()
    return jsonify(stats)

@app.route('/', methods=['GET'])
@cache.cached(timeout=60, query_string=True)
def get_term_frequency():
    """
    Endpoint principal para obtener frecuencia de términos
    
    Parámetros:
    - term: término a buscar (requerido)
    - doc_name: nombre del documento específico (opcional)
    
    Ejemplos:
    - /?term=casa&doc_name=5985-8.txt
    - /?term=auto
    """
    
    # Validar parámetros
    term = request.args.get('term')
    if not term:
        return jsonify({
            'error': 'Parámetro "term" es requerido'
        }), 400
    
    doc_name = request.args.get('doc_name')
    
    try:
        if doc_name:
            # Buscar en documento específico
            frequency = processor.get_term_frequency_in_document(doc_name, term)
            return jsonify({
                'frecuencia': frequency,
                'term': term,
                'document': doc_name
            })
        else:
            # Buscar en toda la colección
            frequency = processor.get_term_frequency_global(term)
            return jsonify({
                'frecuencia': frequency,
                'term': term,
                'scope': 'global'
            })
    
    except Exception as e:
        logger.error(f"Error procesando solicitud: {e}")
        return jsonify({
            'error': 'Error interno del servidor'
        }), 500

@app.route('/documents', methods=['GET'])
def list_documents():
    """Endpoint para listar documentos disponibles"""
    stats = processor.get_document_stats()
    return jsonify({
        'documents': stats['documents'],
        'total_count': stats['total_documents']
    })

@app.errorhandler(404)
def not_found(error):
    """Manejador para errores 404"""
    return jsonify({
        'error': 'Endpoint no encontrado',
        'available_endpoints': [
            'GET /?term=<term>&doc_name=<doc_name>',
            'GET /?term=<term>',
            'GET /health',
            'GET /stats',
            'GET /documents'
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Manejador para errores 500"""
    return jsonify({
        'error': 'Error interno del servidor'
    }), 500

if __name__ == '__main__':
    # Cargar documentos al iniciar
    processor.load_documents()
    
    # Configurar puerto
    port = int(os.environ.get('PORT', 5000))
    
    # Ejecutar aplicación
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.environ.get('FLASK_ENV') == 'development'
    )