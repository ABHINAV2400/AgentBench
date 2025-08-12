from flask import Flask, request, jsonify
import json
import random
import time
from datetime import datetime, timedelta
import requests

app = Flask(__name__)

# Mock APIs and tools
mock_databases = {
    "user_db": {
        "users": [
            {"id": 1, "name": "John Doe", "email": "john@example.com", "age": 30},
            {"id": 2, "name": "Jane Smith", "email": "jane@example.com", "age": 25},
            {"id": 3, "name": "Bob Johnson", "email": "bob@example.com", "age": 35}
        ]
    },
    "product_db": {
        "products": [
            {"id": 1, "name": "Laptop", "price": 999.99, "category": "Electronics", "stock": 50},
            {"id": 2, "name": "Phone", "price": 599.99, "category": "Electronics", "stock": 100},
            {"id": 3, "name": "Book", "price": 19.99, "category": "Education", "stock": 200}
        ]
    }
}

tool_usage_log = []

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "tool_bench_mock_server"})

# File system operations
@app.route('/api/file/read', methods=['POST'])
def read_file():
    data = request.get_json()
    filepath = data.get('filepath', '')
    
    log_tool_usage('file_read', {'filepath': filepath})
    
    # Mock file contents
    mock_files = {
        '/data/config.json': '{"app_name": "TestApp", "version": "1.0", "debug": true}',
        '/logs/app.log': '2024-01-01 INFO: Application started\n2024-01-01 ERROR: Connection failed\n2024-01-01 INFO: Retry successful',
        '/data/users.csv': 'id,name,email\n1,John Doe,john@example.com\n2,Jane Smith,jane@example.com'
    }
    
    if filepath in mock_files:
        return jsonify({
            "success": True,
            "filepath": filepath,
            "content": mock_files[filepath],
            "size": len(mock_files[filepath])
        })
    else:
        return jsonify({
            "success": False,
            "error": "File not found",
            "filepath": filepath
        }), 404

@app.route('/api/file/write', methods=['POST'])
def write_file():
    data = request.get_json()
    filepath = data.get('filepath', '')
    content = data.get('content', '')
    
    log_tool_usage('file_write', {'filepath': filepath, 'content_length': len(content)})
    
    return jsonify({
        "success": True,
        "filepath": filepath,
        "bytes_written": len(content),
        "message": "File written successfully"
    })

@app.route('/api/file/list', methods=['POST'])
def list_files():
    data = request.get_json()
    directory = data.get('directory', '/')
    
    log_tool_usage('file_list', {'directory': directory})
    
    # Mock file listings
    mock_listings = {
        '/': ['data', 'logs', 'config'],
        '/data': ['config.json', 'users.csv', 'backup.sql'],
        '/logs': ['app.log', 'error.log', 'access.log'],
        '/config': ['settings.ini', 'database.conf']
    }
    
    files = mock_listings.get(directory, [])
    return jsonify({
        "success": True,
        "directory": directory,
        "files": files,
        "count": len(files)
    })

# Database operations
@app.route('/api/database/query', methods=['POST'])
def database_query():
    data = request.get_json()
    db_name = data.get('database', 'user_db')
    query_type = data.get('query_type', 'SELECT')
    table = data.get('table', '')
    conditions = data.get('conditions', {})
    
    log_tool_usage('database_query', {
        'database': db_name,
        'query_type': query_type,
        'table': table
    })
    
    if db_name not in mock_databases:
        return jsonify({"success": False, "error": "Database not found"}), 404
    
    db = mock_databases[db_name]
    
    if query_type == 'SELECT':
        if table in db:
            results = db[table]
            # Apply simple filtering
            if conditions:
                for key, value in conditions.items():
                    results = [item for item in results if item.get(key) == value]
            
            return jsonify({
                "success": True,
                "results": results,
                "count": len(results)
            })
    
    return jsonify({"success": False, "error": "Query not supported"})

@app.route('/api/database/insert', methods=['POST'])
def database_insert():
    data = request.get_json()
    db_name = data.get('database', 'user_db')
    table = data.get('table', '')
    record = data.get('record', {})
    
    log_tool_usage('database_insert', {
        'database': db_name,
        'table': table,
        'record_keys': list(record.keys())
    })
    
    if db_name in mock_databases and table in mock_databases[db_name]:
        # Generate new ID
        existing_records = mock_databases[db_name][table]
        new_id = max(item.get('id', 0) for item in existing_records) + 1
        record['id'] = new_id
        existing_records.append(record)
        
        return jsonify({
            "success": True,
            "inserted_id": new_id,
            "record": record
        })
    
    return jsonify({"success": False, "error": "Database or table not found"}), 404

# HTTP/API operations
@app.route('/api/http/get', methods=['POST'])
def http_get():
    data = request.get_json()
    url = data.get('url', '')
    headers = data.get('headers', {})
    
    log_tool_usage('http_get', {'url': url})
    
    # Mock different API responses
    mock_responses = {
        'https://api.weather.com/current': {
            "temperature": 22,
            "condition": "sunny",
            "humidity": 65
        },
        'https://api.github.com/user': {
            "login": "testuser",
            "id": 12345,
            "public_repos": 25
        },
        'https://jsonplaceholder.typicode.com/posts/1': {
            "userId": 1,
            "id": 1,
            "title": "Test Post",
            "body": "This is a test post body"
        }
    }
    
    if url in mock_responses:
        return jsonify({
            "success": True,
            "url": url,
            "status_code": 200,
            "data": mock_responses[url]
        })
    else:
        return jsonify({
            "success": True,
            "url": url,
            "status_code": 200,
            "data": {"message": f"Mock response for {url}"}
        })

