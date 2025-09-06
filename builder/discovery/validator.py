"""
Discovery Validator - Validation phase of discovery.

The DiscoveryValidator validates the discovery results and ensures
data integrity and consistency across all phases.
"""

from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path


class DiscoveryValidator:
    """Validates discovery results and ensures data integrity."""
    
    def __init__(self, strict_mode: bool = True, min_features: int = 3, min_idea_words: int = 10):
        """Initialize the discovery validator.
        
        Args:
            strict_mode: Enable strict validation rules
            min_features: Minimum number of features required
            min_idea_words: Minimum number of words in product idea
        """
        self.strict_mode = strict_mode
        self.min_features = min_features
        self.min_idea_words = min_idea_words
        self.validation_rules = self._load_validation_rules()
    
    def validate(self, generation_data: Dict[str, Any], synthesis_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Validate discovery generation data.
        
        Args:
            generation_data: Data from generation phase
            synthesis_data: Data from synthesis phase (optional)
            
        Returns:
            Validation results dictionary
        """
        validation_data = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'checks_performed': [],
            'data_integrity': self._check_data_integrity(generation_data),
            'completeness': self._check_completeness(generation_data),
            'consistency': self._check_consistency(generation_data),
            'quality_metrics': self._validate_quality_metrics(generation_data)
        }
        
        # Add synthesis meta validation if available
        if synthesis_data and 'meta' in synthesis_data:
            meta_validation = synthesis_data['meta']
            validation_data['synthesis_meta'] = {
                'ok': meta_validation.get('ok', False),
                'errors': meta_validation.get('errors', []),
                'warnings': meta_validation.get('warnings', []),
                'gaps': meta_validation.get('gaps', []),
                'missing_fields': meta_validation.get('missing_fields', []),
                'shell_gaps': meta_validation.get('shell_gaps', [])
            }
            
            # Include synthesis meta errors in overall validation
            if not meta_validation.get('ok', False):
                validation_data['errors'].extend(meta_validation.get('errors', []))
                validation_data['warnings'].extend(meta_validation.get('warnings', []))
        
        # Overall validation status
        validation_data['is_valid'] = (
            len(validation_data['errors']) == 0 and
            validation_data['data_integrity']['is_valid'] and
            validation_data['completeness']['is_complete']
        )
        
        return validation_data
    
    def _check_data_integrity(self, generation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check data integrity of generation results."""
        integrity_checks = {
            'is_valid': True,
            'errors': [],
            'checks': []
        }
        
        # Check required keys
        required_keys = ['reports', 'documentation', 'diagrams', 'recommendations', 'metadata']
        for key in required_keys:
            if key not in generation_data:
                integrity_checks['errors'].append(f"Missing required key: {key}")
                integrity_checks['is_valid'] = False
            else:
                integrity_checks['checks'].append(f"Key '{key}' present")
        
        # Check report formats
        reports = generation_data.get('reports', {})
        expected_formats = ['json', 'markdown', 'text']
        for format_name in expected_formats:
            if format_name not in reports:
                integrity_checks['errors'].append(f"Missing report format: {format_name}")
                integrity_checks['is_valid'] = False
            elif not isinstance(reports[format_name], str):
                integrity_checks['errors'].append(f"Invalid report format '{format_name}': not a string")
                integrity_checks['is_valid'] = False
            else:
                integrity_checks['checks'].append(f"Report format '{format_name}' valid")
        
        # Check documentation structure
        docs = generation_data.get('documentation', {})
        if not isinstance(docs, dict):
            integrity_checks['errors'].append("Documentation should be a dictionary")
            integrity_checks['is_valid'] = False
        else:
            integrity_checks['checks'].append("Documentation structure valid")
        
        # Check metadata
        metadata = generation_data.get('metadata', {})
        if not isinstance(metadata, dict):
            integrity_checks['errors'].append("Metadata should be a dictionary")
            integrity_checks['is_valid'] = False
        else:
            integrity_checks['checks'].append("Metadata structure valid")
        
        return integrity_checks
    
    def _check_completeness(self, generation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check completeness of generation results."""
        completeness_checks = {
            'is_complete': True,
            'missing_items': [],
            'checks': []
        }
        
        # Check reports completeness
        reports = generation_data.get('reports', {})
        if not reports:
            completeness_checks['missing_items'].append("No reports generated")
            completeness_checks['is_complete'] = False
        else:
            completeness_checks['checks'].append("Reports generated")
        
        # Check documentation completeness
        docs = generation_data.get('documentation', {})
        if not docs:
            completeness_checks['missing_items'].append("No documentation generated")
            completeness_checks['is_complete'] = False
        else:
            completeness_checks['checks'].append("Documentation generated")
        
        # Check recommendations completeness
        recommendations = generation_data.get('recommendations', {})
        if not recommendations:
            completeness_checks['missing_items'].append("No recommendations generated")
            completeness_checks['is_complete'] = False
        else:
            completeness_checks['checks'].append("Recommendations generated")
        
        # Check diagrams completeness
        diagrams = generation_data.get('diagrams', {})
        if not diagrams:
            completeness_checks['missing_items'].append("No diagrams generated")
            completeness_checks['is_complete'] = False
        else:
            completeness_checks['checks'].append("Diagrams generated")
        
        return completeness_checks
    
    def _check_consistency(self, generation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check consistency across generation results."""
        consistency_checks = {
            'is_consistent': True,
            'inconsistencies': [],
            'checks': []
        }
        
        # Check that all reports contain similar information
        reports = generation_data.get('reports', {})
        if len(reports) > 1:
            # Basic consistency check - all reports should mention the target
            target_mentioned = []
            for format_name, content in reports.items():
                if isinstance(content, str) and 'target' in content.lower():
                    target_mentioned.append(format_name)
            
            if len(target_mentioned) != len(reports):
                consistency_checks['inconsistencies'].append(
                    f"Not all reports mention target: {target_mentioned}"
                )
                consistency_checks['is_consistent'] = False
            else:
                consistency_checks['checks'].append("All reports mention target")
        
        # Check metadata consistency
        metadata = generation_data.get('metadata', {})
        if metadata:
            # Check that metadata has required fields
            required_metadata = ['target', 'timestamp', 'version']
            missing_metadata = [field for field in required_metadata if field not in metadata]
            
            if missing_metadata:
                consistency_checks['inconsistencies'].append(
                    f"Missing metadata fields: {missing_metadata}"
                )
                consistency_checks['is_consistent'] = False
            else:
                consistency_checks['checks'].append("Metadata fields complete")
        
        return consistency_checks
    
    def _validate_quality_metrics(self, generation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate quality metrics in generation data."""
        quality_validation = {
            'is_valid': True,
            'issues': [],
            'metrics': {}
        }
        
        # Check report quality
        reports = generation_data.get('reports', {})
        for format_name, content in reports.items():
            if isinstance(content, str):
                # Check minimum length
                if len(content) < 100:
                    quality_validation['issues'].append(
                        f"Report '{format_name}' too short ({len(content)} chars)"
                    )
                    quality_validation['is_valid'] = False
                else:
                    quality_validation['metrics'][f'{format_name}_length'] = len(content)
                
                # Check for basic structure
                if format_name == 'markdown' and not content.startswith('#'):
                    quality_validation['issues'].append(
                        f"Markdown report missing header"
                    )
                    quality_validation['is_valid'] = False
                
                if format_name == 'json':
                    try:
                        import json
                        json.loads(content)
                        quality_validation['metrics'][f'{format_name}_valid_json'] = True
                    except json.JSONDecodeError:
                        quality_validation['issues'].append(
                            f"JSON report contains invalid JSON"
                        )
                        quality_validation['is_valid'] = False
        
        # Check documentation quality
        docs = generation_data.get('documentation', {})
        if docs:
            doc_count = len(docs)
            quality_validation['metrics']['documentation_count'] = doc_count
            
            if doc_count == 0:
                quality_validation['issues'].append("No documentation generated")
                quality_validation['is_valid'] = False
        
        # Check recommendations quality
        recommendations = generation_data.get('recommendations', {})
        if recommendations:
            rec_count = sum(len(items) for items in recommendations.values() if isinstance(items, list))
            quality_validation['metrics']['recommendation_count'] = rec_count
            
            if rec_count == 0:
                quality_validation['issues'].append("No recommendations generated")
                quality_validation['is_valid'] = False
        
        return quality_validation
    
    def _load_validation_rules(self) -> Dict[str, Any]:
        """Load validation rules from configuration."""
        # Default validation rules - in real implementation, load from config
        return {
            'min_report_length': 100,
            'required_report_formats': ['json', 'markdown', 'text'],
            'required_documentation': ['README'],
            'required_metadata_fields': ['target', 'timestamp', 'version']
        }
    
    def validate_synthesis_data(self, synthesis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate synthesis data specifically."""
        validation = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'checks': []
        }
        
        # Check required synthesis keys
        required_keys = ['insights', 'recommendations', 'patterns', 'architecture_analysis', 'quality_assessment']
        for key in required_keys:
            if key not in synthesis_data:
                validation['errors'].append(f"Missing synthesis key: {key}")
                validation['is_valid'] = False
            else:
                validation['checks'].append(f"Synthesis key '{key}' present")
        
        # Validate insights
        insights = synthesis_data.get('insights', [])
        if not isinstance(insights, list):
            validation['errors'].append("Insights should be a list")
            validation['is_valid'] = False
        elif len(insights) == 0:
            validation['warnings'].append("No insights generated")
        else:
            validation['checks'].append(f"Generated {len(insights)} insights")
        
        # Validate recommendations
        recommendations = synthesis_data.get('recommendations', [])
        if not isinstance(recommendations, list):
            validation['errors'].append("Recommendations should be a list")
            validation['is_valid'] = False
        elif len(recommendations) == 0:
            validation['warnings'].append("No recommendations generated")
        else:
            validation['checks'].append(f"Generated {len(recommendations)} recommendations")
        
        # Validate quality assessment
        quality = synthesis_data.get('quality_assessment', {})
        if not isinstance(quality, dict):
            validation['errors'].append("Quality assessment should be a dictionary")
            validation['is_valid'] = False
        else:
            score = quality.get('overall_score', 0)
            if not isinstance(score, (int, float)) or score < 0 or score > 100:
                validation['errors'].append("Invalid quality score")
                validation['is_valid'] = False
            else:
                validation['checks'].append(f"Quality score valid: {score}")
        
        return validation
    
    def validate_interview_data(self, interview_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate interview data specifically."""
        validation = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'checks': []
        }
        
        # Check required interview keys
        required_keys = ['target_type', 'file_info', 'dependencies', 'structure']
        for key in required_keys:
            if key not in interview_data:
                validation['errors'].append(f"Missing interview key: {key}")
                validation['is_valid'] = False
            else:
                validation['checks'].append(f"Interview key '{key}' present")
        
        # Validate target type
        target_type = interview_data.get('target_type')
        if target_type not in ['file', 'directory', 'unknown']:
            validation['errors'].append(f"Invalid target type: {target_type}")
            validation['is_valid'] = False
        else:
            validation['checks'].append(f"Target type valid: {target_type}")
        
        # Validate file info
        file_info = interview_data.get('file_info', {})
        if not isinstance(file_info, dict):
            validation['errors'].append("File info should be a dictionary")
            validation['is_valid'] = False
        else:
            validation['checks'].append("File info structure valid")
        
        return validation
    
    def get_validation_summary(self, validation_data: Dict[str, Any]) -> str:
        """Get a human-readable validation summary."""
        if validation_data.get('is_valid', False):
            return "✅ Validation passed - All checks successful"
        
        errors = validation_data.get('errors', [])
        warnings = validation_data.get('warnings', [])
        
        summary_parts = []
        
        if errors:
            summary_parts.append(f"❌ {len(errors)} errors found:")
            for error in errors[:5]:  # Show first 5 errors
                summary_parts.append(f"  - {error}")
            if len(errors) > 5:
                summary_parts.append(f"  ... and {len(errors) - 5} more errors")
        
        if warnings:
            summary_parts.append(f"⚠️  {len(warnings)} warnings:")
            for warning in warnings[:3]:  # Show first 3 warnings
                summary_parts.append(f"  - {warning}")
            if len(warnings) > 3:
                summary_parts.append(f"  ... and {len(warnings) - 3} more warnings")
        
        return "\n".join(summary_parts)
    
    def validate_strict_spec(self, discovery_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate discovery data against strict specification requirements.
        
        Args:
            discovery_data: Complete discovery data including interview, analysis, synthesis
            
        Returns:
            Validation results with strict spec compliance
        """
        validation = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'gaps': [],
            'checks_performed': [],
            'spec_compliance': {}
        }
        
        if not self.strict_mode:
            validation['warnings'].append("Strict mode disabled - using lenient validation")
            return validation
        
        # Extract data from discovery results
        interview_data = discovery_data.get('interview', {})
        synthesis_data = discovery_data.get('synthesis', {})
        
        # Validate product idea length
        product_idea_validation = self._validate_product_idea(interview_data)
        validation['spec_compliance']['product_idea'] = product_idea_validation
        if not product_idea_validation['is_valid']:
            validation['errors'].extend(product_idea_validation['errors'])
            validation['gaps'].extend(product_idea_validation['gaps'])
        validation['checks_performed'].extend(product_idea_validation['checks'])
        
        # Validate minimum features
        features_validation = self._validate_minimum_features(synthesis_data)
        validation['spec_compliance']['features'] = features_validation
        if not features_validation['is_valid']:
            validation['errors'].extend(features_validation['errors'])
            validation['gaps'].extend(features_validation['gaps'])
        validation['checks_performed'].extend(features_validation['checks'])
        
        # Validate feature acceptance criteria
        acceptance_validation = self._validate_feature_acceptance(synthesis_data)
        validation['spec_compliance']['acceptance_criteria'] = acceptance_validation
        if not acceptance_validation['is_valid']:
            validation['errors'].extend(acceptance_validation['errors'])
            validation['gaps'].extend(acceptance_validation['gaps'])
        validation['checks_performed'].extend(acceptance_validation['checks'])
        
        # Overall validation status
        validation['is_valid'] = (
            len(validation['errors']) == 0 and
            all(spec.get('is_valid', False) for spec in validation['spec_compliance'].values())
        )
        
        return validation
    
    def _validate_product_idea(self, interview_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate product idea meets minimum word requirement."""
        validation = {
            'is_valid': True,
            'errors': [],
            'gaps': [],
            'checks': []
        }
        
        # Extract product idea from interview data
        # Handle different data structures
        product_idea = ''
        
        # Try different possible locations for the product idea
        if 'questions' in interview_data:
            product_idea = interview_data['questions'].get('main_idea', '')
        elif 'data' in interview_data:
            # Handle discovery_phases.interview.data structure
            data = interview_data['data']
            product_idea = data.get('product_scope', '') or data.get('main_idea', '')
        elif 'main_idea' in interview_data:
            product_idea = interview_data['main_idea']
        elif 'product_scope' in interview_data:
            product_idea = interview_data['product_scope']
        
        if not product_idea:
            validation['errors'].append("Product idea is missing")
            validation['gaps'].append("No main idea provided")
            validation['is_valid'] = False
        else:
            # Count words in product idea
            word_count = len(product_idea.split())
            validation['checks'].append(f"Product idea word count: {word_count}")
            
            if word_count < self.min_idea_words:
                validation['errors'].append(
                    f"Product idea too short: {word_count} words (minimum: {self.min_idea_words})"
                )
                validation['gaps'].append(
                    f"Product idea needs {self.min_idea_words - word_count} more words"
                )
                validation['is_valid'] = False
            else:
                validation['checks'].append(f"Product idea meets minimum word requirement")
        
        return validation
    
    def _validate_minimum_features(self, synthesis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate minimum number of features requirement."""
        validation = {
            'is_valid': True,
            'errors': [],
            'gaps': [],
            'checks': []
        }
        
        # Extract features from synthesis data
        # Handle different data structures
        must_have_features = []
        
        if 'feature_map' in synthesis_data:
            feature_map = synthesis_data['feature_map']
            must_have_features = feature_map.get('must_have', [])
        elif 'features' in synthesis_data:
            # Handle direct features structure
            features = synthesis_data['features']
            if isinstance(features, list):
                must_have_features = features
            elif isinstance(features, dict):
                must_have_features = features.get('must_have', [])
        elif 'must_have' in synthesis_data:
            must_have_features = synthesis_data['must_have']
        elif 'key_features' in synthesis_data:
            # Handle key_features structure
            key_features = synthesis_data['key_features']
            if isinstance(key_features, list):
                must_have_features = key_features
        
        if not must_have_features:
            validation['errors'].append("No must-have features defined")
            validation['gaps'].append("Feature map missing must_have section")
            validation['is_valid'] = False
        else:
            feature_count = len(must_have_features)
            validation['checks'].append(f"Must-have features count: {feature_count}")
            
            if feature_count < self.min_features:
                validation['errors'].append(
                    f"Insufficient features: {feature_count} (minimum: {self.min_features})"
                )
                validation['gaps'].append(
                    f"Need {self.min_features - feature_count} more must-have features"
                )
                validation['is_valid'] = False
            else:
                validation['checks'].append(f"Feature count meets minimum requirement")
        
        return validation
    
    def _validate_feature_acceptance(self, synthesis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate each feature has at least one acceptance criteria."""
        validation = {
            'is_valid': True,
            'errors': [],
            'gaps': [],
            'checks': []
        }
        
        # Extract features and acceptance criteria using same logic as features validation
        must_have_features = []
        
        if 'feature_map' in synthesis_data:
            feature_map = synthesis_data['feature_map']
            must_have_features = feature_map.get('must_have', [])
        elif 'features' in synthesis_data:
            features = synthesis_data['features']
            if isinstance(features, list):
                must_have_features = features
            elif isinstance(features, dict):
                must_have_features = features.get('must_have', [])
        elif 'must_have' in synthesis_data:
            must_have_features = synthesis_data['must_have']
        elif 'key_features' in synthesis_data:
            key_features = synthesis_data['key_features']
            if isinstance(key_features, list):
                must_have_features = key_features
        
        acceptance_criteria = synthesis_data.get('acceptance_criteria', {})
        
        if not must_have_features:
            validation['errors'].append("No features to validate acceptance criteria for")
            validation['gaps'].append("No features available for acceptance criteria validation")
            validation['is_valid'] = False
            return validation
        
        features_without_acceptance = []
        
        for feature in must_have_features:
            feature_name = feature.get('name', '') if isinstance(feature, dict) else str(feature)
            
            # Check if feature has acceptance criteria
            has_acceptance = False
            if isinstance(acceptance_criteria, dict):
                # Look for acceptance criteria for this feature
                for criteria_key, criteria_list in acceptance_criteria.items():
                    if isinstance(criteria_list, list):
                        for criteria in criteria_list:
                            if isinstance(criteria, dict):
                                criteria_feature = criteria.get('feature', '')
                                if criteria_feature and criteria_feature.lower() in feature_name.lower():
                                    has_acceptance = True
                                    break
                            elif isinstance(criteria, str) and feature_name.lower() in criteria.lower():
                                has_acceptance = True
                                break
                    if has_acceptance:
                        break
            
            if not has_acceptance:
                features_without_acceptance.append(feature_name)
        
        if features_without_acceptance:
            validation['errors'].append(
                f"Features without acceptance criteria: {', '.join(features_without_acceptance)}"
            )
            validation['gaps'].append(
                f"Add acceptance criteria for: {', '.join(features_without_acceptance)}"
            )
            validation['is_valid'] = False
        else:
            validation['checks'].append("All features have acceptance criteria")
        
        validation['checks'].append(f"Validated {len(must_have_features)} features for acceptance criteria")
        
        return validation
    
    def get_strict_validation_summary(self, validation_data: Dict[str, Any]) -> str:
        """Get a human-readable strict validation summary."""
        if validation_data.get('is_valid', False):
            return "✅ Strict validation passed - All spec requirements met"
        
        errors = validation_data.get('errors', [])
        warnings = validation_data.get('warnings', [])
        gaps = validation_data.get('gaps', [])
        
        summary_parts = []
        
        if errors:
            summary_parts.append(f"❌ {len(errors)} spec violations found:")
            for error in errors[:5]:  # Show first 5 errors
                summary_parts.append(f"  - {error}")
            if len(errors) > 5:
                summary_parts.append(f"  ... and {len(errors) - 5} more violations")
        
        if gaps:
            summary_parts.append(f"🔍 {len(gaps)} gaps identified:")
            for gap in gaps[:3]:  # Show first 3 gaps
                summary_parts.append(f"  - {gap}")
            if len(gaps) > 3:
                summary_parts.append(f"  ... and {len(gaps) - 3} more gaps")
        
        if warnings:
            summary_parts.append(f"⚠️  {len(warnings)} warnings:")
            for warning in warnings[:3]:  # Show first 3 warnings
                summary_parts.append(f"  - {warning}")
            if len(warnings) > 3:
                summary_parts.append(f"  ... and {len(warnings) - 3} more warnings")
        
        return "\n".join(summary_parts)
