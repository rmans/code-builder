#!/usr/bin/env python3
"""
Single Task Test Suite

Comprehensive tests for single task execution including:
- Task execution
- Task validation
- Task status tracking
- Task dependencies
- Task rollback
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

from builder.utils.task_orchestrator import Task
from builder.core.cli import cli


class TestSingleTaskSuite:
    """Test suite for single task functionality."""
    
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
        # Create tasks directory
        tasks_dir = self.project_root / "cb_docs" / "tasks"
        tasks_dir.mkdir(parents=True)
        
        # Create test task files
        (tasks_dir / "TASK-001.md").write_text("""---
id: TASK-001
title: Test Task 1
status: pending
priority: 5
dependencies: []
---
# Test Task 1
Description of test task 1.

## Phases
### Phase 1: Implementation
- [ ] Step 1
- [ ] Step 2

### Phase 2: Testing
- [ ] Test step 1
- [ ] Test step 2
""")
        
        (tasks_dir / "TASK-002.md").write_text("""---
id: TASK-002
title: Test Task 2
status: pending
priority: 3
dependencies: [TASK-001]
---
# Test Task 2
Description of test task 2.

## Phases
### Phase 1: Implementation
- [ ] Step 1
- [ ] Step 2
""")
    
    def test_task_creation(self):
        """Test task creation."""
        task = Task("test-task", "Test task description", priority=5)
        
        assert task.id == "test-task"
        assert task.description == "Test task description"
        assert task.priority == 5
        assert task.status == "pending"
        assert task.assigned_agent is None
        assert task.created_at is not None
    
    def test_task_validation(self):
        """Test task validation."""
        # Valid task
        task = Task("valid-task", "Valid task description")
        assert task.validate()
        
        # Invalid task (empty ID)
        task = Task("", "Task description")
        assert not task.validate()
        
        # Invalid task (empty description)
        task = Task("invalid-task", "")
        assert not task.validate()
    
    def test_task_status_transitions(self):
        """Test task status transitions."""
        task = Task("test-task", "Test task description")
        
        # Initial status
        assert task.status == "pending"
        
        # Transition to assigned
        task.status = "assigned"
        assert task.status == "assigned"
        
        # Transition to in_progress
        task.status = "in_progress"
        assert task.status == "in_progress"
        
        # Transition to completed
        task.status = "completed"
        assert task.status == "completed"
        
        # Transition to failed
        task.status = "failed"
        assert task.status == "failed"
    
    def test_task_dependencies(self):
        """Test task dependencies."""
        task1 = Task("task-1", "Task 1 description")
        task2 = Task("task-2", "Task 2 description")
        
        # Add dependency
        task2.add_dependency("task-1")
        
        assert "task-1" in task2.dependencies
        assert task2.has_dependency("task-1")
        assert not task1.has_dependency("task-2")
    
    def test_task_execution(self):
        """Test task execution."""
        task = Task("test-task", "Test task description")
        
        # Mock execution function
        def mock_execute():
            return True
        
        task.execute_function = mock_execute
        
        # Execute task
        result = task.execute()
        
        assert result
        assert task.status == "completed"
        assert task.completed_at is not None
    
    def test_task_execution_failure(self):
        """Test task execution failure."""
        task = Task("test-task", "Test task description")
        
        # Mock execution function that fails
        def mock_execute():
            raise Exception("Execution failed")
        
        task.execute_function = mock_execute
        
        # Execute task
        result = task.execute()
        
        assert not result
        assert task.status == "failed"
        assert task.error_message is not None
    
    def test_task_rollback(self):
        """Test task rollback."""
        task = Task("test-task", "Test task description")
        
        # Mock rollback function
        def mock_rollback():
            return True
        
        task.rollback_function = mock_rollback
        
        # Rollback task
        result = task.rollback()
        
        assert result
        assert task.status == "rolled_back"
    
    def test_task_metadata(self):
        """Test task metadata."""
        task = Task("test-task", "Test task description", priority=5)
        
        # Add metadata
        task.add_metadata("owner", "test-user")
        task.add_metadata("tags", ["test", "example"])
        
        assert task.get_metadata("owner") == "test-user"
        assert task.get_metadata("tags") == ["test", "example"]
        assert task.get_metadata("non-existent") is None
    
    def test_task_phases(self):
        """Test task phases."""
        task = Task("test-task", "Test task description")
        
        # Add phases
        task.add_phase("Phase 1", ["Step 1", "Step 2"])
        task.add_phase("Phase 2", ["Step 3", "Step 4"])
        
        assert len(task.phases) == 2
        assert task.phases[0]["name"] == "Phase 1"
        assert task.phases[0]["steps"] == ["Step 1", "Step 2"]
        
        # Complete phase
        task.complete_phase("Phase 1")
        assert task.phases[0]["completed"]
    
    def test_task_progress(self):
        """Test task progress tracking."""
        task = Task("test-task", "Test task description")
        
        # Add phases
        task.add_phase("Phase 1", ["Step 1", "Step 2"])
        task.add_phase("Phase 2", ["Step 3", "Step 4"])
        
        # Check initial progress
        progress = task.get_progress()
        assert progress["total_phases"] == 2
        assert progress["completed_phases"] == 0
        assert progress["completion_percentage"] == 0.0
        
        # Complete one phase
        task.complete_phase("Phase 1")
        progress = task.get_progress()
        assert progress["completed_phases"] == 1
        assert progress["completion_percentage"] == 50.0
    
    def test_task_serialization(self):
        """Test task serialization."""
        task = Task("test-task", "Test task description", priority=5)
        task.add_metadata("owner", "test-user")
        task.add_phase("Phase 1", ["Step 1", "Step 2"])
        
        # Serialize task
        task_data = task.to_dict()
        
        assert task_data["id"] == "test-task"
        assert task_data["description"] == "Test task description"
        assert task_data["priority"] == 5
        assert task_data["metadata"]["owner"] == "test-user"
        assert len(task_data["phases"]) == 1
        
        # Deserialize task
        new_task = Task.from_dict(task_data)
        
        assert new_task.id == task.id
        assert new_task.description == task.description
        assert new_task.priority == task.priority
        assert new_task.get_metadata("owner") == "test-user"
        assert len(new_task.phases) == 1


class TestSingleTaskIntegration:
    """Integration tests for single task functionality."""
    
    def test_task_with_file_operations(self):
        """Test task with file operations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "test_project"
            project_root.mkdir()
            
            task = Task("file-task", "File operation task")
            
            # Mock file operations
            def mock_execute():
                test_file = project_root / "test.txt"
                test_file.write_text("Test content")
                return True
            
            def mock_rollback():
                test_file = project_root / "test.txt"
                if test_file.exists():
                    test_file.unlink()
                return True
            
            task.execute_function = mock_execute
            task.rollback_function = mock_rollback
            
            # Execute task
            result = task.execute()
            assert result
            assert (project_root / "test.txt").exists()
            
            # Rollback task
            rollback_result = task.rollback()
            assert rollback_result
            assert not (project_root / "test.txt").exists()
    
    def test_task_with_dependencies(self):
        """Test task with dependencies."""
        task1 = Task("task-1", "Task 1 description")
        task2 = Task("task-2", "Task 2 description")
        
        # Add dependency
        task2.add_dependency("task-1")
        
        # Mock execution functions
        def mock_execute_task1():
            task1.status = "completed"
            return True
        
        def mock_execute_task2():
            if task1.status == "completed":
                task2.status = "completed"
                return True
            return False
        
        task1.execute_function = mock_execute_task1
        task2.execute_function = mock_execute_task2
        
        # Execute task 1
        result1 = task1.execute()
        assert result1
        assert task1.status == "completed"
        
        # Execute task 2 (should succeed because task 1 is completed)
        result2 = task2.execute()
        assert result2
        assert task2.status == "completed"
    
    def test_task_error_handling(self):
        """Test task error handling."""
        task = Task("error-task", "Task that will fail")
        
        # Mock execution function that raises exception
        def mock_execute():
            raise ValueError("Test error")
        
        task.execute_function = mock_execute
        
        # Execute task
        result = task.execute()
        
        assert not result
        assert task.status == "failed"
        assert "Test error" in str(task.error_message)
    
    def test_task_performance(self):
        """Test task performance."""
        import time
        
        task = Task("performance-task", "Performance test task")
        
        # Mock execution function with timing
        def mock_execute():
            time.sleep(0.1)  # Simulate work
            return True
        
        task.execute_function = mock_execute
        
        start_time = time.time()
        result = task.execute()
        end_time = time.time()
        
        assert result
        assert (end_time - start_time) >= 0.1
        assert (end_time - start_time) < 0.2  # Should not take too long


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
