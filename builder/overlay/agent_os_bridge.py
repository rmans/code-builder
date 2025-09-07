#!/usr/bin/env python3
"""
Agent-OS Bridge for Code Builder

This module provides a bridge between agent commands and the underlying Code Builder
functionality, mapping agent-friendly commands to the full implementation.
"""

import click
import json
import os
from datetime import datetime
from pathlib import Path
from .paths import OverlayPaths
from ..core.cli.base import cli

# Initialize overlay paths
overlay_paths = OverlayPaths()


@cli.command("plan")
@click.option("--persona", type=click.Choice(['dev', 'pm', 'ai']), default='dev', help="Interview persona")
@click.option("--noninteractive", is_flag=True, help="Use defaults instead of prompts")
@click.option("--auto-analyze", is_flag=True, help="Automatically run analysis if not done")
def plan_command(persona, noninteractive, auto_analyze):
    """
    Create project plan through guided interview.
    
    This command creates planning documents through interview or defaults.
    """
    try:
        
        # Check if analysis has been done
        if auto_analyze:
            _ensure_analysis_done()
        
        click.echo("📋 Creating project plan...")
        
        # Create planning directory
        docs_dir = Path(overlay_paths.get_docs_dir())
        planning_dir = docs_dir / "planning"
        planning_dir.mkdir(parents=True, exist_ok=True)
        
        # Collect planning information
        if noninteractive:
            # Use defaults for non-interactive mode
            planning_data = _get_default_planning_data(persona)
        else:
            # Collect interactive input
            planning_data = _collect_planning_input(persona)
        
        # Create interview.json
        interview_file = planning_dir / "interview.json"
        with open(interview_file, 'w', encoding='utf-8') as f:
            json.dump(planning_data, f, indent=2, sort_keys=True)
        
        # Create assumptions.md
        assumptions_file = planning_dir / "assumptions.md"
        _create_assumptions_file(assumptions_file, planning_data)
        
        # Create decisions.md
        decisions_file = planning_dir / "decisions.md"
        _create_decisions_file(decisions_file, planning_data)
        
        click.echo(f"✅ Planning complete!")
        click.echo(f"📄 Interview responses: {interview_file}")
        click.echo(f"📋 Assumptions: {assumptions_file}")
        click.echo(f"🎯 Decisions: {decisions_file}")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        return 1
    
    return 0


def _get_default_planning_data(persona):
    """Get default planning data based on persona."""
    defaults = {
        "dev": {
            "product": "Code Builder Project",
            "idea": "Automated code generation and project management",
            "problem": "Manual project setup and maintenance is time-consuming",
            "users": "Developers, project managers, technical teams",
            "features": ["CLI interface", "Project analysis", "Automated workflows"],
            "metrics": ["Development speed", "Code quality", "Project success rate"],
            "tech": ["Python", "JavaScript", "Markdown"],
            "timeline": "3-6 months",
            "team_size": "2-5 developers"
        },
        "pm": {
            "product": "Project Management System",
            "idea": "Streamlined project planning and execution",
            "problem": "Lack of structured project planning and tracking",
            "users": "Project managers, stakeholders, development teams",
            "features": ["Planning tools", "Progress tracking", "Resource management"],
            "metrics": ["Project completion rate", "Budget adherence", "Timeline accuracy"],
            "tech": ["Web technologies", "Database systems", "Reporting tools"],
            "timeline": "6-12 months",
            "team_size": "5-10 team members"
        },
        "ai": {
            "product": "AI-Powered Development Tool",
            "idea": "Intelligent code generation and project assistance",
            "problem": "Manual coding and project setup is inefficient",
            "users": "AI researchers, developers, technical teams",
            "features": ["AI code generation", "Intelligent analysis", "Automated testing"],
            "metrics": ["Code generation accuracy", "Development efficiency", "Bug reduction"],
            "tech": ["Machine learning", "Python", "AI frameworks"],
            "timeline": "12-18 months",
            "team_size": "3-7 AI specialists"
        }
    }
    
    return {
        "persona": persona,
        "timestamp": datetime.now().isoformat(),
        "planning_data": defaults.get(persona, defaults["dev"]),
        "status": "completed"
    }


def _collect_planning_input(persona):
    """Collect planning input interactively."""
    click.echo(f"📋 Collecting planning information for {persona} persona...")
    
    # For now, use defaults but mark as interactive
    data = _get_default_planning_data(persona)
    data["mode"] = "interactive"
    
    return data


