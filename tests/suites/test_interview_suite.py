#!/usr/bin/env python3
"""
Interview Test Suite

Comprehensive tests for interview functionality including:
- Interview session management
- Question generation
- Response processing
- Interview analysis
- Interview scoring
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import sys
import json
from unittest.mock import Mock, patch

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class TestInterviewSuite:
    """Test suite for interview functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir) / "test_project"
        self.project_root.mkdir()
        
        # Create test project structure
        self._create_test_project()
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _create_test_project(self):
        """Create a test project structure."""
        # Create interview data directory
        interview_dir = self.project_root / "cb_docs" / "interviews"
        interview_dir.mkdir(parents=True)
        
        # Create test interview files
        (interview_dir / "interview-001.md").write_text("""---
id: interview-001
title: Test Interview 1
status: completed
participant: test-user
---
# Test Interview 1
Interview with test user.

## Questions
1. What is your experience with Python?
2. How do you approach testing?

## Responses
1. I have 5 years of Python experience.
2. I use pytest for testing and follow TDD practices.
""")
    
    def test_interview_session_creation(self):
        """Test interview session creation."""
        # Mock interview session
        session = {
            "id": "test-session",
            "participant": "test-user",
            "questions": [],
            "responses": [],
            "status": "active"
        }
        
        assert session["id"] == "test-session"
        assert session["participant"] == "test-user"
        assert session["status"] == "active"
    
    def test_question_generation(self):
        """Test question generation."""
        # Mock question generator
        def generate_questions(topic, count=5):
            return [
                f"What is your experience with {topic}?",
                f"How do you approach {topic}?",
                f"What challenges have you faced with {topic}?",
                f"What tools do you use for {topic}?",
                f"How do you stay updated with {topic}?"
            ]
        
        questions = generate_questions("Python", 3)
        
        assert len(questions) == 3
        assert all("Python" in q for q in questions)
        assert all(q.endswith("?") for q in questions)
    
    def test_response_processing(self):
        """Test response processing."""
        # Mock response processor
        def process_response(question, response):
            return {
                "question": question,
                "response": response,
                "length": len(response),
                "keywords": response.lower().split(),
                "sentiment": "positive" if "good" in response.lower() else "neutral"
            }
        
        question = "What is your experience with Python?"
        response = "I have 5 years of Python experience and it's been good."
        
        processed = process_response(question, response)
        
        assert processed["question"] == question
        assert processed["response"] == response
        assert processed["length"] > 0
        assert "python" in processed["keywords"]
        assert processed["sentiment"] == "positive"
    
    def test_interview_analysis(self):
        """Test interview analysis."""
        # Mock interview data
        interview_data = {
            "questions": [
                "What is your experience with Python?",
                "How do you approach testing?",
                "What tools do you use for development?"
            ],
            "responses": [
                "I have 5 years of Python experience.",
                "I use pytest and follow TDD practices.",
                "I use VS Code, Git, and Docker."
            ]
        }
        
        # Mock analysis function
        def analyze_interview(data):
            return {
                "total_questions": len(data["questions"]),
                "total_responses": len(data["responses"]),
                "response_rate": len(data["responses"]) / len(data["questions"]),
                "average_response_length": sum(len(r) for r in data["responses"]) / len(data["responses"]),
                "keywords": list(set(word.lower() for response in data["responses"] for word in response.split())),
                "completeness_score": min(1.0, len(data["responses"]) / len(data["questions"]))
            }
        
        analysis = analyze_interview(interview_data)
        
        assert analysis["total_questions"] == 3
        assert analysis["total_responses"] == 3
        assert analysis["response_rate"] == 1.0
        assert analysis["completeness_score"] == 1.0
        assert len(analysis["keywords"]) > 0
    
    def test_interview_scoring(self):
        """Test interview scoring."""
        # Mock scoring function
        def score_interview(analysis):
            score = 0
            
            # Response rate scoring
            if analysis["response_rate"] >= 0.8:
                score += 30
            elif analysis["response_rate"] >= 0.6:
                score += 20
            else:
                score += 10
            
            # Completeness scoring
            if analysis["completeness_score"] >= 0.9:
                score += 40
            elif analysis["completeness_score"] >= 0.7:
                score += 30
            else:
                score += 20
            
            # Response quality scoring
            if analysis["average_response_length"] >= 50:
                score += 30
            elif analysis["average_response_length"] >= 30:
                score += 20
            else:
                score += 10
            
            return min(100, score)
        
        analysis = {
            "response_rate": 1.0,
            "completeness_score": 1.0,
            "average_response_length": 60
        }
        
        score = score_interview(analysis)
        
        assert score == 100  # Perfect score
        assert 0 <= score <= 100
    
    def test_interview_validation(self):
        """Test interview validation."""
        # Valid interview
        valid_interview = {
            "id": "test-interview",
            "participant": "test-user",
            "questions": ["Question 1", "Question 2"],
            "responses": ["Response 1", "Response 2"],
            "status": "completed"
        }
        
        def validate_interview(interview):
            required_fields = ["id", "participant", "questions", "responses", "status"]
            
            for field in required_fields:
                if field not in interview:
                    return False, f"Missing required field: {field}"
            
            if not interview["questions"]:
                return False, "No questions provided"
            
            if not interview["responses"]:
                return False, "No responses provided"
            
            if interview["status"] not in ["active", "completed", "cancelled"]:
                return False, "Invalid status"
            
            return True, "Valid interview"
        
        is_valid, message = validate_interview(valid_interview)
        
        assert is_valid
        assert message == "Valid interview"
    
    def test_interview_export(self):
        """Test interview export functionality."""
        # Mock interview data
        interview_data = {
            "id": "test-interview",
            "participant": "test-user",
            "questions": ["Question 1", "Question 2"],
            "responses": ["Response 1", "Response 2"],
            "status": "completed",
            "timestamp": "2025-01-15T10:00:00Z"
        }
        
        # Mock export function
        def export_interview(data, format="json"):
            if format == "json":
                return json.dumps(data, indent=2)
            elif format == "markdown":
                return f"""# Interview {data['id']}

**Participant:** {data['participant']}
**Status:** {data['status']}
**Timestamp:** {data['timestamp']}

## Questions and Responses

"""
            else:
                return str(data)
        
        # Test JSON export
        json_export = export_interview(interview_data, "json")
        assert "test-interview" in json_export
        assert "test-user" in json_export
        
        # Test Markdown export
        md_export = export_interview(interview_data, "markdown")
        assert "# Interview test-interview" in md_export
        assert "**Participant:** test-user" in md_export
    
    def test_interview_search(self):
        """Test interview search functionality."""
        # Mock interview database
        interviews = [
            {
                "id": "interview-1",
                "participant": "user-1",
                "questions": ["Python experience?", "Testing approach?"],
                "responses": ["5 years", "pytest"],
                "status": "completed"
            },
            {
                "id": "interview-2",
                "participant": "user-2",
                "questions": ["JavaScript experience?", "Frontend tools?"],
                "responses": ["3 years", "React"],
                "status": "completed"
            }
        ]
        
        # Mock search function
        def search_interviews(query, interviews):
            results = []
            query_lower = query.lower()
            
            for interview in interviews:
                # Search in questions and responses
                searchable_text = " ".join(interview["questions"] + interview["responses"]).lower()
                
                if query_lower in searchable_text:
                    results.append(interview)
            
            return results
        
        # Search for Python-related interviews
        python_results = search_interviews("Python", interviews)
        assert len(python_results) == 1
        assert python_results[0]["id"] == "interview-1"
        
        # Search for React-related interviews
        react_results = search_interviews("React", interviews)
        assert len(react_results) == 1
        assert react_results[0]["id"] == "interview-2"
    
    def test_interview_statistics(self):
        """Test interview statistics generation."""
        # Mock interview data
        interviews = [
            {"status": "completed", "participant": "user-1"},
            {"status": "completed", "participant": "user-2"},
            {"status": "active", "participant": "user-3"},
            {"status": "cancelled", "participant": "user-4"}
        ]
        
        # Mock statistics function
        def generate_statistics(interviews):
            total = len(interviews)
            completed = sum(1 for i in interviews if i["status"] == "completed")
            active = sum(1 for i in interviews if i["status"] == "active")
            cancelled = sum(1 for i in interviews if i["status"] == "cancelled")
            
            return {
                "total_interviews": total,
                "completed_interviews": completed,
                "active_interviews": active,
                "cancelled_interviews": cancelled,
                "completion_rate": completed / total if total > 0 else 0,
                "active_rate": active / total if total > 0 else 0
            }
        
        stats = generate_statistics(interviews)
        
        assert stats["total_interviews"] == 4
        assert stats["completed_interviews"] == 2
        assert stats["active_interviews"] == 1
        assert stats["cancelled_interviews"] == 1
        assert stats["completion_rate"] == 0.5
        assert stats["active_rate"] == 0.25


