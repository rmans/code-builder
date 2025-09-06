#!/usr/bin/env python3
"""
Cursor Bridge Server

A Flask server that bridges Cursor with the Code Builder evaluation system.
Serves evaluation prompts and receives responses via HTTP endpoints.
"""

import os
import json
import uuid
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from flask import Flask, request, jsonify, render_template_string
import click

# Add parent directory to path for imports
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from evaluators.objective import evaluate_code, evaluate_doc
from evaluators.artifact_detector import detect_artifact_type
from config.prompts.evaluation_prompt import build_single_eval_prompt, build_abc_eval_prompt

app = Flask(__name__)

# In-memory storage for active evaluations
evaluations: Dict[str, Dict[str, Any]] = {}

# Server configuration
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5000
BASE_URL = f"http://{SERVER_HOST}:{SERVER_PORT}"

def ensure_cache_dir():
    """Ensure the evaluations cache directory exists"""
    cache_dir = Path("builder/cache/evaluations")
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir

def save_evaluation(eval_id: str, data: Dict[str, Any]):
    """Save evaluation data to file"""
    cache_dir = ensure_cache_dir()
    file_path = cache_dir / f"{eval_id}.json"
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def load_evaluation(eval_id: str) -> Optional[Dict[str, Any]]:
    """Load evaluation data from file"""
    cache_dir = ensure_cache_dir()
    file_path = cache_dir / f"{eval_id}.json"
    
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

@app.route('/')
def index():
    """Home page with server status"""
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Code Builder - Cursor Bridge</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .status { color: green; font-weight: bold; }
            .endpoint { background: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 4px; }
            .code { background: #e8e8e8; padding: 2px 4px; border-radius: 2px; }
        </style>
    </head>
    <body>
        <h1>Code Builder - Cursor Bridge Server</h1>
        <p class="status">✅ Server is running</p>
        
        <h2>Active Evaluations</h2>
        {% if evaluations %}
            {% for eval_id, data in evaluations.items() %}
            <div class="endpoint">
                <strong>{{ eval_id }}</strong><br>
                Type: {{ data.get('type', 'unknown') }}<br>
                Path: {{ data.get('path', 'unknown') }}<br>
                <a href="/prompt/{{ eval_id }}">View Prompt</a>
            </div>
            {% endfor %}
        {% else %}
            <p>No active evaluations</p>
        {% endif %}
        
        <h2>API Endpoints</h2>
        <div class="endpoint">
            <strong>GET /prompt/&lt;eval_id&gt;</strong><br>
            Get evaluation prompt for Cursor
        </div>
        <div class="endpoint">
            <strong>POST /response/&lt;eval_id&gt;</strong><br>
            Submit Cursor evaluation response
        </div>
    </body>
    </html>
    """, evaluations=evaluations)

@app.route('/prompt/<eval_id>')
def get_prompt(eval_id: str):
    """Get evaluation prompt for the given evaluation ID"""
    if eval_id not in evaluations:
        return jsonify({"error": "Evaluation not found"}), 404
    
    eval_data = evaluations[eval_id]
    prompt = eval_data.get('prompt', '')
    
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Evaluation Prompt - {{ eval_id }}</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .prompt { background: #f9f9f9; padding: 20px; border-radius: 8px; white-space: pre-wrap; }
            .copy-btn { background: #007cba; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
            .copy-btn:hover { background: #005a87; }
        </style>
    </head>
    <body>
        <h1>Evaluation Prompt</h1>
        <p><strong>Evaluation ID:</strong> {{ eval_id }}</p>
        <p><strong>Type:</strong> {{ eval_data.get('type', 'unknown') }}</p>
        <p><strong>Path:</strong> {{ eval_data.get('path', 'unknown') }}</p>
        
        <button class="copy-btn" onclick="copyPrompt()">Copy to Clipboard</button>
        
        <div class="prompt" id="prompt">{{ prompt }}</div>
        
        <script>
            function copyPrompt() {
                const promptText = document.getElementById('prompt').textContent;
                navigator.clipboard.writeText(promptText).then(() => {
                    alert('Prompt copied to clipboard!');
                });
            }
        </script>
    </body>
    </html>
    """, eval_id=eval_id, eval_data=eval_data, prompt=prompt)

