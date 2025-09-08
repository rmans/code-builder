#!/usr/bin/env python3
"""
Orchestrator Test Suite

Comprehensive tests for orchestrator functionality including:
- Task orchestration
- Agent coordination
- Workflow management
- Status tracking
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

from builder.utils.task_orchestrator import TaskOrchestrator, Agent, Task


class TestOrchestratorSuite:
    """Test suite for orchestrator functionality."""
    
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
---
# Test Task 1
Description of test task 1.
""")
        
        (tasks_dir / "TASK-002.md").write_text("""---
id: TASK-002
title: Test Task 2
status: pending
priority: 3
---
# Test Task 2
Description of test task 2.
""")
    
    def test_orchestrator_creation(self):
        """Test orchestrator creation."""
        orchestrator = TaskOrchestrator()
        assert orchestrator is not None
        assert hasattr(orchestrator, 'agents')
        assert hasattr(orchestrator, 'tasks')
    
    def test_agent_creation(self):
        """Test agent creation."""
        agent = Agent("test-agent", "backend")
        assert agent.name == "test-agent"
        assert agent.agent_type == "backend"
        assert agent.status == "idle"
        assert agent.last_heartbeat is not None
    
    def test_task_creation(self):
        """Test task creation."""
        task = Task("test-task", "Test task description", priority=5)
        assert task.id == "test-task"
        assert task.description == "Test task description"
        assert task.priority == 5
        assert task.status == "pending"
    
    def test_agent_registration(self):
        """Test agent registration."""
        orchestrator = TaskOrchestrator()
        agent = Agent("test-agent", "backend")
        
        orchestrator.register_agent(agent)
        
        assert len(orchestrator.agents) == 1
        assert orchestrator.agents[0].name == "test-agent"
    
    def test_task_assignment(self):
        """Test task assignment to agents."""
        orchestrator = TaskOrchestrator()
        agent = Agent("test-agent", "backend")
        task = Task("test-task", "Test task description")
        
        orchestrator.register_agent(agent)
        orchestrator.add_task(task)
        
        # Assign task to agent
        success = orchestrator.assign_task(task.id, agent.name)
        
        assert success
        assert task.assigned_agent == agent.name
        assert task.status == "assigned"
    
    def test_task_execution(self):
        """Test task execution."""
        orchestrator = TaskOrchestrator()
        agent = Agent("test-agent", "backend")
        task = Task("test-task", "Test task description")
        
        orchestrator.register_agent(agent)
        orchestrator.add_task(task)
        orchestrator.assign_task(task.id, agent.name)
        
        # Execute task
        success = orchestrator.execute_task(task.id)
        
        assert success
        assert task.status == "completed"
    
    def test_task_prioritization(self):
        """Test task prioritization."""
        orchestrator = TaskOrchestrator()
        
        # Add tasks with different priorities
        task1 = Task("task-1", "High priority task", priority=1)
        task2 = Task("task-2", "Low priority task", priority=5)
        task3 = Task("task-3", "Medium priority task", priority=3)
        
        orchestrator.add_task(task1)
        orchestrator.add_task(task2)
        orchestrator.add_task(task3)
        
        # Get prioritized tasks
        prioritized = orchestrator.get_prioritized_tasks()
        
        assert len(prioritized) == 3
        assert prioritized[0].priority <= prioritized[1].priority
        assert prioritized[1].priority <= prioritized[2].priority
    
    def test_agent_status_tracking(self):
        """Test agent status tracking."""
        orchestrator = TaskOrchestrator()
        agent = Agent("test-agent", "backend")
        
        orchestrator.register_agent(agent)
        
        # Update agent status
        orchestrator.update_agent_status(agent.name, "busy")
        
        assert agent.status == "busy"
        assert agent.last_heartbeat is not None
    
    def test_task_status_tracking(self):
        """Test task status tracking."""
        orchestrator = TaskOrchestrator()
        task = Task("test-task", "Test task description")
        
        orchestrator.add_task(task)
        
        # Update task status
        orchestrator.update_task_status(task.id, "in_progress")
        
        assert task.status == "in_progress"
    
    def test_orchestrator_cleanup(self):
        """Test orchestrator cleanup."""
        orchestrator = TaskOrchestrator()
        agent = Agent("test-agent", "backend")
        task = Task("test-task", "Test task description")
        
        orchestrator.register_agent(agent)
        orchestrator.add_task(task)
        
        # Cleanup
        orchestrator.cleanup()
        
        # Should handle cleanup gracefully
        assert True  # If we get here, cleanup didn't crash
    
    def test_error_handling(self):
        """Test error handling."""
        orchestrator = TaskOrchestrator()
        
        # Test assigning task to non-existent agent
        task = Task("test-task", "Test task description")
        orchestrator.add_task(task)
        
        success = orchestrator.assign_task(task.id, "non-existent-agent")
        assert not success
        
        # Test executing non-existent task
        success = orchestrator.execute_task("non-existent-task")
        assert not success
    
    def test_orchestrator_performance(self):
        """Test orchestrator performance."""
        import time
        
        orchestrator = TaskOrchestrator()
        
        # Add multiple agents and tasks
        for i in range(10):
            agent = Agent(f"agent-{i}", "backend")
            orchestrator.register_agent(agent)
            
            task = Task(f"task-{i}", f"Task {i} description", priority=i)
            orchestrator.add_task(task)
        
        start_time = time.time()
        
        # Perform operations
        for i in range(10):
            orchestrator.assign_task(f"task-{i}", f"agent-{i}")
            orchestrator.execute_task(f"task-{i}")
        
        end_time = time.time()
        
        # Should complete within reasonable time
        assert (end_time - start_time) < 2.0  # 2 seconds max


