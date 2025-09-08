#!/usr/bin/env python3
"""
Quality Test Suites Runner

Runs all quality test suites and generates comprehensive reports.
"""

import sys
import pytest
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from builder.quality.gates import QualityGates


class QualityTestRunner:
    """Runs quality test suites and generates reports."""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.results = {}
        self.start_time = None
        self.end_time = None
    
    def run_all_suites(self) -> Dict[str, Any]:
        """Run all quality test suites."""
        self.start_time = time.time()
        
        # Define test suites
        suites = {
            "discovery": "tests/suites/test_discovery_suite.py",
            "context": "tests/suites/test_context_suite.py", 
            "orchestrator": "tests/suites/test_orchestrator_suite.py",
            "single_task": "tests/suites/test_single_task_suite.py",
            "interview": "tests/suites/test_interview_suite.py"
        }
        
        # Run each suite
        for suite_name, suite_path in suites.items():
            print(f"🧪 Running {suite_name} test suite...")
            
            try:
                result = self._run_suite(suite_path)
                self.results[suite_name] = result
                print(f"✅ {suite_name} suite completed: {result['passed']}/{result['total']} tests passed")
            except Exception as e:
                print(f"❌ {suite_name} suite failed: {e}")
                self.results[suite_name] = {
                    "passed": 0,
                    "total": 0,
                    "failed": 0,
                    "error": str(e),
                    "execution_time": 0
                }
        
        self.end_time = time.time()
        
        return self._generate_summary()
    
    def _run_suite(self, suite_path: str) -> Dict[str, Any]:
        """Run a single test suite."""
        start_time = time.time()
        
        # Run pytest
        result = pytest.main([
            suite_path,
            "-v",
            "--tb=short",
            "--json-report",
            "--json-report-file=temp_report.json"
        ])
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Try to read JSON report
        try:
            with open("temp_report.json", "r") as f:
                report_data = json.load(f)
            
            # Clean up temp file
            Path("temp_report.json").unlink(missing_ok=True)
            
            return {
                "passed": report_data.get("summary", {}).get("passed", 0),
                "total": report_data.get("summary", {}).get("total", 0),
                "failed": report_data.get("summary", {}).get("failed", 0),
                "execution_time": execution_time,
                "exit_code": result
            }
        except (FileNotFoundError, json.JSONDecodeError):
            # Fallback if JSON report not available
            return {
                "passed": 0 if result != 0 else 1,
                "total": 1,
                "failed": 1 if result != 0 else 0,
                "execution_time": execution_time,
                "exit_code": result
            }
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate summary of all test results."""
        total_passed = sum(result.get("passed", 0) for result in self.results.values())
        total_tests = sum(result.get("total", 0) for result in self.results.values())
        total_failed = sum(result.get("failed", 0) for result in self.results.values())
        total_time = self.end_time - self.start_time if self.end_time and self.start_time else 0
        
        # Calculate success rate
        success_rate = total_passed / total_tests if total_tests > 0 else 0
        
        # Check if all suites passed
        all_passed = all(
            result.get("failed", 0) == 0 and "error" not in result 
            for result in self.results.values()
        )
        
        return {
            "timestamp": datetime.now().isoformat(),
            "overall_passed": all_passed,
            "total_tests": total_tests,
            "total_passed": total_passed,
            "total_failed": total_failed,
            "success_rate": success_rate,
            "total_execution_time": total_time,
            "suites": self.results
        }
    
    def generate_report(self, output_file: Path = None) -> Path:
        """Generate detailed test report."""
        if output_file is None:
            output_file = self.project_root / "builder" / "cache" / "quality_test_report.json"
        
        # Ensure cache directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate summary if not already done
        if not self.results:
            self.run_all_suites()
        
        summary = self._generate_summary()
        
        # Write report
        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        return output_file
    
    def run_quality_gates(self) -> Dict[str, Any]:
        """Run quality gates in addition to test suites."""
        print("🔍 Running quality gates...")
        
        try:
            gates = QualityGates(self.project_root)
            report = gates.run_all_gates()
            
            return {
                "timestamp": report.timestamp,
                "overall_passed": report.overall_passed,
                "gates": [
                    {
                        "name": gate.name,
                        "passed": gate.passed,
                        "message": gate.message,
                        "execution_time_ms": gate.execution_time_ms
                    }
                    for gate in report.gates
                ],
                "summary": report.summary
            }
        except Exception as e:
            print(f"❌ Quality gates failed: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "overall_passed": False,
                "error": str(e),
                "gates": [],
                "summary": {}
            }


def main():
    """Main entry point for quality test runner."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run quality test suites")
    parser.add_argument("--suites", nargs="+", 
                       choices=["discovery", "context", "orchestrator", "single_task", "interview"],
                       help="Specific suites to run")
    parser.add_argument("--gates", action="store_true", help="Run quality gates")
    parser.add_argument("--output", help="Output file for report")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    runner = QualityTestRunner()
    
    if args.suites:
        # Run specific suites
        print(f"🧪 Running specific suites: {', '.join(args.suites)}")
        # Implementation for specific suites would go here
    else:
        # Run all suites
        print("🧪 Running all quality test suites...")
        summary = runner.run_all_suites()
        
        print(f"\n📊 Quality Test Summary")
        print("=" * 50)
        print(f"Overall Status: {'PASSED' if summary['overall_passed'] else 'FAILED'}")
        print(f"Tests Passed: {summary['total_passed']}/{summary['total_tests']}")
        print(f"Success Rate: {summary['success_rate']:.1%}")
        print(f"Execution Time: {summary['total_execution_time']:.1f}s")
        
        if args.verbose:
            print("\n📋 Suite Details:")
            for suite_name, result in summary['suites'].items():
                status = "✅" if result.get("failed", 0) == 0 and "error" not in result else "❌"
                print(f"  {status} {suite_name}: {result.get('passed', 0)}/{result.get('total', 0)} tests passed")
    
    if args.gates:
        print("\n🔍 Running quality gates...")
        gates_result = runner.run_quality_gates()
        
        print(f"Quality Gates Status: {'PASSED' if gates_result['overall_passed'] else 'FAILED'}")
        
        if args.verbose:
            for gate in gates_result.get('gates', []):
                status = "✅" if gate['passed'] else "❌"
                print(f"  {status} {gate['name']}: {gate['message']}")
    
    # Generate report
    if args.output:
        report_file = runner.generate_report(Path(args.output))
        print(f"\n📄 Report saved to: {report_file}")
    
    return 0 if summary.get('overall_passed', False) else 1


if __name__ == "__main__":
    sys.exit(main())
