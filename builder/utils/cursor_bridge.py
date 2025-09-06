#!/usr/bin/env python3
"""
Cursor bridge utilities for parsing responses and merging evaluations.
Handles JSON extraction from markdown and clipboard monitoring.
"""

import os
import json
import re
import time
from typing import Dict, Any, Optional, Union
from pathlib import Path

# Optional dependency for clipboard monitoring
try:
    import pyperclip  # type: ignore
    HAS_PYPERCLIP = True
except ImportError:
    HAS_PYPERCLIP = False

ROOT = os.path.dirname(os.path.dirname(__file__))
CONFIG_PATH = os.path.join(ROOT, "docs", "eval", "config.yaml")

def load_config() -> Dict[str, Any]:
    """Load evaluation configuration"""
    try:
        import yaml
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception:
        return {}

def extract_json_from_markdown(content: str) -> Optional[Dict[str, Any]]:
    """Extract JSON from markdown content (like Cursor responses)"""
    # Look for JSON code blocks
    json_patterns = [
        r'```json\s*\n(.*?)\n```',  # ```json ... ```
        r'```\s*\n(\{.*?\})\n```',  # ``` ... ``` (generic)
        r'```\s*\n(\[.*?\])\n```',  # ``` ... ``` (array)
    ]
    
    for pattern in json_patterns:
        matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
        for match in matches:
            try:
                return json.loads(match.strip())
            except json.JSONDecodeError:
                continue
    
    # Look for raw JSON in the content
    json_start = content.find('{')
    if json_start != -1:
        json_end = content.rfind('}') + 1
        if json_end > json_start:
            try:
                json_str = content[json_start:json_end]
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass
    
    return None

def validate_evaluation_schema(data: Dict[str, Any]) -> bool:
    """Validate that the data matches expected evaluation schema"""
    required_fields = ['overall_score']
    
    # Check for single evaluation format
    if all(field in data for field in required_fields):
        return True
    
    # Check for ABC evaluation format
    if 'variant_scores' in data and 'winner' in data:
        return True
    
    # Check for pairwise evaluation format
    if 'artifact_a' in data and 'artifact_b' in data and 'winner' in data:
        return True
    
    return False

