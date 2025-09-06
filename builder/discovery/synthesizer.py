"""
Discovery Synthesizer - Synthesis phase of discovery.

The DiscoverySynthesizer combines and structures findings from analysis
to create coherent insights and recommendations.
"""

from typing import Dict, List, Any, Optional
from pathlib import Path


class DiscoverySynthesizer:
    """Synthesizes discovery findings into coherent insights."""
    
    def __init__(self):
        """Initialize the discovery synthesizer."""
        self.insights_cache = {}
    
    def synthesize(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize analysis data into structured insights.
        
        Args:
            analysis_data: Data from analysis phase
            
        Returns:
            Synthesis results dictionary
        """
        synthesis_data = {
            'insights': self._generate_insights(analysis_data),
            'recommendations': self._generate_recommendations(analysis_data),
            'patterns': self._identify_patterns(analysis_data),
            'architecture_analysis': self._analyze_architecture(analysis_data),
            'quality_assessment': self._assess_quality(analysis_data),
            'risk_factors': self._identify_risks(analysis_data),
            'opportunities': self._identify_opportunities(analysis_data),
            'summary': self._create_summary(analysis_data)
        }
        
        return synthesis_data
    
    def explain(self, results: Dict[str, Any]) -> str:
        """Generate a human-readable explanation of discovery results.
        
        Args:
            results: Complete discovery results
            
        Returns:
            Explanation string
        """
        if 'error' in results:
            return f"Discovery failed: {results['error']}"
        
        synthesis = results.get('synthesis', {})
        summary = synthesis.get('summary', {})
        
        explanation_parts = []
        
        # Basic info
        target = results.get('target', 'unknown')
        explanation_parts.append(f"Discovery Analysis for: {target}")
        explanation_parts.append("=" * 50)
        
        # Key insights
        insights = synthesis.get('insights', [])
        if insights:
            explanation_parts.append("\nKey Insights:")
            for i, insight in enumerate(insights[:5], 1):  # Top 5 insights
                explanation_parts.append(f"{i}. {insight}")
        
        # Architecture
        arch = synthesis.get('architecture_analysis', {})
        if arch:
            explanation_parts.append(f"\nArchitecture: {arch.get('style', 'unknown')}")
            patterns = arch.get('patterns', [])
            if patterns:
                explanation_parts.append(f"Patterns: {', '.join(patterns)}")
        
        # Quality
        quality = synthesis.get('quality_assessment', {})
        if quality:
            score = quality.get('overall_score', 0)
            explanation_parts.append(f"\nQuality Score: {score}/100")
            
            issues = quality.get('issues', [])
            if issues:
                explanation_parts.append("Issues found:")
                for issue in issues[:3]:  # Top 3 issues
                    explanation_parts.append(f"  - {issue}")
        
        # Recommendations
        recommendations = synthesis.get('recommendations', [])
        if recommendations:
            explanation_parts.append("\nRecommendations:")
            for i, rec in enumerate(recommendations[:3], 1):  # Top 3 recommendations
                explanation_parts.append(f"{i}. {rec}")
        
        return "\n".join(explanation_parts)
    
    def _generate_insights(self, analysis_data: Dict[str, Any]) -> List[str]:
        """Generate key insights from analysis data."""
        insights = []
        
        # Complexity insights
        complexity = analysis_data.get('complexity_metrics', {})
        if complexity:
            lines = complexity.get('lines_of_code', 0)
            if lines > 500:
                insights.append(f"Large codebase with {lines} lines of code")
            elif lines > 200:
                insights.append(f"Moderate codebase with {lines} lines of code")
            else:
                insights.append(f"Small codebase with {lines} lines of code")
            
            cyclomatic = complexity.get('cyclomatic_complexity', 0)
            if cyclomatic > 20:
                insights.append(f"High complexity detected (cyclomatic: {cyclomatic})")
            elif cyclomatic > 10:
                insights.append(f"Moderate complexity (cyclomatic: {cyclomatic})")
        
        # Pattern insights
        patterns = analysis_data.get('code_patterns', [])
        if patterns:
            pattern_names = [p.get('name', '') for p in patterns if p.get('type') == 'design_pattern']
            if pattern_names:
                insights.append(f"Uses design patterns: {', '.join(pattern_names)}")
            
            anti_patterns = [p for p in patterns if p.get('type') == 'anti_pattern']
            if anti_patterns:
                insights.append(f"Potential anti-patterns detected: {len(anti_patterns)}")
        
        # Architecture insights
        architecture = analysis_data.get('architecture', {})
        layers = architecture.get('layers', [])
        if layers:
            insights.append(f"Architectural layers: {', '.join(layers)}")
        
        # Quality insights
        quality = analysis_data.get('quality_indicators', {})
        if quality:
            doc_quality = quality.get('documentation', 'unknown')
            if doc_quality == 'good':
                insights.append("Well-documented code")
            elif doc_quality == 'poor':
                insights.append("Poor documentation coverage")
            
            error_handling = quality.get('error_handling', 'unknown')
            if error_handling == 'present':
                insights.append("Includes error handling")
            elif error_handling == 'missing':
                insights.append("Missing error handling")
        
        return insights
    
    def _generate_recommendations(self, analysis_data: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []
        
        # Complexity recommendations
        complexity = analysis_data.get('complexity_metrics', {})
        if complexity:
            lines = complexity.get('lines_of_code', 0)
            if lines > 500:
                recommendations.append("Consider breaking large files into smaller modules")
            
            cyclomatic = complexity.get('cyclomatic_complexity', 0)
            if cyclomatic > 20:
                recommendations.append("Refactor to reduce cyclomatic complexity")
            elif cyclomatic > 10:
                recommendations.append("Consider simplifying complex functions")
        
        # Quality recommendations
        quality = analysis_data.get('quality_indicators', {})
        if quality:
            doc_quality = quality.get('documentation', 'unknown')
            if doc_quality == 'poor':
                recommendations.append("Add comprehensive documentation")
            
            error_handling = quality.get('error_handling', 'unknown')
            if error_handling == 'missing':
                recommendations.append("Implement proper error handling")
            
            testing = quality.get('testing', 'unknown')
            if testing == 'unknown':
                recommendations.append("Add unit tests for better reliability")
        
        # Security recommendations
        security = analysis_data.get('security_concerns', [])
        if security:
            high_severity = [s for s in security if s.get('severity') == 'high']
            if high_severity:
                recommendations.append("Address high-severity security issues")
        
        # Architecture recommendations
        architecture = analysis_data.get('architecture', {})
        if not architecture.get('layers'):
            recommendations.append("Consider implementing layered architecture")
        
        # Performance recommendations
        performance = analysis_data.get('performance_indicators', {})
        if performance:
            loops = performance.get('loops', 0)
            if loops > 10:
                recommendations.append("Review loop performance and consider optimization")
        
        return recommendations
    
    def _identify_patterns(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Identify and categorize patterns."""
        patterns = {
            'design_patterns': [],
            'anti_patterns': [],
            'architectural_patterns': [],
            'test_patterns': []
        }
        
        code_patterns = analysis_data.get('code_patterns', [])
        for pattern in code_patterns:
            pattern_type = pattern.get('type', '')
            pattern_name = pattern.get('name', '')
            confidence = pattern.get('confidence', 0)
            
            if pattern_type == 'design_pattern':
                patterns['design_patterns'].append({
                    'name': pattern_name,
                    'confidence': confidence
                })
            elif pattern_type == 'anti_pattern':
                patterns['anti_patterns'].append({
                    'name': pattern_name,
                    'confidence': confidence
                })
            elif pattern_type == 'test_pattern':
                patterns['test_patterns'].append({
                    'name': pattern_name,
                    'confidence': confidence
                })
        
        # Architectural patterns
        architecture = analysis_data.get('architecture', {})
        arch_patterns = architecture.get('patterns', [])
        for pattern in arch_patterns:
            patterns['architectural_patterns'].append({
                'name': pattern,
                'confidence': 0.8  # Default confidence for detected patterns
            })
        
        return patterns
    
    def _analyze_architecture(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze architectural aspects."""
        architecture = analysis_data.get('architecture', {})
        
        arch_analysis = {
            'style': 'unknown',
            'patterns': architecture.get('patterns', []),
            'layers': architecture.get('layers', []),
            'coupling': architecture.get('coupling', 'unknown'),
            'cohesion': architecture.get('cohesion', 'unknown'),
            'maturity': 'unknown'
        }
        
        # Determine architectural style
        layers = architecture.get('layers', [])
        patterns = architecture.get('patterns', [])
        
        if 'controller' in layers and 'service' in layers and 'model' in layers:
            arch_analysis['style'] = 'mvc'
        elif 'view' in layers and 'model' in layers:
            arch_analysis['style'] = 'mvp'
        elif 'object_oriented' in patterns:
            arch_analysis['style'] = 'oop'
        elif 'functional' in patterns:
            arch_analysis['style'] = 'functional'
        
        # Assess maturity
        if len(layers) > 2 and len(patterns) > 1:
            arch_analysis['maturity'] = 'mature'
        elif len(layers) > 0 or len(patterns) > 0:
            arch_analysis['maturity'] = 'developing'
        else:
            arch_analysis['maturity'] = 'basic'
        
        return arch_analysis
    
    def _assess_quality(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall code quality."""
        quality_indicators = analysis_data.get('quality_indicators', {})
        maintainability = analysis_data.get('maintainability', {})
        security = analysis_data.get('security_concerns', [])
        
        # Calculate overall score
        score = 100
        issues = []
        
        # Documentation score
        doc_quality = quality_indicators.get('documentation', 'unknown')
        if doc_quality == 'poor':
            score -= 20
            issues.append("Poor documentation")
        elif doc_quality == 'fair':
            score -= 10
            issues.append("Insufficient documentation")
        
        # Error handling score
        error_handling = quality_indicators.get('error_handling', 'unknown')
        if error_handling == 'missing':
            score -= 15
            issues.append("Missing error handling")
        
        # Testing score
        testing = quality_indicators.get('testing', 'unknown')
        if testing == 'unknown':
            score -= 10
            issues.append("No tests detected")
        
        # Maintainability score
        maint_score = maintainability.get('score', 100)
        score = min(score, maint_score)
        
        # Security score
        if security:
            high_severity = len([s for s in security if s.get('severity') == 'high'])
            medium_severity = len([s for s in security if s.get('severity') == 'medium'])
            score -= (high_severity * 20 + medium_severity * 10)
            
            if high_severity > 0:
                issues.append(f"{high_severity} high-severity security issues")
            if medium_severity > 0:
                issues.append(f"{medium_severity} medium-severity security issues")
        
        # Determine quality level
        if score >= 90:
            quality_level = 'excellent'
        elif score >= 80:
            quality_level = 'good'
        elif score >= 70:
            quality_level = 'fair'
        elif score >= 60:
            quality_level = 'poor'
        else:
            quality_level = 'critical'
        
        return {
            'overall_score': max(0, score),
            'quality_level': quality_level,
            'issues': issues,
            'documentation': doc_quality,
            'error_handling': error_handling,
            'testing': testing
        }
    
    def _identify_risks(self, analysis_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify potential risks."""
        risks = []
        
        # Security risks
        security = analysis_data.get('security_concerns', [])
        for issue in security:
            risks.append({
                'type': 'security',
                'severity': issue.get('severity', 'unknown'),
                'description': issue.get('description', ''),
                'line': issue.get('line', 0)
            })
        
        # Complexity risks
        complexity = analysis_data.get('complexity_metrics', {})
        if complexity:
            cyclomatic = complexity.get('cyclomatic_complexity', 0)
            if cyclomatic > 20:
                risks.append({
                    'type': 'complexity',
                    'severity': 'high',
                    'description': f'High cyclomatic complexity ({cyclomatic})',
                    'line': 0
                })
            elif cyclomatic > 10:
                risks.append({
                    'type': 'complexity',
                    'severity': 'medium',
                    'description': f'Moderate cyclomatic complexity ({cyclomatic})',
                    'line': 0
                })
        
        # Maintainability risks
        maintainability = analysis_data.get('maintainability', {})
        maint_score = maintainability.get('score', 100)
        if maint_score < 60:
            risks.append({
                'type': 'maintainability',
                'severity': 'high',
                'description': f'Low maintainability score ({maint_score})',
                'line': 0
            })
        
        return risks
    
    def _identify_opportunities(self, analysis_data: Dict[str, Any]) -> List[str]:
        """Identify improvement opportunities."""
        opportunities = []
        
        # Performance opportunities
        performance = analysis_data.get('performance_indicators', {})
        if performance.get('loops', 0) > 5:
            opportunities.append("Optimize loop performance")
        
        if performance.get('file_operations', False):
            opportunities.append("Consider async file operations")
        
        # Architecture opportunities
        architecture = analysis_data.get('architecture', {})
        if not architecture.get('layers'):
            opportunities.append("Implement layered architecture")
        
        if not architecture.get('patterns'):
            opportunities.append("Apply design patterns")
        
        # Quality opportunities
        quality = analysis_data.get('quality_indicators', {})
        if quality.get('documentation') == 'poor':
            opportunities.append("Improve documentation")
        
        if quality.get('testing') == 'unknown':
            opportunities.append("Add comprehensive testing")
        
        return opportunities
    
    def _create_summary(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a high-level summary."""
        complexity = analysis_data.get('complexity_metrics', {})
        quality = analysis_data.get('quality_indicators', {})
        maintainability = analysis_data.get('maintainability', {})
        
        return {
            'lines_of_code': complexity.get('lines_of_code', 0),
            'complexity_level': self._get_complexity_level(complexity.get('cyclomatic_complexity', 0)),
            'quality_level': quality.get('documentation', 'unknown'),
            'maintainability_score': maintainability.get('score', 0),
            'has_tests': quality.get('testing', 'unknown') != 'unknown',
            'has_error_handling': quality.get('error_handling', 'unknown') == 'present'
        }
    
    def _get_complexity_level(self, cyclomatic: int) -> str:
        """Get complexity level from cyclomatic complexity."""
        if cyclomatic <= 10:
            return 'low'
        elif cyclomatic <= 20:
            return 'moderate'
        else:
            return 'high'
