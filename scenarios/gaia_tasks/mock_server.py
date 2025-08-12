from flask import Flask, request, jsonify
import json
import random
import requests
from datetime import datetime, timedelta
import base64

app = Flask(__name__)

# Mock knowledge base and APIs
knowledge_base = {
    "companies": {
        "AAPL": {"name": "Apple Inc.", "sector": "Technology", "founded": 1976},
        "GOOGL": {"name": "Alphabet Inc.", "sector": "Technology", "founded": 1998},
        "TSLA": {"name": "Tesla Inc.", "sector": "Automotive", "founded": 2003}
    },
    "countries": {
        "US": {"population": 331000000, "capital": "Washington D.C.", "continent": "North America"},
        "JP": {"population": 126000000, "capital": "Tokyo", "continent": "Asia"},
        "DE": {"population": 83000000, "capital": "Berlin", "continent": "Europe"}
    },
    "movies": {
        "inception": {"year": 2010, "director": "Christopher Nolan", "rating": 8.8, "genre": "Sci-Fi"},
        "interstellar": {"year": 2014, "director": "Christopher Nolan", "rating": 8.6, "genre": "Sci-Fi"},
        "avatar": {"year": 2009, "director": "James Cameron", "rating": 7.8, "genre": "Action"}
    }
}

# Mock weather data
weather_data = {
    "New York": {"temp": 22, "condition": "sunny", "humidity": 60},
    "London": {"temp": 15, "condition": "rainy", "humidity": 80},
    "Tokyo": {"temp": 25, "condition": "cloudy", "humidity": 70}
}

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "gaia_tasks_mock_server"})

@app.route('/api/knowledge/search')
def search_knowledge():
    """Search the knowledge base."""
    query = request.args.get('q', '').lower()
    category = request.args.get('category', 'all')
    
    results = []
    
    if category in ['all', 'companies']:
        for symbol, info in knowledge_base["companies"].items():
            if query in info["name"].lower() or query in symbol.lower():
                results.append({
                    "type": "company",
                    "symbol": symbol,
                    "data": info
                })
    
    if category in ['all', 'countries']:
        for code, info in knowledge_base["countries"].items():
            if query in code.lower() or query in info["capital"].lower():
                results.append({
                    "type": "country", 
                    "code": code,
                    "data": info
                })
    
    if category in ['all', 'movies']:
        for title, info in knowledge_base["movies"].items():
            if query in title.lower() or query in info["director"].lower():
                results.append({
                    "type": "movie",
                    "title": title,
                    "data": info
                })
    
    return jsonify({"results": results, "query": query})

@app.route('/api/weather/<city>')
def get_weather(city):
    """Get weather information for a city."""
    if city in weather_data:
        return jsonify({
            "city": city,
            "weather": weather_data[city],
            "timestamp": datetime.now().isoformat()
        })
    return jsonify({"error": "City not found"}), 404

@app.route('/api/calculate', methods=['POST'])
def calculate():
    """Perform mathematical calculations."""
    data = request.get_json()
    expression = data.get('expression', '')
    
    try:
        # Simple eval (in real scenario would use safer parsing)
        result = eval(expression)
        return jsonify({
            "expression": expression,
            "result": result,
            "success": True
        })
    except Exception as e:
        return jsonify({
            "expression": expression,
            "error": str(e),
            "success": False
        })

@app.route('/api/translate', methods=['POST'])
def translate_text():
    """Mock translation service."""
    data = request.get_json()
    text = data.get('text', '')
    target_lang = data.get('target_lang', 'en')
    
    # Mock translations
    translations = {
        "hello": {"es": "hola", "fr": "bonjour", "de": "hallo"},
        "goodbye": {"es": "adiós", "fr": "au revoir", "de": "auf wiedersehen"},
        "thank you": {"es": "gracias", "fr": "merci", "de": "danke"}
    }
    
    text_lower = text.lower()
    if text_lower in translations and target_lang in translations[text_lower]:
        translated = translations[text_lower][target_lang]
    else:
        translated = f"[{target_lang.upper()}] {text}"
    
    return jsonify({
        "original": text,
        "translated": translated,
        "target_language": target_lang
    })