class TestOrchestratorIntegration:
    """Integration tests for orchestrator functionality."""
    
    def test_orchestrator_with_real_tasks(self):
        """Test orchestrator with real task files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "test_project"
            project_root.mkdir()
            
            # Create tasks directory
            tasks_dir = project_root / "cb_docs" / "tasks"
            tasks_dir.mkdir(parents=True)
            
            # Create test task files
            (tasks_dir / "TASK-001.md").write_text("""---
id: TASK-001
title: Test Task 1
status: pending
priority: 5
---
# Test Task 1
Description of test task 1.
""")
            
            # Test orchestrator with real tasks
            orchestrator = TaskOrchestrator()
            
            # Load tasks from files
            task_files = list(tasks_dir.glob("*.md"))
            for task_file in task_files:
                content = task_file.read_text()
                # Parse task from content (simplified)
                task_id = task_file.stem
                task = Task(task_id, f"Task from {task_file.name}")
                orchestrator.add_task(task)
            
            assert len(orchestrator.tasks) > 0
    
    def test_orchestrator_workflow(self):
        """Test complete orchestrator workflow."""
        orchestrator = TaskOrchestrator()
        
        # Create agents
        agent1 = Agent("agent-1", "backend")
        agent2 = Agent("agent-2", "frontend")
        
        orchestrator.register_agent(agent1)
        orchestrator.register_agent(agent2)
        
        # Create tasks
        task1 = Task("task-1", "Backend task", priority=1)
        task2 = Task("task-2", "Frontend task", priority=2)
        
        orchestrator.add_task(task1)
        orchestrator.add_task(task2)
        
        # Assign and execute tasks
        orchestrator.assign_task("task-1", "agent-1")
        orchestrator.assign_task("task-2", "agent-2")
        
        orchestrator.execute_task("task-1")
        orchestrator.execute_task("task-2")
        
        # Verify completion
        assert task1.status == "completed"
        assert task2.status == "completed"
    
    def test_orchestrator_monitoring(self):
        """Test orchestrator monitoring capabilities."""
        orchestrator = TaskOrchestrator()
        
        # Add agents and tasks
        agent = Agent("test-agent", "backend")
        task = Task("test-task", "Test task description")
        
        orchestrator.register_agent(agent)
        orchestrator.add_task(task)
        
        # Test monitoring
        status = orchestrator.get_status()
        
        assert "agents" in status
        assert "tasks" in status
        assert "active_tasks" in status
        assert "completed_tasks" in status


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
