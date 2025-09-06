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
    
    def synthesize(self, analysis_data: Dict[str, Any], interview_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Synthesize analysis and interview data into structured insights.
        
        Args:
            analysis_data: Data from analysis phase
            interview_data: Data from interview phase (optional)
            
        Returns:
            Synthesis results dictionary with validation metadata
        """
        # Merge interview and analysis data
        merged_data = self._merge_interview_and_analysis(interview_data, analysis_data)
        
        # Generate synthesis data
        synthesis_data = {
            'insights': self._generate_insights(merged_data),
            'recommendations': self._generate_recommendations(merged_data),
            'patterns': self._identify_patterns(merged_data),
            'architecture_analysis': self._analyze_architecture(merged_data),
            'quality_assessment': self._assess_quality(merged_data),
            'risk_factors': self._identify_risks(merged_data),
            'opportunities': self._identify_opportunities(merged_data),
            'summary': self._create_summary(merged_data),
            'meta': self._create_validation_metadata(merged_data)
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
    
    def _merge_interview_and_analysis(self, interview_data: Optional[Dict[str, Any]], analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Merge interview and analysis data into a unified structure.
        
        Args:
            interview_data: Data from interview phase
            analysis_data: Data from analysis phase
            
        Returns:
            Merged data dictionary
        """
        merged = {}
        
        # Start with analysis data as base
        merged.update(analysis_data)
        
        # Merge interview data if available
        if interview_data:
            # Merge questions from interview
            if 'questions' in interview_data:
                merged['questions'] = interview_data['questions']
            
            # Merge detected technologies from analysis with interview insights
            if 'detected' in analysis_data:
                merged['detected'] = analysis_data['detected']
            
            # Add interview-specific data
            if 'target_type' in interview_data:
                merged['target_type'] = interview_data['target_type']
            if 'file_info' in interview_data:
                merged['file_info'] = interview_data['file_info']
            if 'dependencies' in interview_data:
                merged['dependencies'] = interview_data['dependencies']
            if 'structure' in interview_data:
                merged['structure'] = interview_data['structure']
            if 'patterns' in interview_data:
                merged['patterns'] = interview_data['patterns']
        
        return merged
    
    def _create_validation_metadata(self, merged_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create validation metadata with gap detection.
        
        Args:
            merged_data: Merged interview and analysis data
            
        Returns:
            Validation metadata dictionary
        """
        validation = {
            'ok': True,
            'errors': [],
            'warnings': [],
            'gaps': [],
            'required_fields': self._get_required_fields(),
            'present_fields': self._get_present_fields(merged_data),
            'missing_fields': []
        }
        
        # Check for required fields
        required_fields = validation['required_fields']
        present_fields = validation['present_fields']
        missing_fields = []
        
        for field in required_fields:
            if field not in present_fields:
                missing_fields.append(field)
                validation['errors'].append(f"Missing required field: {field}")
        
        validation['missing_fields'] = missing_fields
        validation['gaps'] = missing_fields
        
        # Check for minimum shells (basic data presence)
        validation.update(self._check_minimum_shells(merged_data))
        
        # Set overall validation status
        if validation['errors']:
            validation['ok'] = False
        
        return validation
    
    def _get_required_fields(self) -> List[str]:
        """Get list of required fields for validation."""
        return [
            'product_name',
            'main_idea',
            'problem_solved',
            'target_users',
            'key_features',
            'success_metrics'
        ]
    
    def _get_present_fields(self, data: Dict[str, Any]) -> List[str]:
        """Get list of fields present in the data."""
        present_fields = []
        
        # Check top-level fields
        for key in data.keys():
            if data[key] is not None and data[key] != '' and data[key] != []:
                present_fields.append(key)
        
        # Check nested fields in questions
        if 'questions' in data and isinstance(data['questions'], dict):
            for key in data['questions'].keys():
                if data['questions'][key] is not None and data['questions'][key] != '' and data['questions'][key] != []:
                    present_fields.append(key)
        
        return present_fields
    
    def _check_minimum_shells(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check for minimum shell requirements and mark gaps.
        
        Args:
            data: Merged data to validate
            
        Returns:
            Dictionary with shell validation results
        """
        shell_validation = {
            'minimum_shells_met': True,
            'shell_gaps': [],
            'shell_warnings': []
        }
        
        # Check for basic product information
        questions = data.get('questions', {})
        
        # Product identity shell
        if not questions.get('product_name') or questions.get('product_name') == 'Not specified':
            shell_validation['shell_gaps'].append('product_identity')
            shell_validation['shell_warnings'].append('Product name not specified')
        
        # Problem definition shell
        if not questions.get('problem_solved') or questions.get('problem_solved') == 'Not specified':
            shell_validation['shell_gaps'].append('problem_definition')
            shell_validation['shell_warnings'].append('Problem definition missing')
        
        # User definition shell
        if not questions.get('target_users') or questions.get('target_users') == 'Not specified':
            shell_validation['shell_gaps'].append('user_definition')
            shell_validation['shell_warnings'].append('Target users not specified')
        
        # Feature definition shell
        if not questions.get('key_features') or questions.get('key_features') == 'Not specified':
            shell_validation['shell_gaps'].append('feature_definition')
            shell_validation['shell_warnings'].append('Key features not specified')
        
        # Success metrics shell
        if not questions.get('success_metrics') or questions.get('success_metrics') == 'Not specified':
            shell_validation['shell_gaps'].append('success_metrics')
            shell_validation['shell_warnings'].append('Success metrics not defined')
        
        # Technical stack shell
        detected = data.get('detected', {})
        if not detected.get('languages') and not detected.get('frameworks'):
            shell_validation['shell_gaps'].append('technical_stack')
            shell_validation['shell_warnings'].append('Technical stack not detected or specified')
        
        # Architecture shell
        architecture = data.get('architecture_analysis', {})
        if not architecture.get('layers') and not architecture.get('patterns'):
            shell_validation['shell_gaps'].append('architecture_definition')
            shell_validation['shell_warnings'].append('Architecture not defined or detected')
        
        # Testing shell
        test_runners = detected.get('test_runners', [])
        if not test_runners:
            shell_validation['shell_gaps'].append('testing_framework')
            shell_validation['shell_warnings'].append('Testing framework not detected or specified')
        
        # Set overall shell validation status
        if shell_validation['shell_gaps']:
            shell_validation['minimum_shells_met'] = False
        
        return shell_validation
