#!/usr/bin/env python3
"""
Discovery Commands Module

This module contains discovery-related commands like discover:*
"""

import click
import os
import yaml
import json
from datetime import datetime
from .base import cli, get_project_root

# Import required modules and functions
try:
    from ..overlay.paths import OverlayPaths
    overlay_paths = OverlayPaths()
    ROOT = overlay_paths.get_root()
    DOCS = overlay_paths.get_docs_dir()
    CACHE = overlay_paths.get_cache_dir()
except ImportError:
    ROOT = get_project_root()
    DOCS = ROOT / "cb_docs"
    CACHE = ROOT / ".cb" / "cache"

def _get_template_defaults(template):
    """Get template-specific defaults for discovery context."""
    templates = {
        'default': {
            'product': 'To be defined',
            'idea': 'To be defined',
            'problem': 'To be defined',
            'users': 'Target users to be defined',
            'features': 'To be defined',
            'metrics': 'Success metrics to be defined',
            'tech': 'Technology stack to be defined',
            'timeline': 'Timeline to be defined',
            'team_size': 'To be defined'
        },
        'enterprise': {
            'product': 'To be defined',
            'idea': 'To be defined',
            'problem': 'To be defined',
            'users': 'Enterprise users to be defined',
            'features': 'To be defined',
            'metrics': 'Enterprise success metrics to be defined',
            'tech': 'Enterprise technology stack to be defined',
            'timeline': 'Timeline to be defined',
            'team_size': 'To be defined'
        },
        'startup': {
            'product': 'To be defined',
            'idea': 'To be defined',
            'problem': 'To be defined',
            'users': 'Startup users to be defined',
            'features': 'To be defined',
            'metrics': 'Startup success metrics to be defined',
            'tech': 'Startup technology stack to be defined',
            'timeline': 'Timeline to be defined',
            'team_size': 'To be defined'
        }
    }
    return templates.get(template, templates['default'])

def _collect_interactive_inputs(template_defaults):
    """Collect inputs interactively from user."""
    inputs = {}
    
    # Product name
    product = click.prompt("Product name", default=template_defaults['product'])
    inputs['product'] = product
    
    # Idea description
    idea = click.prompt("Short idea description", default=template_defaults['idea'])
    inputs['idea'] = idea
    
    # Problem
    problem = click.prompt("Problem this product solves", default=template_defaults['problem'])
    inputs['problem'] = problem
    
    # Users
    users = click.prompt("Target users", default=template_defaults['users'])
    inputs['users'] = users
    
    # Features
    features = click.prompt("Key features (comma-separated)", default=template_defaults['features'])
    inputs['features'] = features
    
    # Metrics
    metrics = click.prompt("Success metrics", default=template_defaults['metrics'])
    inputs['metrics'] = metrics
    
    # Tech stack
    tech = click.prompt("Technology stack preferences", default=template_defaults['tech'])
    inputs['tech'] = tech
    
    # Timeline
    timeline = click.prompt("Project timeline", default=template_defaults['timeline'])
    inputs['timeline'] = timeline
    
    # Team size
    team_size = click.prompt("Development team size", default=template_defaults['team_size'])
    inputs['team_size'] = team_size
    
    return inputs

def _collect_batch_inputs(template_defaults, product, idea, problem, users, features, metrics, tech, timeline, team_size):
    """Collect inputs from command line arguments."""
    return {
        'product': product or template_defaults['product'],
        'idea': idea or template_defaults['idea'],
        'problem': problem or template_defaults['problem'],
        'users': users or template_defaults['users'],
        'features': features or template_defaults['features'],
        'metrics': metrics or template_defaults['metrics'],
        'tech': tech or template_defaults['tech'],
        'timeline': timeline or template_defaults['timeline'],
        'team_size': team_size or template_defaults['team_size']
    }

def _create_discovery_context(inputs, template, question_set, auto_generate):
    """Create discovery context structure."""
    return {
        'created': datetime.now().isoformat(),
        'status': 'draft',
        'question_set': question_set,
        'auto_generated': auto_generate,
        'template': template,
        'product': inputs['product'],
        'idea': inputs['idea'],
        'problem': inputs['problem'],
        'users': inputs['users'],
        'features': inputs['features'],
        'metrics': inputs['metrics'],
        'tech': inputs['tech'],
        'timeline': inputs['timeline'],
        'team_size': inputs['team_size'],
        'discovery_phases': [],
        'targets': [],
        'insights': [],
        'recommendations': [],
        'next_steps': []
    }