@app.route('/api/http/post', methods=['POST'])
def http_post():
    data = request.get_json()
    url = data.get('url', '')
    payload = data.get('payload', {})
    headers = data.get('headers', {})
    
    log_tool_usage('http_post', {'url': url, 'payload_keys': list(payload.keys())})
    
    return jsonify({
        "success": True,
        "url": url,
        "status_code": 201,
        "response": {
            "message": "Data posted successfully",
            "id": random.randint(1000, 9999),
            "posted_data": payload
        }
    })

# Data processing operations
@app.route('/api/data/process', methods=['POST'])
def process_data():
    data = request.get_json()
    operation = data.get('operation', 'filter')
    dataset = data.get('dataset', [])
    parameters = data.get('parameters', {})
    
    log_tool_usage('data_process', {
        'operation': operation,
        'dataset_size': len(dataset),
        'parameters': list(parameters.keys())
    })
    
    if operation == 'filter':
        condition = parameters.get('condition', lambda x: True)
        # Simple filtering based on parameters
        if 'min_value' in parameters:
            min_val = parameters['min_value']
            filtered = [item for item in dataset if isinstance(item, (int, float)) and item >= min_val]
        else:
            filtered = dataset
        
        return jsonify({
            "success": True,
            "operation": operation,
            "original_count": len(dataset),
            "filtered_count": len(filtered),
            "result": filtered
        })
    
    elif operation == 'aggregate':
        if all(isinstance(item, (int, float)) for item in dataset):
            result = {
                "sum": sum(dataset),
                "average": sum(dataset) / len(dataset) if dataset else 0,
                "min": min(dataset) if dataset else None,
                "max": max(dataset) if dataset else None,
                "count": len(dataset)
            }
        else:
            result = {"count": len(dataset)}
        
        return jsonify({
            "success": True,
            "operation": operation,
            "result": result
        })
    
    return jsonify({"success": False, "error": "Unsupported operation"})

# System operations
@app.route('/api/system/info', methods=['POST'])
def system_info():
    log_tool_usage('system_info', {})
    
    return jsonify({
        "success": True,
        "system": {
            "os": "Linux",
            "cpu_count": 4,
            "memory_gb": 16,
            "disk_space_gb": 500,
            "uptime_hours": 24.5,
            "load_average": 0.75
        }
    })

@app.route('/api/system/execute', methods=['POST'])
def system_execute():
    data = request.get_json()
    command = data.get('command', '')
    
    log_tool_usage('system_execute', {'command': command})
    
    # Mock command outputs
    mock_outputs = {
        'ls -la': 'total 24\ndrwxr-xr-x 3 user user 4096 Jan 1 12:00 .\ndrwxr-xr-x 5 user user 4096 Jan 1 11:00 ..\n-rw-r--r-- 1 user user 1024 Jan 1 12:00 file.txt',
        'ps aux': 'USER PID %CPU %MEM VSZ RSS TTY STAT START TIME COMMAND\nroot 1 0.0 0.1 225488 8760 ? Ss Jan01 0:02 /sbin/init',
        'df -h': 'Filesystem Size Used Avail Use% Mounted on\n/dev/sda1 100G 45G 50G 48% /',
        'uptime': '12:34:56 up 1 day, 30 min, 1 user, load average: 0.75, 0.65, 0.50'
    }
    
    output = mock_outputs.get(command, f"Mock output for: {command}")
    
    return jsonify({
        "success": True,
        "command": command,
        "output": output,
        "return_code": 0
    })

# Tool usage analytics
@app.route('/api/tools/usage')
def get_tool_usage():
    return jsonify({
        "total_calls": len(tool_usage_log),
        "usage_log": tool_usage_log[-20:],  # Last 20 calls
        "tool_counts": count_tool_usage()
    })

@app.route('/api/tools/reset', methods=['POST'])
def reset_tool_usage():
    global tool_usage_log
    tool_usage_log = []
    return jsonify({"message": "Tool usage log reset"})

def log_tool_usage(tool_name, parameters):
    """Log tool usage for analytics."""
    tool_usage_log.append({
        "tool": tool_name,
        "parameters": parameters,
        "timestamp": datetime.now().isoformat()
    })

def count_tool_usage():
    """Count usage by tool type."""
    counts = {}
    for entry in tool_usage_log:
        tool = entry["tool"]
        counts[tool] = counts.get(tool, 0) + 1
    return counts

# Multi-step workflow endpoint
@app.route('/api/workflow/execute', methods=['POST'])
def execute_workflow():
    data = request.get_json()
    steps = data.get('steps', [])
    
    log_tool_usage('workflow_execute', {'step_count': len(steps)})
    
    results = []
    for i, step in enumerate(steps):
        tool = step.get('tool', '')
        params = step.get('parameters', {})
        
        # Mock step execution
        step_result = {
            "step": i + 1,
            "tool": tool,
            "success": True,
            "result": f"Executed {tool} with parameters: {params}",
            "duration_ms": random.randint(100, 2000)
        }
        results.append(step_result)
    
    return jsonify({
        "workflow_success": True,
        "steps_completed": len(results),
        "results": results,
        "total_duration_ms": sum(r["duration_ms"] for r in results)
    })

def start_server():
    app.run(host='127.0.0.1', port=8006, debug=False, use_reloader=False)

if __name__ == "__main__":
    start_server()