@app.route('/api/analyze_document', methods=['POST'])
def analyze_document():
    """Analyze uploaded document content."""
    data = request.get_json()
    content = data.get('content', '')
    analysis_type = data.get('type', 'summary')
    
    word_count = len(content.split())
    char_count = len(content)
    
    if analysis_type == 'summary':
        # Mock summarization
        sentences = content.split('.')[:3]  # First 3 sentences
        summary = '. '.join(sentences) + '.'
        
        return jsonify({
            "type": "summary",
            "summary": summary,
            "word_count": word_count,
            "char_count": char_count
        })
    
    elif analysis_type == 'sentiment':
        # Mock sentiment analysis
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'disappointing']
        
        content_lower = content.lower()
        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)
        
        if positive_count > negative_count:
            sentiment = "positive"
        elif negative_count > positive_count:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        return jsonify({
            "type": "sentiment",
            "sentiment": sentiment,
            "confidence": 0.75,
            "positive_indicators": positive_count,
            "negative_indicators": negative_count
        })
    
    return jsonify({"error": "Unsupported analysis type"}), 400

@app.route('/api/tasks/multi_step', methods=['POST'])
def handle_multi_step_task():
    """Handle complex multi-step tasks."""
    data = request.get_json()
    task_description = data.get('task', '')
    steps = data.get('steps', [])
    
    # Process each step
    results = []
    for i, step in enumerate(steps):
        step_result = {
            "step": i + 1,
            "action": step.get('action', ''),
            "completed": True,
            "result": f"Completed: {step.get('action', '')}"
        }
        results.append(step_result)
    
    return jsonify({
        "task": task_description,
        "steps_completed": len(results),
        "results": results,
        "success": True
    })

@app.route('/api/reasoning/chain', methods=['POST'])
def chain_reasoning():
    """Handle chain-of-thought reasoning tasks."""
    data = request.get_json()
    question = data.get('question', '')
    context = data.get('context', '')
    
    # Mock reasoning chain
    reasoning_steps = [
        f"Understanding the question: {question}",
        f"Analyzing provided context: {context[:50]}..." if context else "No context provided",
        "Applying logical reasoning",
        "Formulating answer based on analysis"
    ]
    
    # Mock answer generation
    answer = f"Based on the analysis, the answer involves multiple factors from the given context."
    
    return jsonify({
        "question": question,
        "reasoning_chain": reasoning_steps,
        "answer": answer,
        "confidence": 0.8
    })

@app.route('/api/data/process', methods=['POST'])  
def process_data():
    """Process and analyze data."""
    data = request.get_json()
    dataset = data.get('data', [])
    operation = data.get('operation', 'statistics')
    
    if not dataset:
        return jsonify({"error": "No data provided"}), 400
    
    if operation == 'statistics':
        numeric_data = [x for x in dataset if isinstance(x, (int, float))]
        if numeric_data:
            stats = {
                "count": len(numeric_data),
                "sum": sum(numeric_data),
                "mean": sum(numeric_data) / len(numeric_data),
                "min": min(numeric_data),
                "max": max(numeric_data)
            }
        else:
            stats = {"error": "No numeric data found"}
        
        return jsonify({
            "operation": operation,
            "input_count": len(dataset),
            "statistics": stats
        })
    
    elif operation == 'filter':
        condition = data.get('condition', 'positive')
        if condition == 'positive':
            filtered = [x for x in dataset if isinstance(x, (int, float)) and x > 0]
        else:
            filtered = dataset
        
        return jsonify({
            "operation": operation,
            "condition": condition,
            "original_count": len(dataset),
            "filtered_count": len(filtered),
            "filtered_data": filtered[:10]  # First 10 items
        })
    
    return jsonify({"error": "Unsupported operation"}), 400

def start_server():
    app.run(host='127.0.0.1', port=8005, debug=False, use_reloader=False)

if __name__ == "__main__":
    start_server()