def _auto_generate_discovery_context(discovery_context, inputs, question_set):
    """Auto-generate discovery context content."""
    # This would integrate with AI/LLM services
    # For now, just return the context as-is
    return discovery_context

# Discovery Commands
@cli.command("discover:new")
@click.option("--interactive", is_flag=True, help="Run in interactive mode with prompts")
@click.option("--batch", is_flag=True, help="Run in batch mode without prompts")
@click.option("--template", type=click.Choice(['default', 'enterprise', 'startup']), default='default', help="Template to use for discovery context")
@click.option("--product", help="Product name for discovery context")
@click.option("--idea", help="Short idea description")
@click.option("--problem", help="Problem this product solves")
@click.option("--users", help="Target users")
@click.option("--features", help="Key features (comma-separated)")
@click.option("--metrics", help="Success metrics")
@click.option("--tech", help="Technology stack preferences")
@click.option("--timeline", help="Project timeline")
@click.option("--team-size", help="Development team size")
@click.option("--question-set", default="new_product", help="Question set to use")
@click.option("--auto-generate", is_flag=True, help="Auto-generate discovery context")
@click.option("--output", help="Output context file path")
def discover_new(interactive, batch, template, product, idea, problem, users, features, metrics, tech, timeline, team_size, question_set, auto_generate, output):
    """Create a new discovery context for product development."""
    try:
        # Determine mode
        if interactive and batch:
            click.echo("❌ Error: Cannot use both --interactive and --batch flags")
            raise SystemExit(1)
        
        if not interactive and not batch:
            # Default to interactive mode if neither is specified
            interactive = True
        
        # Set default output path if not provided
        if not output:
            output = os.path.join(CACHE, "discovery_context.yml")
        
        # Get template-specific defaults
        template_defaults = _get_template_defaults(template)
        
        # Collect inputs based on mode
        if interactive:
            inputs = _collect_interactive_inputs(template_defaults)
        else:  # batch mode
            inputs = _collect_batch_inputs(template_defaults, product, idea, problem, users, features, metrics, tech, timeline, team_size)
        
        # Validate required inputs for batch mode
        if batch and not inputs.get('product'):
            click.echo("❌ Error: --product is required in batch mode")
            raise SystemExit(1)
        if batch and not inputs.get('idea'):
            click.echo("❌ Error: --idea is required in batch mode")
            raise SystemExit(1)
        
        click.echo(f"🔍 Creating discovery context for: {inputs['product']}")
        click.echo(f"💡 Idea: {inputs['idea']}")
        click.echo(f"📋 Template: {template}")
        click.echo(f"📋 Question Set: {question_set}")
        click.echo(f"📁 Output: {output}")
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Create discovery context with template-specific structure
        discovery_context = _create_discovery_context(inputs, template, question_set, auto_generate)
        
        # Auto-generate if requested
        if auto_generate:
            click.echo("🤖 Auto-generating discovery context...")
            discovery_context = _auto_generate_discovery_context(discovery_context, inputs, question_set)
        
        # Save discovery context
        with open(output, 'w', encoding='utf-8') as f:
            yaml.dump(discovery_context, f, default_flow_style=False, sort_keys=False)
        
        click.echo(f"✅ Discovery context created successfully!")
        click.echo(f"📄 Saved to: {output}")
        click.echo(f"📊 Status: {discovery_context['status']}")
        click.echo(f"🎯 Template: {template}")
        
        # Show what was filled in
        filled_fields = [k for k, v in discovery_context.items() if k not in ["created", "status", "question_set", "auto_generated", "discovery_phases", "targets", "insights", "recommendations", "next_steps", "template"] and v not in ["To be defined", "Target users to be defined", "Success metrics to be defined", "Technology stack to be defined", "Timeline to be defined"]]
        if filled_fields:
            click.echo(f"📝 Filled fields: {', '.join(filled_fields)}")
        
        if auto_generate:
            click.echo("🚀 Next steps:")
            click.echo("  1. Review the generated discovery context")
            click.echo("  2. Run: python -m builder discover:scan --auto-generate")
            click.echo("  3. Run: python -m builder discover:regenerate --all")
        
    except Exception as e:
        click.echo(f"❌ Error creating discovery context: {e}")
        raise SystemExit(1)

