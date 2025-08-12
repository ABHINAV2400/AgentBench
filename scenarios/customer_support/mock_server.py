from flask import Flask, jsonify, request
import sqlite3
import os
import json
from datetime import datetime

DATABASE_FILE = 'customer_support_tickets.db'
TRACKING_FILE = 'ai_actions_tracking.json'
app = Flask(__name__)

# Global tracking system for AI actions
ai_action_tracker = {
    'api_calls': [],
    'database_changes': [],
    'workflow_states': [],
    'start_time': None,
    'end_time': None
}

def log_api_call(endpoint, method, payload=None, response_data=None):
    """Track all API calls made by the AI agent"""
    call_data = {
        'timestamp': datetime.now().isoformat(),
        'endpoint': endpoint,
        'method': method,
        'payload': payload,
        'response': response_data
    }
    ai_action_tracker['api_calls'].append(call_data)

def log_database_change(table, record_id, field, old_value, new_value):
    """Track all database modifications"""
    change_data = {
        'timestamp': datetime.now().isoformat(),
        'table': table,
        'record_id': record_id,
        'field': field,
        'old_value': old_value,
        'new_value': new_value
    }
    ai_action_tracker['database_changes'].append(change_data)

def log_workflow_state(state, description, success=True):
    """Track AI workflow progression"""
    state_data = {
        'timestamp': datetime.now().isoformat(),
        'state': state,
        'description': description,
        'success': success
    }
    ai_action_tracker['workflow_states'].append(state_data)

def get_database_snapshot():
    """Get current state of all tickets for comparison"""
    connection = sqlite3.connect(DATABASE_FILE)
    cursor = connection.cursor()
    rows = cursor.execute('SELECT id, customer_name, issue_description, status FROM tickets').fetchall()
    connection.close()
    
    return {
        'tickets': [
            {
                'id': row[0],
                'customer_name': row[1], 
                'issue_description': row[2], 
                'status': row[3]
            } 
            for row in rows
        ]
    }

def reset_tracking():
    """Reset tracking for new test"""
    global ai_action_tracker
    ai_action_tracker = {
        'api_calls': [],
        'database_changes': [],
        'workflow_states': [],
        'start_time': datetime.now().isoformat(),
        'end_time': None,
        'initial_database_state': get_database_snapshot()
    }

def setup_database():
    """Initialize the customer support ticket database"""
    if os.path.exists(DATABASE_FILE):
        return
    
    connection = sqlite3.connect(DATABASE_FILE)
    cursor = connection.cursor()
    
    # Create tickets table
    cursor.execute('''
        CREATE TABLE tickets (
            id INTEGER PRIMARY KEY, 
            customer_name TEXT, 
            issue_description TEXT, 
            status TEXT
        )
    ''')
    
    # Add sample tickets
    sample_tickets = [
        ('Alice', 'My product arrived broken', 'open'),
        ('Bob', 'I need an invoice for order 1234', 'open')
    ]
    
    cursor.executemany(
        "INSERT INTO tickets (customer_name, issue_description, status) VALUES (?, ?, ?)", 
        sample_tickets
    )
    
    connection.commit()
    connection.close()

@app.route('/api/tickets', methods=['GET'])
def get_all_tickets():
    """Retrieve all customer support tickets"""
    # Log this API call for tracking
    log_api_call('/api/tickets', 'GET')
    log_workflow_state('fetch_tickets', 'AI fetched all tickets to identify open issues')
    
    connection = sqlite3.connect(DATABASE_FILE)
    cursor = connection.cursor()
    
    rows = cursor.execute('SELECT id, customer_name, issue_description, status FROM tickets').fetchall()
    connection.close()
    
    tickets = [
        {
            'id': row[0],
            'customer_name': row[1], 
            'issue_description': row[2], 
            'status': row[3]
        } 
        for row in rows
    ]
    
    # Log the response data
    log_api_call('/api/tickets', 'GET', response_data={'ticket_count': len(tickets), 'tickets': tickets})
    
    return jsonify(tickets)

@app.route('/api/tickets/<int:ticket_id>/reply', methods=['POST'])
def reply_to_ticket(ticket_id):
    """Submit a reply to a customer support ticket"""
    request_data = request.json
    reply_message = request_data.get('reply', 'replied')
    
    # Get old status for tracking
    connection = sqlite3.connect(DATABASE_FILE)
    cursor = connection.cursor()
    old_status = cursor.execute('SELECT status FROM tickets WHERE id = ?', (ticket_id,)).fetchone()
    old_status_value = old_status[0] if old_status else 'unknown'
    
    # Log the API call and payload
    log_api_call(f'/api/tickets/{ticket_id}/reply', 'POST', 
                payload={'reply': reply_message})
    
    # Determine if this looks like a proper customer service response
    if any(keyword in reply_message.lower() for keyword in ['sorry', 'apologize', 'apology']):
        log_workflow_state('compose_response', f'AI composed appropriate apology-based response for ticket {ticket_id}')
    else:
        log_workflow_state('compose_response', f'AI composed response for ticket {ticket_id} (no apology detected)', success=False)
    
    log_workflow_state('submit_reply', f'AI submitted reply to ticket {ticket_id}')
    
    # Update the database
    cursor.execute('UPDATE tickets SET status = ? WHERE id = ?', (reply_message, ticket_id))
    connection.commit()
    connection.close()
    
    # Log the database change
    log_database_change('tickets', ticket_id, 'status', old_status_value, reply_message)
    
    response = {'success': True, 'message': 'Reply submitted successfully', 'ticket_id': ticket_id}
    
    # Log the response
    log_api_call(f'/api/tickets/{ticket_id}/reply', 'POST', 
                response_data=response)
    
    return jsonify(response)

@app.route('/tracking/actions', methods=['GET'])
def get_tracking_data():
    """Retrieve all tracked AI actions for evaluation"""
    # Mark end time when evaluation requests tracking data
    ai_action_tracker['end_time'] = datetime.now().isoformat()
    ai_action_tracker['final_database_state'] = get_database_snapshot()
    
    return jsonify(ai_action_tracker)

@app.route('/tracking/reset', methods=['POST'])
def reset_tracking_data():
    """Reset tracking data for new test"""
    reset_tracking()
    return jsonify({'status': 'tracking_reset', 'message': 'AI action tracking has been reset'})

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'customer_support_mock_server'})

if __name__ == '__main__':
    print("Starting Customer Support Mock Server...")
    setup_database()
    reset_tracking()  # Initialize tracking for new test
    app.run(host='127.0.0.1', port=8001, debug=False)