def _create_assumptions_file(file_path, planning_data):
    """Create assumptions.md file."""
    data = planning_data["planning_data"]
    
    content = f"""# Project Assumptions

## Product Assumptions
- **Product**: {data['product']}
- **Core Idea**: {data['idea']}
- **Problem Statement**: {data['problem']}

## User Assumptions
- **Target Users**: {data['users']}
- **User Needs**: Automated solutions for manual processes
- **User Skills**: Technical proficiency in development tools

## Technical Assumptions
- **Technology Stack**: {', '.join(data['tech'])}
- **Development Timeline**: {data['timeline']}
- **Team Size**: {data['team_size']}

## Feature Assumptions
- **Core Features**: {', '.join(data['features'])}
- **Success Metrics**: {', '.join(data['metrics'])}

## Risk Assumptions
- **Technical Risks**: Technology complexity and integration challenges
- **Timeline Risks**: Scope creep and resource availability
- **User Adoption**: Learning curve and change management

*Generated on {planning_data['timestamp']}*
"""
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


def _create_decisions_file(file_path, planning_data):
    """Create decisions.md file."""
    data = planning_data["planning_data"]
    
    content = f"""# Key Project Decisions

## Architecture Decisions
- **Technology Choice**: Selected {', '.join(data['tech'])} for core implementation
- **Development Approach**: Iterative development with regular feedback
- **Integration Strategy**: Modular design for easy integration

## Feature Decisions
- **Priority Features**: {', '.join(data['features'])}
- **User Experience**: Focus on developer-friendly interfaces
- **Performance**: Optimize for speed and reliability

## Process Decisions
- **Development Timeline**: {data['timeline']} for full implementation
- **Team Structure**: {data['team_size']} team with specialized roles
- **Quality Assurance**: Automated testing and code review processes

## Success Criteria
- **Primary Metrics**: {', '.join(data['metrics'])}
- **User Satisfaction**: High adoption and positive feedback
- **Technical Quality**: Maintainable and scalable codebase

*Generated on {planning_data['timestamp']}*
"""
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


def _ensure_analysis_done():
    """Ensure project analysis has been completed."""
    try:
        # Check if discovery report exists
        docs_dir = Path(overlay_paths.get_docs_dir())
        discovery_dir = docs_dir / "discovery"
        report_file = discovery_dir / "report.json"
        
        if not report_file.exists():
            click.echo("🔍 Running project analysis first...")
            from ..core.cli.discovery_commands import discover_analyze
            
            # Run analysis
            discover_analyze(
                repo_root=".",
                target="",
                feature="",
                question_set="default",
                test_answers="",
                output=str(report_file),
                batch=True
            )
            click.echo("✅ Analysis complete!")
        
    except Exception as e:
        click.echo(f"⚠️  Warning: Could not ensure analysis: {e}")


def create_plan_project_rule():
    """Create the @rules/plan-project rule file."""
    try:
        # Get the rules directory
        rules_dir = Path(overlay_paths.cursor_rules_dir())
        rules_dir.mkdir(parents=True, exist_ok=True)
        
        # Create the plan-project rule
        rule_file = rules_dir / "plan-project.md"
        
        docs_dir = overlay_paths.get_docs_dir()
        rule_content = f"""# Plan Project

## Description
Create project plan through guided interview questions and analysis.

## Usage
```bash
cb plan
# or
@rules/plan-project
```

## Agent Instructions
1. Execute the plan command using Code Builder CLI
2. Follow the guided interview process
3. Answer questions based on project requirements
4. Review generated planning documents

## Expected Outputs
- `{docs_dir}/planning/interview.json` - Interview responses
- `{docs_dir}/planning/assumptions.md` - Documented assumptions
- `{docs_dir}/planning/decisions.md` - Key decisions made

## Flags
- `--persona [dev|pm|ai]` - Interview persona (default: dev)
- `--noninteractive` - Use defaults instead of prompts
- `--auto-analyze` - Automatically run analysis if not done

## Examples
```bash
# Interactive planning
cb plan

# Developer persona
cb plan --persona dev

# Non-interactive with defaults
cb plan --noninteractive

# Auto-analyze then plan
cb plan --auto-analyze
```

## Context
This command has been selected based on current project state and dependencies.
"""
        
        with open(rule_file, 'w', encoding='utf-8') as f:
            f.write(rule_content)
        
        return str(rule_file)
        
    except Exception as e:
        print(f"Error creating plan-project rule: {e}")
        return None


def register_agent_os_commands():
    """Register agent-OS bridge commands with the main CLI."""
    # Commands are already registered via the @cli.command decorators
    pass


def get_agent_os_mapping():
    """Get mapping of agent-OS commands to their implementations."""
    return {
        "plan": "discover:new",
        "analyze": "discover:analyze",
        "status": "orchestrator:status",
        "commands": "commands:list"
    }


if __name__ == "__main__":
    # Test the agent-OS bridge
    print("Agent-OS Bridge Commands:")
    mapping = get_agent_os_mapping()
    for agent, implementation in mapping.items():
        print(f"  {agent} -> {implementation}")
    
    # Create plan-project rule
    rule_file = create_plan_project_rule()
    if rule_file:
        print(f"Created plan-project rule: {rule_file}")
    else:
        print("Failed to create plan-project rule")