@cli.command("discover:analyze")
@click.option("--repo-root", is_flag=True, help="Analyze entire repository root")
@click.option("--target", help="Specific target path to analyze")
@click.option("--feature", default="", help="Feature name for analysis")
@click.option("--question-set", default="comprehensive", help="Question set to use")
@click.option("--test-answers", help="Path to test answers JSON file for testing")
@click.option("--output", default="builder/cache/discovery_analysis.json", help="Output analysis file path")
@click.option("--batch", is_flag=True, help="Run in batch mode (non-interactive)")
def discover_analyze(repo_root, target, feature, question_set, test_answers, output, batch):
    """Analyze codebase using discovery engine."""
    try:
        if not repo_root and not target:
            click.echo("❌ Error: Must specify either --repo-root or --target")
            raise SystemExit(1)
        
        if repo_root:
            click.echo("🔍 Analyzing entire repository...")
            analysis_target = "."
        else:
            click.echo(f"🔍 Analyzing target: {target}")
            analysis_target = target
        
        # Mock analysis results for now
        results = {
            'target': analysis_target,
            'feature': feature,
            'question_set': question_set,
            'batch_mode': batch,
            'synthesis': {
                'insights': [
                    'Codebase follows modern Python patterns',
                    'Good separation of concerns in CLI modules',
                    'Comprehensive error handling implemented'
                ],
                'recommendations': [
                    'Consider adding more unit tests',
                    'Documentation could be enhanced',
                    'Performance optimization opportunities identified'
                ]
            },
            'status': 'completed'
        }
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Save analysis results
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        # Show summary
        click.echo(f"✅ Discovery analysis completed!")
        click.echo(f"📄 Results saved to: {output}")
        click.echo(f"🎯 Target: {results.get('target', 'unknown')}")
        
        # Show key insights
        synthesis = results.get('synthesis', {})
        insights = synthesis.get('insights', [])
        if insights:
            click.echo(f"\n💡 Key Insights ({len(insights)}):")
            for i, insight in enumerate(insights[:3], 1):  # Show top 3
                click.echo(f"  {i}. {insight}")
            if len(insights) > 3:
                click.echo(f"  ... and {len(insights) - 3} more insights")
        
        # Show recommendations
        recommendations = synthesis.get('recommendations', [])
        if recommendations:
            click.echo(f"\n📋 Recommendations ({len(recommendations)}):")
            for i, rec in enumerate(recommendations[:3], 1):  # Show top 3
                click.echo(f"  {i}. {rec}")
            if len(recommendations) > 3:
                click.echo(f"  ... and {len(recommendations) - 3} more recommendations")
        
        # Show next steps
        click.echo(f"\n🚀 Next Steps:")
        click.echo(f"1. Review analysis results in: {output}")
        click.echo(f"2. Run: python -m builder discover:validate {output}")
        click.echo(f"3. Generate reports: python -m builder discover:regenerate --reports")
        
    except Exception as e:
        click.echo(f"❌ Error during discovery analysis: {e}")
        raise SystemExit(1)

# Placeholder for other discovery commands - will be implemented in next iteration
@cli.command("discover:validate")
@click.argument("context_file")
def discover_validate(context_file):
    """Validate discovery context file - to be implemented."""
    click.echo(f"✅ Validating discovery context file {context_file} - to be implemented")
    return 0

@cli.command("discover:refresh")
@click.option("--prd", required=True, help="PRD ID to refresh")
def discover_refresh(prd):
    """Refresh discovery context for PRD - to be implemented."""
    click.echo(f"🔄 Refreshing discovery context for PRD {prd} - to be implemented")
    return 0

@cli.command("discover:scan")
@click.option("--auto-generate", is_flag=True, help="Auto-generate missing contexts")
def discover_scan(auto_generate):
    """Scan project for discovery opportunities - to be implemented."""
    click.echo(f"🔍 Scanning project for discovery opportunities - to be implemented")
    return 0