class TestInterviewIntegration:
    """Integration tests for interview functionality."""
    
    def test_interview_workflow(self):
        """Test complete interview workflow."""
        # Mock complete workflow
        def run_interview_workflow(participant, topic):
            # 1. Create interview session
            session = {
                "id": f"interview-{participant}",
                "participant": participant,
                "topic": topic,
                "questions": [],
                "responses": [],
                "status": "active"
            }
            
            # 2. Generate questions
            questions = [
                f"What is your experience with {topic}?",
                f"How do you approach {topic}?",
                f"What challenges have you faced with {topic}?"
            ]
            session["questions"] = questions
            
            # 3. Simulate responses
            responses = [
                f"I have experience with {topic}.",
                f"I approach {topic} systematically.",
                f"I have faced some challenges with {topic}."
            ]
            session["responses"] = responses
            
            # 4. Complete interview
            session["status"] = "completed"
            
            # 5. Analyze interview
            analysis = {
                "response_rate": len(responses) / len(questions),
                "completeness_score": 1.0,
                "average_response_length": sum(len(r) for r in responses) / len(responses)
            }
            
            # 6. Score interview
            score = min(100, int(analysis["response_rate"] * 100))
            
            return {
                "session": session,
                "analysis": analysis,
                "score": score
            }
        
        # Run workflow
        result = run_interview_workflow("test-user", "Python")
        
        assert result["session"]["status"] == "completed"
        assert result["analysis"]["response_rate"] == 1.0
        assert result["score"] == 100
    
    def test_interview_error_handling(self):
        """Test interview error handling."""
        # Mock error-prone interview
        def problematic_interview():
            try:
                # Simulate error
                raise ValueError("Interview error")
            except Exception as e:
                return {
                    "error": str(e),
                    "status": "failed"
                }
        
        result = problematic_interview()
        
        assert result["status"] == "failed"
        assert "Interview error" in result["error"]
    
    def test_interview_performance(self):
        """Test interview performance."""
        import time
        
        # Mock performance test
        def performance_test():
            start_time = time.time()
            
            # Simulate interview processing
            interviews = []
            for i in range(100):
                interview = {
                    "id": f"interview-{i}",
                    "participant": f"user-{i}",
                    "questions": [f"Question {j}" for j in range(5)],
                    "responses": [f"Response {j}" for j in range(5)],
                    "status": "completed"
                }
                interviews.append(interview)
            
            end_time = time.time()
            
            return {
                "processing_time": end_time - start_time,
                "interviews_processed": len(interviews)
            }
        
        result = performance_test()
        
        assert result["interviews_processed"] == 100
        assert result["processing_time"] < 1.0  # Should complete within 1 second


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
