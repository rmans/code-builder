#!/usr/bin/env python3
"""
Quality Commands Module

This module contains commands for running quality gates and validation.
"""

import click
import json
from pathlib import Path
from .base import cli, get_project_root, format_command_output, common_output_format_option

# Import quality gates
try:
    from ...quality.gates import QualityGates
    QUALITY_AVAILABLE = True
except ImportError:
    QUALITY_AVAILABLE = False


@cli.command("quality:gates")
@common_output_format_option()
@click.option("--output-file", help="Output file for detailed report")
@click.option("--verbose", is_flag=True, help="Show detailed gate information")
def quality_gates(output_format, output_file, verbose):
    """Run quality gates for release criteria validation."""
    if not QUALITY_AVAILABLE:
        click.echo("❌ Error: Quality gates module not available")
        return 1
    
    try:
        project_root = get_project_root()
        gates = QualityGates(project_root)
        
        click.echo("🔍 Running quality gates...")
        report = gates.run_all_gates()
        
        # Generate report file if requested
        if output_file:
            report_path = gates.generate_report(report, Path(output_file))
            click.echo(f"📄 Detailed report saved to: {report_path}")
        
        # Display results
        if output_format == 'json':
            report_data = {
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
            click.echo(json.dumps(report_data, indent=2))
        else:
            # Table format
            status_icon = "✅" if report.overall_passed else "❌"
            click.echo(f"\n{status_icon} Quality Gates Summary")
            click.echo("=" * 50)
            click.echo(f"Overall Status: {'PASSED' if report.overall_passed else 'FAILED'}")
            click.echo(f"Gates Passed: {report.summary['passed_gates']}/{report.summary['total_gates']}")
            click.echo(f"Success Rate: {report.summary['success_rate']:.1%}")
            click.echo(f"Execution Time: {report.summary['execution_time_ms']:.1f}ms")
            
            if verbose:
                click.echo("\n📋 Gate Details:")
                for gate in report.gates:
                    gate_icon = "✅" if gate.passed else "❌"
                    click.echo(f"  {gate_icon} {gate.name}: {gate.message} ({gate.execution_time_ms:.1f}ms)")
                    
                    if not gate.passed and gate.details:
                        click.echo(f"    Details: {gate.details}")
        
        return 0 if report.overall_passed else 1
        
    except Exception as e:
        click.echo(f"❌ Error running quality gates: {e}")
        return 1


@cli.command("quality:check")
@click.option("--gate", help="Run specific gate only")
@click.option("--verbose", is_flag=True, help="Show detailed information")
def quality_check(gate, verbose):
    """Check specific quality gate or all gates."""
    if not QUALITY_AVAILABLE:
        click.echo("❌ Error: Quality gates module not available")
        return 1
    
    try:
        project_root = get_project_root()
        gates = QualityGates(project_root)
        
        if gate:
            # Run specific gate
            click.echo(f"🔍 Running {gate} gate...")
            
            if gate == "idempotency":
                result = gates._check_idempotency()
            elif gate == "parity":
                result = gates._check_parity_index_rules()
            elif gate == "determinism":
                result = gates._check_determinism()
            elif gate == "cursor_ux":
                result = gates._check_cursor_ux()
            elif gate == "end_to_end":
                result = gates._check_end_to_end_flow()
            else:
                click.echo(f"❌ Unknown gate: {gate}")
                click.echo("Available gates: idempotency, parity, determinism, cursor_ux, end_to_end")
                return 1
            
            status_icon = "✅" if result.passed else "❌"
            click.echo(f"{status_icon} {result.name}: {result.message}")
            click.echo(f"Execution time: {result.execution_time_ms:.1f}ms")
            
            if verbose and result.details:
                click.echo(f"Details: {json.dumps(result.details, indent=2)}")
            
            return 0 if result.passed else 1
        else:
            # Run all gates
            return quality_gates.callback('table', None, verbose)
            
    except Exception as e:
        click.echo(f"❌ Error running quality check: {e}")
        return 1


@cli.command("quality:report")
@click.option("--output-file", help="Output file for report")
@click.option("--format", "output_format", type=click.Choice(['json', 'yaml', 'html']), default='json')
def quality_report(output_file, output_format):
    """Generate detailed quality gates report."""
    if not QUALITY_AVAILABLE:
        click.echo("❌ Error: Quality gates module not available")
        return 1
    
    try:
        project_root = get_project_root()
        gates = QualityGates(project_root)
        
        click.echo("🔍 Running quality gates for report...")
        report = gates.run_all_gates()
        
        # Determine output file
        if output_file:
            report_path = Path(output_file)
        else:
            report_path = gates.cache_dir / f"quality_gates_report.{output_format}"
        
        # Generate report based on format
        if output_format == 'json':
            gates.generate_report(report, report_path)
        elif output_format == 'yaml':
            import yaml
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
            with open(report_path, 'w') as f:
                yaml.dump(report_data, f, default_flow_style=False)
        elif output_format == 'html':
            # Generate HTML report
            html_content = _generate_html_report(report)
            with open(report_path, 'w') as f:
                f.write(html_content)
        
        click.echo(f"📄 Quality gates report saved to: {report_path}")
        return 0
        
    except Exception as e:
        click.echo(f"❌ Error generating quality report: {e}")
        return 1


def _generate_html_report(report) -> str:
    """Generate HTML report."""
    status_icon = "✅" if report.overall_passed else "❌"
    status_color = "green" if report.overall_passed else "red"
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Quality Gates Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .gate {{ margin: 10px 0; padding: 10px; border-left: 4px solid #ccc; }}
        .gate.passed {{ border-left-color: green; }}
        .gate.failed {{ border-left-color: red; }}
        .summary {{ background-color: #f9f9f9; padding: 15px; border-radius: 5px; }}
        .details {{ margin-top: 10px; font-size: 0.9em; color: #666; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{status_icon} Quality Gates Report</h1>
        <p>Generated: {report.timestamp}</p>
        <p>Overall Status: <span style="color: {status_color}; font-weight: bold;">{'PASSED' if report.overall_passed else 'FAILED'}</span></p>
    </div>
    
    <div class="summary">
        <h2>Summary</h2>
        <p>Gates Passed: {report.summary['passed_gates']}/{report.summary['total_gates']}</p>
        <p>Success Rate: {report.summary['success_rate']:.1%}</p>
        <p>Execution Time: {report.summary['execution_time_ms']:.1f}ms</p>
    </div>
    
    <h2>Gate Results</h2>
"""
    
    for gate in report.gates:
        gate_icon = "✅" if gate.passed else "❌"
        gate_class = "passed" if gate.passed else "failed"
        
        html += f"""
    <div class="gate {gate_class}">
        <h3>{gate_icon} {gate.name}</h3>
        <p>{gate.message}</p>
        <p>Execution time: {gate.execution_time_ms:.1f}ms</p>
        <div class="details">
            <pre>{json.dumps(gate.details, indent=2)}</pre>
        </div>
    </div>
"""
    
    html += """
</body>
</html>
"""
    
    return html
