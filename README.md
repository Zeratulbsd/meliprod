API de Frecuencia de Términos
Challenge MercadoLibre - Raul Vilchis
Sistema para obtener la frecuencia de términos en una colección de documentos a través de una API REST.
🚀 Características

API REST para consultar frecuencia de términos
Búsqueda en documento específico o en toda la colección
Normalización de texto (minúsculas, sin acentos)
Cache integrado para mejor rendimiento
Logs estructurados para monitoreo
Deployment ready con  Heroku
Escalable y preparado para alta disponibilidad

📋 Endpoints
Obtener frecuencia de término
bash# Frecuencia en documento específico
GET /?term=casa&doc_name=5985-8.txt
Response: {"frecuencia": 223, "term": "casa", "document": "5985-8.txt"}

# Frecuencia en toda la colección
GET /?term=auto
Response: {"frecuencia": 1050, "term": "auto", "scope": "global"}
Endpoints adicionales
bash# Health check
GET /health

# Estadísticas del sistema
GET /stats



API Layer: Flask con endpoints RESTful
Processing Layer: Clase DocumentProcessor para análisis de texto
Caching Layer: Redis/Memory cache para optimización
Storage Layer: Sistema de archivos para documentos
Monitoring: Logs estructurados y health checks