@app.route('/response/<eval_id>', methods=['POST'])
def submit_response(eval_id: str):
    """Submit Cursor evaluation response"""
    if eval_id not in evaluations:
        return jsonify({"error": "Evaluation not found"}), 404
    
    try:
        response_data = request.get_json()
        if not response_data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Update evaluation with response
        evaluations[eval_id]['response'] = response_data
        evaluations[eval_id]['completed_at'] = datetime.now().isoformat()
        
        # Save to file
        save_evaluation(eval_id, evaluations[eval_id])
        
        # Auto-complete if this is a single evaluation
        if evaluations[eval_id].get('type') == 'single':
            complete_single_evaluation(eval_id)
        
        return jsonify({
            "status": "success",
            "message": "Response received and processed",
            "eval_id": eval_id
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to process response: {str(e)}"}), 500

def complete_single_evaluation(eval_id: str):
    """Complete a single evaluation by merging objective and subjective scores"""
    try:
        eval_data = evaluations[eval_id]
        artifact_path = eval_data['path']
        artifact_type = eval_data['artifact_type']
        objective_scores = eval_data['objective_scores']
        subjective_response = eval_data['response']
        
        # Load configuration for weights
        import yaml
        with open('docs/eval/config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        # Merge evaluations
        from utils.cursor_bridge import merge_evaluations
        final_scores = merge_evaluations(
            objective_scores, 
            subjective_response, 
            config['artifact_weights'][artifact_type]
        )
        
        # Save final evaluation
        final_eval = {
            "artifact_path": artifact_path,
            "artifact_type": artifact_type,
            "objective_scores": objective_scores,
            "subjective_scores": subjective_response,
            "final_scores": final_scores,
            "completed_at": datetime.now().isoformat()
        }
        
        # Save to cache
        cache_dir = ensure_cache_dir()
        final_file = cache_dir / f"final_{eval_id}.json"
        with open(final_file, 'w', encoding='utf-8') as f:
            json.dump(final_eval, f, indent=2)
        
        print(f"✅ Evaluation {eval_id} completed! Final score: {final_scores['overall_score']:.1f}")
        print(f"📁 Results saved to: {final_file}")
        
    except Exception as e:
        print(f"❌ Failed to complete evaluation {eval_id}: {e}")

def start_server(host: str = SERVER_HOST, port: int = SERVER_PORT, debug: bool = False):
    """Start the Flask server"""
    print(f"🚀 Starting Cursor Bridge Server...")
    print(f"📍 Server URL: {BASE_URL}")
    print(f"🔗 Open in browser: {BASE_URL}")
    print(f"⏹️  Press Ctrl+C to stop")
    
    app.run(host=host, port=port, debug=debug, use_reloader=False)

def create_evaluation(artifact_path: str, eval_type: str = "single", **kwargs) -> str:
    """Create a new evaluation and return its ID"""
    eval_id = str(uuid.uuid4())[:8]
    
    # Detect artifact type
    artifact_type = detect_artifact_type(artifact_path)
    
    # Run objective evaluation
    try:
        if artifact_type == 'code':
            objective_scores = evaluate_code(artifact_path)
        else:
            objective_scores = evaluate_doc(artifact_path, artifact_type)
    except Exception as e:
        print(f"⚠️  Objective evaluation failed: {e}")
        objective_scores = {"overall": 50.0, "error": str(e)}
    
    # Generate prompt
    if eval_type == "single":
        prompt = build_single_eval_prompt(artifact_path, artifact_type)
    elif eval_type == "abc":
        variants = kwargs.get('variants', {})
        prompt = build_abc_eval_prompt(variants, objective_scores)
    else:
        prompt = f"Evaluate: {artifact_path}"
    
    # Store evaluation
    eval_data = {
        "id": eval_id,
        "type": eval_type,
        "path": artifact_path,
        "artifact_type": artifact_type,
        "objective_scores": objective_scores,
        "prompt": prompt,
        "created_at": datetime.now().isoformat()
    }
    
    evaluations[eval_id] = eval_data
    save_evaluation(eval_id, eval_data)
    
    return eval_id

@click.command()
@click.option('--host', default=SERVER_HOST, help='Server host')
@click.option('--port', default=SERVER_PORT, help='Server port')
@click.option('--debug', is_flag=True, help='Enable debug mode')
def main(host: str, port: int, debug: bool):
    """Start the Cursor Bridge Server"""
    start_server(host, port, debug)

if __name__ == '__main__':
    main()