def parse_cursor_response(clipboard_or_file: Union[str, Path]) -> Dict[str, Any]:
    """
    Parse Cursor response from clipboard text or file.
    Handles both raw JSON and JSON embedded in markdown.
    
    Args:
        clipboard_or_file: Either clipboard content string or file path
        
    Returns:
        Parsed evaluation data
        
    Raises:
        ValueError: If no valid JSON found or schema validation fails
    """
    # Read content
    if isinstance(clipboard_or_file, (str, Path)) and os.path.exists(str(clipboard_or_file)):
        with open(clipboard_or_file, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = str(clipboard_or_file)
    
    # Extract JSON
    data = extract_json_from_markdown(content)
    if not data:
        raise ValueError("No valid JSON found in the provided content")
    
    # Validate schema
    if not validate_evaluation_schema(data):
        raise ValueError("JSON does not match expected evaluation schema")
    
    return data

def watch_for_cursor(poll_interval: float = 1.0, timeout: float = 60.0) -> Optional[Dict[str, Any]]:
    """
    Monitor clipboard for Cursor JSON response.
    
    Args:
        poll_interval: How often to check clipboard (seconds)
        timeout: Maximum time to wait (seconds)
        
    Returns:
        Parsed evaluation data or None if timeout
    """
    if not HAS_PYPERCLIP:
        print("Warning: pyperclip not available. Install with: pip install pyperclip")
        return None
    
    start_time = time.time()
    last_content = ""
    
    print(f"Watching clipboard for Cursor response (timeout: {timeout}s)...")
    
    while time.time() - start_time < timeout:
        try:
            current_content = pyperclip.paste()
            
            # Check if content changed and contains JSON
            if current_content != last_content and ('{' in current_content or '[' in current_content):
                try:
                    data = parse_cursor_response(current_content)
                    print("✅ Valid Cursor response detected!")
                    return data
                except ValueError:
                    # Not a valid evaluation response, continue watching
                    pass
            
            last_content = current_content
            time.sleep(poll_interval)
            
        except Exception as e:
            print(f"Error monitoring clipboard: {e}")
            time.sleep(poll_interval)
    
    print("⏰ Timeout reached - no valid Cursor response detected")
    return None

def merge_evaluations(objective: Dict[str, Any], subjective: Dict[str, Any], 
                     weights: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
    """
    Merge objective and subjective evaluations using config weights.
    
    Args:
        objective: Objective scores from automated tools
        subjective: Subjective scores from Cursor evaluation
        weights: Custom weights (uses config if not provided)
        
    Returns:
        Blended evaluation with confidence bounds
    """
    # Load weights from config
    if weights is None:
        config = load_config()
        artifact_type = objective.get('artifact_type', 'code')
        artifact_weights = config.get('artifact_weights', {}).get(artifact_type, {
            'objective': 0.7, 
            'subjective': 0.3
        })
    else:
        artifact_weights = weights
    
    # Extract scores
    obj_scores = objective.get('scores', {})
    subj_scores = subjective.get('dimensions', {})
    
    # Calculate blended scores
    blended_scores = {}
    confidence_factors = []
    
    for dimension in subj_scores.keys():
        if dimension in obj_scores:
            obj_score = obj_scores[dimension]
            subj_score = subj_scores[dimension]
            
            # Weighted blend
            blended = (obj_score * artifact_weights['objective'] + 
                      subj_score * artifact_weights['subjective'])
            blended_scores[dimension] = blended
            
            # Calculate confidence factor (how close objective and subjective are)
            score_diff = abs(obj_score - subj_score)
            confidence = max(0, 1 - (score_diff / 100))  # Normalize to 0-1
            confidence_factors.append(confidence)
        else:
            # Use subjective score if no objective equivalent
            blended_scores[dimension] = subj_scores[dimension]
            confidence_factors.append(0.5)  # Medium confidence for subjective-only
    
    # Calculate overall blended score
    obj_overall = obj_scores.get('overall', 50)
    subj_overall = subjective.get('overall_score', 50)
    overall_blended = (obj_overall * artifact_weights['objective'] + 
                      subj_overall * artifact_weights['subjective'])
    
    # Calculate confidence bounds
    avg_confidence = sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.5
    confidence_interval = 10 * (1 - avg_confidence)  # Wider interval for lower confidence
    
    return {
        'artifact_path': objective.get('artifact_path', ''),
        'artifact_type': objective.get('artifact_type', 'code'),
        'objective_scores': obj_scores,
        'subjective_scores': subj_scores,
        'blended_scores': blended_scores,
        'overall_score': overall_blended,
        'confidence': avg_confidence,
        'confidence_interval': confidence_interval,
        'weights': artifact_weights,
        'reasoning': subjective.get('reasoning', ''),
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S')
    }

def test_parsing():
    """Test the parsing functionality with sample data"""
    print("🧪 Testing Cursor Bridge Parsing")
    print("="*50)
    
    # Test 1: Raw JSON
    raw_json = '{"overall_score": 85.2, "dimensions": {"clarity": 82, "design": 88}}'
    try:
        result = parse_cursor_response(raw_json)
        print("✅ Raw JSON parsing: SUCCESS")
        print(f"   Overall score: {result.get('overall_score', 'N/A')}")
    except Exception as e:
        print(f"❌ Raw JSON parsing: FAILED - {e}")
    
    # Test 2: Markdown with JSON
    markdown_content = """
    Here's my evaluation:
    
    ```json
    {
      "overall_score": 91.7,
      "dimensions": {
        "clarity": 89,
        "design": 93,
        "maintainability": 88
      }
    }
    ```
    
    This code shows excellent quality.
    """
    try:
        result = parse_cursor_response(markdown_content)
        print("✅ Markdown JSON parsing: SUCCESS")
        print(f"   Overall score: {result.get('overall_score', 'N/A')}")
    except Exception as e:
        print(f"❌ Markdown JSON parsing: FAILED - {e}")
    
    # Test 3: Merge evaluations
    objective = {
        'artifact_path': 'src/hello.ts',
        'artifact_type': 'code',
        'scores': {'clarity': 80, 'design': 85, 'overall': 82.5}
    }
    subjective = {
        'overall_score': 90,
        'dimensions': {'clarity': 85, 'design': 95},
        'reasoning': 'Excellent code quality'
    }
    
    try:
        merged = merge_evaluations(objective, subjective)
        print("✅ Evaluation merging: SUCCESS")
        print(f"   Blended overall: {merged['overall_score']:.1f}")
        print(f"   Confidence: {merged['confidence']:.2f}")
    except Exception as e:
        print(f"❌ Evaluation merging: FAILED - {e}")
    
    print("="*50)

if __name__ == "__main__":
    test_parsing()