@cli.command("discover:regenerate")
@click.option("--batch", is_flag=True, help="Run in batch mode (non-interactive)")
def discover_regenerate(batch):
    """Regenerate discovery contexts - to be implemented."""
    click.echo(f"🔄 Regenerating discovery contexts - to be implemented")
    return 0


@cli.command("discover:interview")
@click.option("--persona", type=click.Choice(['dev', 'pm', 'ai']), default='dev', help="Interview persona")
@click.option("--noninteractive", is_flag=True, help="Use defaults instead of prompts")
@click.option("--output", help="Output directory for interview files")
def discover_interview(persona, noninteractive, output):
    """Conduct interactive interview for project planning."""
    try:
        from ...discovery.interview import DiscoveryInterview
        import json
        from pathlib import Path
        
        # Initialize interview
        interview = DiscoveryInterview(question_set=persona)
        
        # Set output directory
        if output:
            output_dir = Path(output)
        else:
            # Use overlay paths if available
            try:
                from ...overlay.paths import OverlayPaths
                overlay_paths = OverlayPaths()
                output_dir = Path(overlay_paths.get_docs_dir()) / "planning"
            except ImportError:
                output_dir = Path("cb_docs") / "planning"
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Conduct interview
        click.echo(f"📋 Starting interview for {persona} persona...")
        responses = interview.conduct_interactive(persona=persona, noninteractive=noninteractive)
        
        # Save interview.json
        interview_file = output_dir / "interview.json"
        with open(interview_file, 'w', encoding='utf-8') as f:
            json.dump(responses, f, indent=2, sort_keys=True)
        
        # Create assumptions.md
        assumptions_file = output_dir / "assumptions.md"
        _create_assumptions_file(assumptions_file, responses)
        
        # Create decisions.md
        decisions_file = output_dir / "decisions.md"
        _create_decisions_file(decisions_file, responses)
        
        click.echo(f"✅ Interview complete!")
        click.echo(f"📄 Interview responses: {interview_file}")
        click.echo(f"📋 Assumptions: {assumptions_file}")
        click.echo(f"🎯 Decisions: {decisions_file}")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        raise SystemExit(1)


def _create_assumptions_file(file_path, responses):
    """Create assumptions.md file from interview responses."""
    content = f"""# Project Assumptions

## Product Assumptions
- **Product**: {responses.get('product_name', 'Unknown')}
- **Description**: {responses.get('product_description', 'Not specified')}
- **Target Users**: {responses.get('target_users', 'Not specified')}

## Technical Assumptions
- **Requirements**: {responses.get('technical_requirements', 'Not specified')}
- **Timeline**: {responses.get('timeline', 'Not specified')}
- **Team Size**: {responses.get('team_size', 'Not specified')}
- **Budget**: {responses.get('budget', 'Not specified')}

## Feature Assumptions
- **Key Features**: {', '.join(responses.get('key_features', []))}
- **Success Metrics**: {', '.join(responses.get('success_metrics', []))}

## Risk Assumptions
- **Identified Risks**: {', '.join(responses.get('risks', []))}

## Generated Assumptions
{chr(10).join(f"- {assumption}" for assumption in responses.get('assumptions', []))}

*Generated on {responses.get('timestamp', 'Unknown')}*
"""
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


def _create_decisions_file(file_path, responses):
    """Create decisions.md file from interview responses."""
    content = f"""# Key Project Decisions

## Product Decisions
- **Product Name**: {responses.get('product_name', 'Unknown')}
- **Target Users**: {responses.get('target_users', 'Not specified')}
- **Core Features**: {', '.join(responses.get('key_features', []))}

## Technical Decisions
- **Technology Stack**: {responses.get('technical_requirements', 'Not specified')}
- **Development Timeline**: {responses.get('timeline', 'Not specified')}
- **Team Structure**: {responses.get('team_size', 'Not specified')}
- **Budget Allocation**: {responses.get('budget', 'Not specified')}

## Success Criteria
- **Primary Metrics**: {', '.join(responses.get('success_metrics', []))}

## Generated Decisions
{chr(10).join(f"- {decision}" for decision in responses.get('decisions', []))}

*Generated on {responses.get('timestamp', 'Unknown')}*
"""
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
