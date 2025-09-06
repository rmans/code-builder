"""
Discovery Generators - Generation phase of discovery.

The DiscoveryGenerators creates various outputs and reports based on
synthesis data, including documentation, diagrams, and recommendations.
"""

import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime


class DiscoveryGenerators:
    """Generates various outputs from discovery synthesis."""
    
    def __init__(self):
        """Initialize the discovery generators."""
        self.output_formats = ['json', 'markdown', 'html', 'txt']
    
    def generate(self, synthesis_data: Dict[str, Any], target: Path) -> tuple[Dict[str, Any], List[str], str]:
        """Generate outputs from synthesis data.
        
        Args:
            synthesis_data: Data from synthesis phase
            target: Target path that was analyzed
            
        Returns:
            Tuple of (artifacts, warnings, prd_id)
        """
        warnings = []
        prd_id = None
        
        try:
            # Generate PRD with proper ID
            prd_id = self._generate_prd_id(synthesis_data)
            prd_artifacts = self._generate_prd_documentation(synthesis_data, target, prd_id)
            
            # Generate other outputs
            generation_data = {
                'reports': self._generate_reports(synthesis_data, target),
                'documentation': self._generate_documentation(synthesis_data, target),
                'diagrams': self._generate_diagrams(synthesis_data, target),
                'recommendations': self._generate_recommendation_files(synthesis_data, target),
                'metadata': self._generate_metadata(synthesis_data, target),
                'prd': prd_artifacts
            }
            
            return generation_data, warnings, prd_id
            
        except OSError as e:
            warnings.append(f"File operation error: {e}")
            # Return partial results on file errors
            return {
                'reports': {},
                'documentation': {},
                'diagrams': {},
                'recommendations': {},
                'metadata': {},
                'prd': {}
            }, warnings, prd_id or "PRD-ERROR"
    
    def _generate_reports(self, synthesis_data: Dict[str, Any], target: Path) -> Dict[str, str]:
        """Generate various report formats."""
        reports = {}
        
        # JSON report
        reports['json'] = self._generate_json_report(synthesis_data, target)
        
        # Markdown report
        reports['markdown'] = self._generate_markdown_report(synthesis_data, target)
        
        # Text report
        reports['text'] = self._generate_text_report(synthesis_data, target)
        
        return reports
    
    def _generate_json_report(self, synthesis_data: Dict[str, Any], target: Path) -> str:
        """Generate JSON report."""
        report_data = {
            'target': str(target),
            'timestamp': datetime.now().isoformat(),
            'synthesis': synthesis_data,
            'generated_by': 'code-builder-discovery'
        }
        
        return json.dumps(report_data, indent=2)
    
    def _generate_markdown_report(self, synthesis_data: Dict[str, Any], target: Path) -> str:
        """Generate Markdown report."""
        lines = []
        
        # Header
        lines.append(f"# Discovery Report: {target.name}")
        lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Target:** `{target}`")
        lines.append("")
        
        # Summary
        summary = synthesis_data.get('summary', {})
        if summary:
            lines.append("## Summary")
            lines.append("")
            lines.append(f"- **Lines of Code:** {summary.get('lines_of_code', 0)}")
            lines.append(f"- **Complexity Level:** {summary.get('complexity_level', 'unknown')}")
            lines.append(f"- **Quality Level:** {summary.get('quality_level', 'unknown')}")
            lines.append(f"- **Maintainability Score:** {summary.get('maintainability_score', 0)}/100")
            lines.append(f"- **Has Tests:** {'Yes' if summary.get('has_tests') else 'No'}")
            lines.append(f"- **Has Error Handling:** {'Yes' if summary.get('has_error_handling') else 'No'}")
            lines.append("")
        
        # Insights
        insights = synthesis_data.get('insights', [])
        if insights:
            lines.append("## Key Insights")
            lines.append("")
            for i, insight in enumerate(insights, 1):
                lines.append(f"{i}. {insight}")
            lines.append("")
        
        # Architecture Analysis
        arch = synthesis_data.get('architecture_analysis', {})
        if arch:
            lines.append("## Architecture Analysis")
            lines.append("")
            lines.append(f"- **Style:** {arch.get('style', 'unknown')}")
            lines.append(f"- **Maturity:** {arch.get('maturity', 'unknown')}")
            
            patterns = arch.get('patterns', [])
            if patterns:
                lines.append(f"- **Patterns:** {', '.join(patterns)}")
            
            layers = arch.get('layers', [])
            if layers:
                lines.append(f"- **Layers:** {', '.join(layers)}")
            lines.append("")
        
        # Quality Assessment
        quality = synthesis_data.get('quality_assessment', {})
        if quality:
            lines.append("## Quality Assessment")
            lines.append("")
            score = quality.get('overall_score', 0)
            level = quality.get('quality_level', 'unknown')
            lines.append(f"- **Overall Score:** {score}/100 ({level})")
            
            issues = quality.get('issues', [])
            if issues:
                lines.append("- **Issues:**")
                for issue in issues:
                    lines.append(f"  - {issue}")
            lines.append("")
        
        # Patterns
        patterns = synthesis_data.get('patterns', {})
        if patterns:
            lines.append("## Patterns")
            lines.append("")
            
            design_patterns = patterns.get('design_patterns', [])
            if design_patterns:
                lines.append("### Design Patterns")
                for pattern in design_patterns:
                    name = pattern.get('name', '')
                    confidence = pattern.get('confidence', 0)
                    lines.append(f"- {name} (confidence: {confidence:.1f})")
                lines.append("")
            
            anti_patterns = patterns.get('anti_patterns', [])
            if anti_patterns:
                lines.append("### Anti-Patterns")
                for pattern in anti_patterns:
                    name = pattern.get('name', '')
                    confidence = pattern.get('confidence', 0)
                    lines.append(f"- {name} (confidence: {confidence:.1f})")
                lines.append("")
        
        # Recommendations
        recommendations = synthesis_data.get('recommendations', [])
        if recommendations:
            lines.append("## Recommendations")
            lines.append("")
            for i, rec in enumerate(recommendations, 1):
                lines.append(f"{i}. {rec}")
            lines.append("")
        
        # Risk Factors
        risks = synthesis_data.get('risk_factors', [])
        if risks:
            lines.append("## Risk Factors")
            lines.append("")
            for risk in risks:
                risk_type = risk.get('type', 'unknown')
                severity = risk.get('severity', 'unknown')
                description = risk.get('description', '')
                lines.append(f"- **{risk_type.title()}** ({severity}): {description}")
            lines.append("")
        
        # Opportunities
        opportunities = synthesis_data.get('opportunities', [])
        if opportunities:
            lines.append("## Opportunities")
            lines.append("")
            for i, opp in enumerate(opportunities, 1):
                lines.append(f"{i}. {opp}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _generate_text_report(self, synthesis_data: Dict[str, Any], target: Path) -> str:
        """Generate plain text report."""
        lines = []
        
        lines.append(f"DISCOVERY REPORT: {target.name}")
        lines.append("=" * 50)
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Target: {target}")
        lines.append("")
        
        # Summary
        summary = synthesis_data.get('summary', {})
        if summary:
            lines.append("SUMMARY:")
            lines.append(f"  Lines of Code: {summary.get('lines_of_code', 0)}")
            lines.append(f"  Complexity: {summary.get('complexity_level', 'unknown')}")
            lines.append(f"  Quality: {summary.get('quality_level', 'unknown')}")
            lines.append(f"  Maintainability: {summary.get('maintainability_score', 0)}/100")
            lines.append("")
        
        # Key insights
        insights = synthesis_data.get('insights', [])
        if insights:
            lines.append("KEY INSIGHTS:")
            for i, insight in enumerate(insights, 1):
                lines.append(f"  {i}. {insight}")
            lines.append("")
        
        # Recommendations
        recommendations = synthesis_data.get('recommendations', [])
        if recommendations:
            lines.append("RECOMMENDATIONS:")
            for i, rec in enumerate(recommendations, 1):
                lines.append(f"  {i}. {rec}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _generate_documentation(self, synthesis_data: Dict[str, Any], target: Path) -> Dict[str, str]:
        """Generate documentation files."""
        docs = {}
        
        # README for discovery results
        docs['README'] = self._generate_readme(synthesis_data, target)
        
        # Architecture documentation
        docs['ARCHITECTURE'] = self._generate_architecture_doc(synthesis_data, target)
        
        # Quality guidelines
        docs['QUALITY'] = self._generate_quality_doc(synthesis_data, target)
        
        return docs
    
    def _generate_readme(self, synthesis_data: Dict[str, Any], target: Path) -> str:
        """Generate README for discovery results."""
        lines = []
        
        lines.append(f"# Discovery Results: {target.name}")
        lines.append("")
        lines.append("This document contains the results of automated code discovery analysis.")
        lines.append("")
        
        # Quick overview
        summary = synthesis_data.get('summary', {})
        if summary:
            lines.append("## Quick Overview")
            lines.append("")
            lines.append(f"- **File:** {target.name}")
            lines.append(f"- **Size:** {summary.get('lines_of_code', 0)} lines of code")
            lines.append(f"- **Complexity:** {summary.get('complexity_level', 'unknown')}")
            lines.append(f"- **Quality:** {summary.get('quality_level', 'unknown')}")
            lines.append("")
        
        # Next steps
        lines.append("## Next Steps")
        lines.append("")
        lines.append("1. Review the detailed analysis in the generated reports")
        lines.append("2. Address any high-priority recommendations")
        lines.append("3. Consider implementing suggested improvements")
        lines.append("4. Re-run discovery after making changes")
        lines.append("")
        
        return "\n".join(lines)
    
    def _generate_architecture_doc(self, synthesis_data: Dict[str, Any], target: Path) -> str:
        """Generate architecture documentation."""
        lines = []
        
        lines.append("# Architecture Analysis")
        lines.append("")
        
        arch = synthesis_data.get('architecture_analysis', {})
        if arch:
            lines.append(f"**Architectural Style:** {arch.get('style', 'unknown')}")
            lines.append(f"**Maturity Level:** {arch.get('maturity', 'unknown')}")
            lines.append("")
            
            patterns = arch.get('patterns', [])
            if patterns:
                lines.append("## Design Patterns")
                lines.append("")
                for pattern in patterns:
                    lines.append(f"- {pattern}")
                lines.append("")
            
            layers = arch.get('layers', [])
            if layers:
                lines.append("## Architectural Layers")
                lines.append("")
                for layer in layers:
                    lines.append(f"- {layer}")
                lines.append("")
        
        return "\n".join(lines)
    
    def _generate_quality_doc(self, synthesis_data: Dict[str, Any], target: Path) -> str:
        """Generate quality documentation."""
        lines = []
        
        lines.append("# Quality Assessment")
        lines.append("")
        
        quality = synthesis_data.get('quality_assessment', {})
        if quality:
            score = quality.get('overall_score', 0)
            level = quality.get('quality_level', 'unknown')
            lines.append(f"**Overall Quality Score:** {score}/100 ({level})")
            lines.append("")
            
            issues = quality.get('issues', [])
            if issues:
                lines.append("## Issues Found")
                lines.append("")
                for issue in issues:
                    lines.append(f"- {issue}")
                lines.append("")
        
        return "\n".join(lines)
    
    def _generate_diagrams(self, synthesis_data: Dict[str, Any], target: Path) -> Dict[str, str]:
        """Generate diagram files."""
        diagrams = {}
        
        # Mermaid diagram for architecture
        diagrams['architecture.mmd'] = self._generate_architecture_diagram(synthesis_data, target)
        
        # Mermaid diagram for relationships
        diagrams['relationships.mmd'] = self._generate_relationships_diagram(synthesis_data, target)
        
        return diagrams
    
    def _generate_architecture_diagram(self, synthesis_data: Dict[str, Any], target: Path) -> str:
        """Generate Mermaid architecture diagram."""
        lines = []
        
        lines.append("graph TD")
        lines.append(f"    A[{target.name}]")
        
        arch = synthesis_data.get('architecture_analysis', {})
        layers = arch.get('layers', [])
        
        if layers:
            for i, layer in enumerate(layers):
                lines.append(f"    A --> {layer.upper()}[{layer.title()}]")
        
        patterns = arch.get('patterns', [])
        if patterns:
            for pattern in patterns:
                lines.append(f"    A --> {pattern.upper()}[{pattern.title()}]")
        
        return "\n".join(lines)
    
    def _generate_relationships_diagram(self, synthesis_data: Dict[str, Any], target: Path) -> str:
        """Generate Mermaid relationships diagram."""
        lines = []
        
        lines.append("graph LR")
        lines.append(f"    A[{target.name}]")
        
        # This would be populated with actual relationship data
        # For now, just show a basic structure
        lines.append("    A --> B[Imports]")
        lines.append("    A --> C[Exports]")
        lines.append("    A --> D[Dependencies]")
        
        return "\n".join(lines)
    
    def _generate_recommendation_files(self, synthesis_data: Dict[str, Any], target: Path) -> Dict[str, str]:
        """Generate recommendation files."""
        recommendations = {}
        
        # High priority recommendations
        high_priority = []
        medium_priority = []
        low_priority = []
        
        recs = synthesis_data.get('recommendations', [])
        for rec in recs:
            # Simple priority assignment based on keywords
            if any(word in rec.lower() for word in ['security', 'critical', 'urgent', 'fix']):
                high_priority.append(rec)
            elif any(word in rec.lower() for word in ['improve', 'optimize', 'consider']):
                medium_priority.append(rec)
            else:
                low_priority.append(rec)
        
        if high_priority:
            recommendations['HIGH_PRIORITY.md'] = self._format_priority_list(high_priority, "High Priority")
        
        if medium_priority:
            recommendations['MEDIUM_PRIORITY.md'] = self._format_priority_list(medium_priority, "Medium Priority")
        
        if low_priority:
            recommendations['LOW_PRIORITY.md'] = self._format_priority_list(low_priority, "Low Priority")
        
        return recommendations
    
    def _format_priority_list(self, items: List[str], title: str) -> str:
        """Format a priority list as Markdown."""
        lines = []
        lines.append(f"# {title} Recommendations")
        lines.append("")
        
        for i, item in enumerate(items, 1):
            lines.append(f"{i}. {item}")
        
        return "\n".join(lines)
    
    def _generate_metadata(self, synthesis_data: Dict[str, Any], target: Path) -> Dict[str, Any]:
        """Generate metadata about the discovery process."""
        return {
            'target': str(target),
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'generator': 'code-builder-discovery',
            'formats_generated': list(self.output_formats),
            'synthesis_keys': list(synthesis_data.keys())
        }
    
    def _generate_prd_id(self, synthesis_data: Dict[str, Any]) -> str:
        """Generate PRD ID in format PRD-YYYY-MM-DD-slug.
        
        Args:
            synthesis_data: Data from synthesis phase
            
        Returns:
            PRD ID string
        """
        # Get product name from synthesis data
        questions = synthesis_data.get('questions', {})
        product_name = questions.get('product_name', 'Unknown Product')
        
        # Create slug from product name
        slug = self._create_slug(product_name)
        
        # Get current date
        today = datetime.now()
        date_str = today.strftime('%Y-%m-%d')
        
        return f"PRD-{date_str}-{slug}"
    
    def _create_slug(self, text: str) -> str:
        """Create URL-safe slug from text.
        
        Args:
            text: Input text
            
        Returns:
            URL-safe slug
        """
        import re
        
        # Convert to lowercase and replace spaces with hyphens
        slug = text.lower()
        # Remove special characters except hyphens
        slug = re.sub(r'[^a-z0-9-]', '', slug)
        # Replace multiple hyphens with single hyphen
        slug = re.sub(r'-+', '-', slug)
        # Remove leading/trailing hyphens
        slug = slug.strip('-')
        
        return slug or 'product'
    
    def _generate_prd_documentation(self, synthesis_data: Dict[str, Any], target: Path, prd_id: str) -> Dict[str, str]:
        """Generate PRD documentation with proper ID and ADR linking.
        
        Args:
            synthesis_data: Data from synthesis phase
            target: Target path that was analyzed
            prd_id: Generated PRD ID
            
        Returns:
            Dictionary of PRD artifacts
        """
        prd_artifacts = {}
        
        try:
            # Ensure docs/prd directory exists
            prd_dir = Path('docs/prd')
            prd_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate main PRD file
            prd_content = self._generate_prd_content(synthesis_data, prd_id)
            prd_file = prd_dir / f"{prd_id}.md"
            
            with open(prd_file, 'w', encoding='utf-8') as f:
                f.write(prd_content)
            
            prd_artifacts[f"{prd_id}.md"] = prd_content
            
            # Update master PRD file
            self._update_master_prd_file(prd_id, synthesis_data)
            
            # Note: ADR linking is handled by the existing master ADR system
            # No need to create separate ADR-link files
            
        except OSError as e:
            # Handle file operation errors gracefully
            prd_artifacts['error'] = f"Failed to generate PRD documentation: {e}"
        
        return prd_artifacts
    
    def _update_master_prd_file(self, prd_id: str, synthesis_data: Dict[str, Any]) -> None:
        """Update the master PRD file with the new PRD entry."""
        master_file = Path('docs/prd/0000_MASTER_PRD.md')
        if not master_file.exists():
            return
        
        # Extract title from synthesis data
        questions = synthesis_data.get('questions', {})
        title = questions.get('product_name', 'Unknown Product')
        
        # Check if entry already exists
        try:
            with open(master_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if prd_id already exists in the file
            if f"| {prd_id} |" in content:
                return  # Entry already exists, skip update
            
            # Create the new row
            row = f"| {prd_id} | {title} | draft |  | ./{prd_id}.md |\n"
            
            # Append to master file
            with open(master_file, 'a', encoding='utf-8') as f:
                f.write(row)
        except OSError as e:
            # Silently fail for master file updates
            pass
    
    def _generate_prd_content(self, synthesis_data: Dict[str, Any], prd_id: str) -> str:
        """Generate PRD content.
        
        Args:
            synthesis_data: Data from synthesis phase
            prd_id: Generated PRD ID
            
        Returns:
            PRD content as string
        """
        questions = synthesis_data.get('questions', {})
        detected = synthesis_data.get('detected', {})
        
        # Extract key information
        product_name = questions.get('product_name', 'Unknown Product')
        main_idea = questions.get('main_idea', 'No description provided')
        problem_solved = questions.get('problem_solved', 'Not specified')
        target_users = questions.get('target_users', 'Not specified')
        key_features = questions.get('key_features', [])
        success_metrics = questions.get('success_metrics', 'Not specified')
        
        # Get detected technologies
        languages = detected.get('languages', [])
        frameworks = detected.get('frameworks', [])
        test_runners = detected.get('test_runners', [])
        
        # Generate PRD content
        content = f"""# Product Requirements Document: {product_name}

**PRD ID:** {prd_id}  
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Status:** Draft

## Executive Summary

{main_idea}

## Problem Statement

{problem_solved}

## Target Users

{target_users}

## Key Features

"""
        
        if isinstance(key_features, list):
            for i, feature in enumerate(key_features, 1):
                content += f"{i}. {feature}\n"
        else:
            content += f"- {key_features}\n"
        
        content += f"""
## Success Metrics

{success_metrics}

## Technical Stack

"""
        
        if languages:
            content += f"**Languages:** {', '.join(languages)}\n"
        if frameworks:
            content += f"**Frameworks:** {', '.join(frameworks)}\n"
        if test_runners:
            content += f"**Test Runners:** {', '.join(test_runners)}\n"
        
        content += f"""
## Architecture Decisions

This PRD references the following Architecture Decision Records (ADRs):

- [Master ADR Index](./adrs/0000_MASTER_ADR.md) - Complete list of all ADRs
- [ADR-0001: Technology Stack Selection](./adrs/ADR-0001.md)
- [ADR-0002: System Architecture](./adrs/ADR-0002.md)
- [ADR-0003: Data Model Design](./adrs/ADR-0003.md)

*Note: Use `python builder/cli.py adr:new --title "Your Title"` to create new ADRs.*

## Related Documents

- [Master PRD Index](./prd/0000_MASTER_PRD.md) - Complete list of all PRDs
- [Master Architecture Index](./arch/0000_MASTER_ARCH.md) - Complete list of all architecture documents
- [Master Execution Index](./exec/0000_MASTER_EXEC.md) - Complete list of all execution documents
- [Master Implementation Index](./impl/0000_MASTER_IMPL.md) - Complete list of all implementation documents
- [Master Integrations Index](./integrations/0000_MASTER_INTEGRATIONS.md) - Complete list of all integration documents
- [Master Tasks Index](./tasks/0000_MASTER_TASKS.md) - Complete list of all task documents
- [Master UX Index](./ux/0000_MASTER_UX.md) - Complete list of all UX documents

## Implementation Plan

1. **Phase 1:** Core functionality implementation
2. **Phase 2:** User interface development
3. **Phase 3:** Testing and validation
4. **Phase 4:** Deployment and monitoring

## Acceptance Criteria

- [ ] All key features implemented and tested
- [ ] Performance requirements met
- [ ] Security requirements satisfied
- [ ] User acceptance testing completed

## Risks and Mitigation

- **Technical Risk:** Technology stack complexity
  - *Mitigation:* Prototype early, validate assumptions
- **Timeline Risk:** Feature scope creep
  - *Mitigation:* Strict scope management, regular reviews

## Appendices

### A. User Stories

"""
        
        # Add user stories if available
        if isinstance(key_features, list):
            for feature in key_features:
                content += f"- As a user, I want {feature.lower()}, so that I can achieve my goals\n"
        
        content += f"""
### B. Technical Requirements

- **Performance:** Response time < 2 seconds
- **Availability:** 99.9% uptime
- **Security:** OWASP compliance
- **Scalability:** Support 1000+ concurrent users

### C. Dependencies

- External API integrations
- Third-party libraries
- Infrastructure requirements

---

*This PRD is a living document and will be updated as requirements evolve.*
"""
        
        return content
    
