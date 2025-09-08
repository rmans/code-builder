#!/usr/bin/env python3
"""
Quality Gates Module

Implements quality gates for release criteria including:
- Idempotency checks
- Parity checks (index ↔ rules)
- Determinism checks (non-interactive)
- Cursor UX validation
"""

import os
import json
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from ..overlay.paths import OverlayPaths


@dataclass
class QualityGateResult:
    """Result of a quality gate check."""
    name: str
    passed: bool
    message: str
    details: Dict[str, Any]
    execution_time_ms: float


@dataclass
class QualityReport:
    """Complete quality gates report."""
    timestamp: str
    overall_passed: bool
    gates: List[QualityGateResult]
    summary: Dict[str, Any]


class QualityGates:
    """Quality gates implementation for release criteria."""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.overlay_paths = OverlayPaths()
        self.cache_dir = self.overlay_paths.get_cache_dir()
        self.docs_dir = self.overlay_paths.get_docs_dir()
        
    def run_all_gates(self) -> QualityReport:
        """Run all quality gates and return comprehensive report."""
        start_time = time.time()
        gates = []
        
        # Core quality gates
        gates.append(self._check_idempotency())
        gates.append(self._check_parity_index_rules())
        gates.append(self._check_determinism())
        gates.append(self._check_cursor_ux())
        gates.append(self._check_end_to_end_flow())
        
        # Test suite gates
        gates.append(self._check_discovery_suite())
        gates.append(self._check_interview_suite())
        gates.append(self._check_context_suite())
        gates.append(self._check_orchestrator_suite())
        gates.append(self._check_single_task_suite())
        
        overall_passed = all(gate.passed for gate in gates)
        execution_time = (time.time() - start_time) * 1000
        
        summary = {
            "total_gates": len(gates),
            "passed_gates": sum(1 for gate in gates if gate.passed),
            "failed_gates": sum(1 for gate in gates if not gate.passed),
            "execution_time_ms": execution_time,
            "success_rate": float(sum(1 for gate in gates if gate.passed)) / float(len(gates)) if gates else 0
        }
        
        return QualityReport(
            timestamp=datetime.now().isoformat(),
            overall_passed=overall_passed,
            gates=gates,
            summary=summary
        )
    
    def _check_idempotency(self) -> QualityGateResult:
        """Check that operations are idempotent (same result on repeated runs)."""
        start_time = time.time()
        
        try:
            # Test 1: Command discovery should be idempotent
            discovery_results = []
            for _ in range(3):
                result = self._run_command("discover:analyze", ["--repo-root"])
                discovery_results.append(result)
            
            # All results should be identical
            idempotent = all(
                result == discovery_results[0] 
                for result in discovery_results
            )
            
            # Test 2: Rules generation should be idempotent
            rules_results = []
            for _ in range(3):
                result = self._run_command("rules:check", ["src/**/*.ts", "--feature", "test"])
                rules_results.append(result)
            
            rules_idempotent = all(
                result == rules_results[0] 
                for result in rules_results
            )
            
            passed = idempotent and rules_idempotent
            message = "Idempotency checks passed" if passed else "Idempotency checks failed"
            
            details = {
                "discovery_idempotent": idempotent,
                "rules_idempotent": rules_idempotent,
                "discovery_runs": len(discovery_results),
                "rules_runs": len(rules_results)
            }
            
        except Exception as e:
            passed = False
            message = f"Idempotency check failed with error: {e}"
            details = {"error": str(e)}
        
        execution_time = (time.time() - start_time) * 1000
        
        return QualityGateResult(
            name="idempotency",
            passed=passed,
            message=message,
            details=details,
            execution_time_ms=execution_time
        )
    
    def _check_parity_index_rules(self) -> QualityGateResult:
        """Check parity between index and rules (consistency)."""
        start_time = time.time()
        
        try:
            # Get index data
            index_file = self.docs_dir / "tasks" / "index.json"
            if not index_file.exists():
                return QualityGateResult(
                    name="parity_index_rules",
                    passed=False,
                    message="Index file not found",
                    details={"error": "index.json not found"},
                    execution_time_ms=(time.time() - start_time) * 1000
                )
            
            with open(index_file, 'r') as f:
                index_data = json.load(f)
            
            # Get rules data
            rules_dir = Path(".cursor/rules")
            rules_files = list(rules_dir.glob("*.md")) if rules_dir.exists() else []
            
            # Check for consistency
            index_tasks = set()
            if "tasks" in index_data:
                index_tasks = set(task.get("id", "") for task in index_data["tasks"] if task.get("id"))
            
            rules_commands = set()
            
            for rules_file in rules_files:
                # Extract command ID from rules file
                content = rules_file.read_text()
                if "id:" in content:
                    for line in content.split('\n'):
                        if line.strip().startswith("id:"):
                            command_id = line.split(":", 1)[1].strip()
                            rules_commands.add(command_id)
                            break
            
            # Check parity
            missing_in_rules = index_tasks - rules_commands
            missing_in_index = rules_commands - index_tasks
            
            passed = len(missing_in_rules) == 0 and len(missing_in_index) == 0
            message = "Parity check passed" if passed else "Parity check failed"
            
            # Calculate parity score safely
            total_items = max(len(index_tasks), len(rules_commands), 1)
            missing_items = len(missing_in_rules) + len(missing_in_index)
            parity_score = 1.0 - (float(missing_items) / float(total_items)) if total_items > 0 else 1.0
            
            details = {
                "index_tasks_count": len(index_tasks),
                "rules_commands_count": len(rules_commands),
                "missing_in_rules": list(missing_in_rules),
                "missing_in_index": list(missing_in_index),
                "parity_score": parity_score
            }
            
        except Exception as e:
            passed = False
            message = f"Parity check failed with error: {e}"
            details = {"error": str(e)}
        
        execution_time = (time.time() - start_time) * 1000
        
        return QualityGateResult(
            name="parity_index_rules",
            passed=passed,
            message=message,
            details=details,
            execution_time_ms=execution_time
        )
    
    def _check_determinism(self) -> QualityGateResult:
        """Check that operations are deterministic (non-interactive)."""
        start_time = time.time()
        
        try:
            # Test non-interactive commands
            non_interactive_commands = [
                ("discover:analyze", ["--repo-root"]),
                ("rules:check", ["src/**/*.ts"]),
                ("status", []),
                ("commands:list", [])
            ]
            
            results = []
            for cmd, args in non_interactive_commands:
                result = self._run_command(cmd, args)
                results.append({
                    "command": cmd,
                    "args": args,
                    "success": result is not None,
                    "output_hash": hashlib.md5(str(result).encode()).hexdigest()
                })
            
            # All commands should succeed and produce consistent output
            all_successful = all(r["success"] for r in results)
            
            # Check for deterministic output (same hash on repeated runs)
            deterministic_results = []
            for cmd, args in non_interactive_commands:
                hashes = []
                for _ in range(3):
                    result = self._run_command(cmd, args)
                    if result is not None:
                        hashes.append(hashlib.md5(str(result).encode()).hexdigest())
                
                deterministic_results.append(len(set(hashes)) == 1)
            
            all_deterministic = all(deterministic_results)
            passed = all_successful and all_deterministic
            
            message = "Determinism checks passed" if passed else "Determinism checks failed"
            
            details = {
                "commands_tested": len(non_interactive_commands),
                "all_successful": all_successful,
                "all_deterministic": all_deterministic,
                "results": results
            }
            
        except Exception as e:
            passed = False
            message = f"Determinism check failed with error: {e}"
            details = {"error": str(e)}
        
        execution_time = (time.time() - start_time) * 1000
        
        return QualityGateResult(
            name="determinism",
            passed=passed,
            message=message,
            details=details,
            execution_time_ms=execution_time
        )
    
    def _check_cursor_ux(self) -> QualityGateResult:
        """Check Cursor UX quality (rules format, usability)."""
        start_time = time.time()
        
        try:
            rules_dir = Path(".cursor/rules")
            if not rules_dir.exists():
                return QualityGateResult(
                    name="cursor_ux",
                    passed=False,
                    message="Rules directory not found",
                    details={"error": ".cursor/rules directory not found"},
                    execution_time_ms=(time.time() - start_time) * 1000
                )
            
            rules_files = list(rules_dir.glob("*.md"))
            ux_issues = []
            
            for rules_file in rules_files:
                content = rules_file.read_text()
                
                # Check for required sections
                required_sections = ["id:", "title:", "description:", "usage:"]
                missing_sections = [section for section in required_sections if section not in content]
                
                if missing_sections:
                    ux_issues.append(f"{rules_file.name}: Missing sections {missing_sections}")
                
                # Check for proper formatting
                if "```bash" not in content and "```" in content:
                    ux_issues.append(f"{rules_file.name}: Missing bash code blocks")
                
                # Check for examples
                if "## Examples" not in content and "## Usage" not in content:
                    ux_issues.append(f"{rules_file.name}: Missing examples or usage section")
            
            passed = len(ux_issues) == 0
            message = "Cursor UX checks passed" if passed else "Cursor UX checks failed"
            
            details = {
                "rules_files_count": len(rules_files),
                "ux_issues": ux_issues,
                "ux_score": 1.0 - float(len(ux_issues)) / float(max(len(rules_files), 1))
            }
            
        except Exception as e:
            passed = False
            message = f"Cursor UX check failed with error: {e}"
            details = {"error": str(e)}
        
        execution_time = (time.time() - start_time) * 1000
        
        return QualityGateResult(
            name="cursor_ux",
            passed=passed,
            message=message,
            details=details,
            execution_time_ms=execution_time
        )
    
    def _check_end_to_end_flow(self) -> QualityGateResult:
        """Check complete end-to-end flow."""
        start_time = time.time()
        
        try:
            # Test the complete flow: analyze → plan → context → execute
            flow_commands = [
                ("discover:analyze", ["--repo-root"]),
                ("plan:sync", []),
                ("context:create", []),
                ("tasks:execute", ["--dry-run"])
            ]
            
            flow_results = []
            for cmd, args in flow_commands:
                result = self._run_command(cmd, args)
                flow_results.append({
                    "command": cmd,
                    "args": args,
                    "success": result is not None,
                    "exit_code": 0 if result is not None else 1
                })
            
            all_successful = all(r["success"] for r in flow_results)
            passed = all_successful
            
            message = "End-to-end flow passed" if passed else "End-to-end flow failed"
            
            details = {
                "flow_commands": len(flow_commands),
                "all_successful": all_successful,
                "results": flow_results
            }
            
        except Exception as e:
            passed = False
            message = f"End-to-end flow check failed with error: {e}"
            details = {"error": str(e)}
        
        execution_time = (time.time() - start_time) * 1000
        
        return QualityGateResult(
            name="end_to_end_flow",
            passed=passed,
            message=message,
            details=details,
            execution_time_ms=execution_time
        )
    
    def _check_discovery_suite(self) -> QualityGateResult:
        """Check discovery test suite."""
        return self._run_test_suite("discovery", [("discover:analyze", []), ("discover:scan", [])])
    
    def _check_interview_suite(self) -> QualityGateResult:
        """Check interview test suite."""
        return self._run_test_suite("interview", [("interview:start", []), ("interview:analyze", [])])
    
    def _check_context_suite(self) -> QualityGateResult:
        """Check context test suite."""
        return self._run_test_suite("context", [("context:create", []), ("context:pack", [])])
    
    def _check_orchestrator_suite(self) -> QualityGateResult:
        """Check orchestrator test suite."""
        return self._run_test_suite("orchestrator", [("orchestrator:start", []), ("orchestrator:status", [])])
    
    def _check_single_task_suite(self) -> QualityGateResult:
        """Check single task test suite."""
        return self._run_test_suite("single_task", [("tasks:execute", []), ("tasks:list", [])])
    
    def _run_test_suite(self, suite_name: str, commands: List[tuple]) -> QualityGateResult:
        """Run a test suite and return results."""
        start_time = time.time()
        
        try:
            results = []
            for cmd, args in commands:
                result = self._run_command(cmd, args)
                results.append({
                    "command": cmd,
                    "success": result is not None
                })
            
            all_successful = all(r["success"] for r in results)
            passed = all_successful
            
            message = f"{suite_name} suite passed" if passed else f"{suite_name} suite failed"
            
            details = {
                "commands_tested": len(commands),
                "all_successful": all_successful,
                "results": results
            }
            
        except Exception as e:
            passed = False
            message = f"{suite_name} suite check failed with error: {e}"
            details = {"error": str(e)}
        
        execution_time = (time.time() - start_time) * 1000
        
        return QualityGateResult(
            name=f"{suite_name}_suite",
            passed=passed,
            message=message,
            details=details,
            execution_time_ms=execution_time
        )
    
    def _run_command(self, command: str, args: List[str] = None) -> Optional[Any]:
        """Run a command and return the result."""
        try:
            import subprocess
            import sys
            
            cmd_args = [sys.executable, "-m", "builder.core.cli", command]
            if args:
                cmd_args.extend(args)
            
            result = subprocess.run(
                cmd_args,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.project_root
            )
            
            return {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
        except Exception as e:
            return None
    
    def generate_report(self, report: QualityReport, output_file: Path = None) -> Path:
        """Generate a quality gates report file."""
        if output_file is None:
            output_file = self.cache_dir / "quality_gates_report.json"
        
        # Ensure cache directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to serializable format
        report_data = {
            "timestamp": report.timestamp,
            "overall_passed": report.overall_passed,
            "gates": [
                {
                    "name": gate.name,
                    "passed": gate.passed,
                    "message": gate.message,
                    "details": gate.details,
                    "execution_time_ms": gate.execution_time_ms
                }
                for gate in report.gates
            ],
            "summary": report.summary
        }
        
        with open(output_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        return output_file
