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
    
    def generate(self, synthesis_data: Dict[str, Any], target: Path) -> Dict[str, Any]:
        """Generate outputs from synthesis data.
        
        Args:
            synthesis_data: Data from synthesis phase
            target: Target path that was analyzed
            
        Returns:
            Generation results dictionary
        """
        generation_data = {
            'reports': self._generate_reports(synthesis_data, target),
            'documentation': self._generate_documentation(synthesis_data, target),
            'diagrams': self._generate_diagrams(synthesis_data, target),
            'recommendations': self._generate_recommendation_files(synthesis_data, target),
            'metadata': self._generate_metadata(synthesis_data, target)
        }
        
        return generation_data
    
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
