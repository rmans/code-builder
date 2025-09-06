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
        
        # Validate user stories format
        story_validation = self._validate_user_stories(discovery_data)
        validation['spec_compliance']['user_stories'] = story_validation
        if not story_validation['is_valid']:
            validation['errors'].extend(story_validation['errors'])
            validation['gaps'].extend(story_validation['errors'])
        validation['warnings'].extend(story_validation['warnings'])
        validation['checks_performed'].append('user_story_format')
        
        # Validate metrics
        metrics_validation = self._validate_metrics(discovery_data)
        validation['spec_compliance']['metrics'] = metrics_validation
        if not metrics_validation['is_valid']:
            validation['errors'].extend(metrics_validation['errors'])
            validation['gaps'].extend(metrics_validation['errors'])
        validation['warnings'].extend(metrics_validation['warnings'])
        validation['checks_performed'].append('metrics_validation')
        
        # Validate KPIs
        kpi_validation = self._validate_kpis(discovery_data)
        validation['spec_compliance']['kpis'] = kpi_validation
        if not kpi_validation['is_valid']:
            validation['errors'].extend(kpi_validation['errors'])
            validation['gaps'].extend(kpi_validation['errors'])
        validation['warnings'].extend(kpi_validation['warnings'])
        validation['checks_performed'].append('kpi_validation')
        
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

    def _validate_user_stories(self, discovery_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate user story format matches 'As a ... I want ... so that ...' pattern."""
        story_validation = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'valid_stories': [],
            'invalid_stories': []
        }
        
        # Extract user stories from various possible locations
        stories = []
        
        # Check features with user stories
        features = self._extract_features(discovery_data)
        for feature in features:
            if isinstance(feature, dict) and 'user_story' in feature:
                stories.append(feature['user_story'])
            elif isinstance(feature, str):
                # Try to find user story in feature description
                if 'as a' in feature.lower() or 'i want' in feature.lower():
                    stories.append(feature)
        
        # Check direct user stories in discovery data
        if 'user_stories' in discovery_data:
            stories.extend(discovery_data['user_stories'])
        
        # Check features_with_stories
        if 'features_with_stories' in discovery_data:
            for item in discovery_data['features_with_stories']:
                if isinstance(item, dict) and 'user_story' in item:
                    stories.append(item['user_story'])
        
        # Validate each story
        for story in stories:
            if not story or not isinstance(story, str):
                continue
                
            story = story.strip()
            if self._is_valid_user_story(story):
                story_validation['valid_stories'].append(story)
            else:
                story_validation['invalid_stories'].append(story)
                story_validation['errors'].append(
                    f"Invalid user story format: '{story[:50]}{'...' if len(story) > 50 else ''}'"
                )
                story_validation['is_valid'] = False
        
        # Add helpful guidance for invalid stories
        if story_validation['invalid_stories']:
            story_validation['warnings'].append(
                "User stories should follow format: 'As a [user type] I want [goal] so that [benefit]'"
            )
        
        return story_validation
    
    def _is_valid_user_story(self, story: str) -> bool:
        """Check if user story follows the proper format."""
        story_lower = story.lower().strip()
        
        # Must start with "as a"
        if not story_lower.startswith('as a'):
            return False
        
        # Must contain "i want"
        if 'i want' not in story_lower:
            return False
        
        # Must contain "so that"
        if 'so that' not in story_lower:
            return False
        
        # Check for reasonable structure
        parts = story_lower.split('i want')
        if len(parts) < 2:
            return False
        
        # Check that there's content between "as a" and "i want"
        as_a_part = parts[0].strip()
        if len(as_a_part) < 5:  # "as a" + at least 2 chars
            return False
        
        # Check that there's content between "i want" and "so that"
        want_so_part = parts[1]
        if 'so that' not in want_so_part:
            return False
        
        want_parts = want_so_part.split('so that')
        if len(want_parts) < 2:
            return False
        
        want_content = want_parts[0].strip()
        so_that_content = want_parts[1].strip()
        
        # Both parts should have meaningful content
        if len(want_content) < 3 or len(so_that_content) < 3:
            return False
        
        # Check for placeholder text that indicates incomplete stories
        placeholder_indicators = [
            'not specified', 'needs manual input', 'to be defined', 
            'tbd', 'todo', 'placeholder', 'example', 'sample'
        ]
        
        story_text = story_lower
        if any(indicator in story_text for indicator in placeholder_indicators):
            return False
        
        return True
    
    def _validate_metrics(self, discovery_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate metrics structure and content."""
        metrics_validation = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'metrics_found': [],
            'missing_metrics': []
        }
        
        # Extract metrics from various possible locations
        metrics = {}
        
        # Check direct metrics
        if 'metrics' in discovery_data:
            metrics.update(discovery_data['metrics'])
        
        # Check success metrics
        if 'success_metrics' in discovery_data:
            if isinstance(discovery_data['success_metrics'], dict):
                metrics.update(discovery_data['success_metrics'])
            elif isinstance(discovery_data['success_metrics'], str):
                metrics['success'] = discovery_data['success_metrics']
        
        # Check questions for metrics
        questions = discovery_data.get('questions', {})
        if 'success_metrics' in questions:
            if isinstance(questions['success_metrics'], dict):
                metrics.update(questions['success_metrics'])
            elif isinstance(questions['success_metrics'], str):
                metrics['success'] = questions['success_metrics']
        
        # Validate metrics
        if not metrics:
            metrics_validation['errors'].append("No metrics defined")
            metrics_validation['is_valid'] = False
            metrics_validation['missing_metrics'].append("success")
        else:
            for metric_name, metric_value in metrics.items():
                metrics_validation['metrics_found'].append(metric_name)
                
                if not metric_value or (isinstance(metric_value, str) and not metric_value.strip()):
                    metrics_validation['errors'].append(f"Metric '{metric_name}' is empty")
                    metrics_validation['is_valid'] = False
                elif isinstance(metric_value, str) and len(metric_value.strip()) < 5:
                    metrics_validation['warnings'].append(f"Metric '{metric_name}' is very short")
        
        # Check for success metric specifically
        if 'success' not in metrics:
            metrics_validation['warnings'].append("No 'success' metric defined")
        
        return metrics_validation
    
    def _validate_kpis(self, discovery_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate KPIs have metric, target, and timeframe."""
        kpi_validation = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'valid_kpis': [],
            'invalid_kpis': []
        }
        
        # Extract KPIs from various possible locations
        kpis = []
        
        # Check direct KPIs
        if 'kpis' in discovery_data:
            kpis_data = discovery_data['kpis']
            if isinstance(kpis_data, list):
                kpis.extend(kpis_data)
            elif isinstance(kpis_data, dict):
                kpis.append(kpis_data)
        
        # Check metrics for KPI-like structures
        metrics = discovery_data.get('metrics', {})
        for metric_name, metric_value in metrics.items():
            if isinstance(metric_value, dict) and any(key in metric_value for key in ['target', 'timeframe', 'goal']):
                kpis.append(metric_value)
        
        # Validate each KPI
        for kpi in kpis:
            if not isinstance(kpi, dict):
                kpi_validation['invalid_kpis'].append(str(kpi))
                kpi_validation['errors'].append(f"KPI must be a dictionary: {str(kpi)[:50]}")
                kpi_validation['is_valid'] = False
                continue
            
            # Check required fields
            missing_fields = []
            if 'metric' not in kpi or not kpi['metric']:
                missing_fields.append('metric')
            if 'target' not in kpi or not kpi['target']:
                missing_fields.append('target')
            if 'timeframe' not in kpi or not kpi['timeframe']:
                missing_fields.append('timeframe')
            
            if missing_fields:
                kpi_validation['invalid_kpis'].append(kpi)
                kpi_validation['errors'].append(
                    f"KPI missing required fields: {', '.join(missing_fields)} - {kpi}"
                )
                kpi_validation['is_valid'] = False
            else:
                kpi_validation['valid_kpis'].append(kpi)
        
        # Add helpful guidance
        if kpi_validation['invalid_kpis']:
            kpi_validation['warnings'].append(
                "KPIs should have: metric (what to measure), target (goal value), timeframe (when to achieve)"
            )
        
        return kpi_validation
    
    def _extract_features(self, discovery_data: Dict[str, Any]) -> List[Any]:
        """Extract features from discovery data in various formats."""
        features = []
        
        # Check synthesis data
        synthesis = discovery_data.get('synthesis', {})
        if 'features' in synthesis:
            features.extend(synthesis['features'])
        elif 'feature_map' in synthesis:
            feature_map = synthesis['feature_map']
            if isinstance(feature_map, dict):
                # Extract from feature map structure
                for category, feature_list in feature_map.items():
                    if isinstance(feature_list, list):
                        features.extend(feature_list)
            elif isinstance(feature_map, list):
                features.extend(feature_map)
        
        # Check top-level key_features
        if 'key_features' in discovery_data:
            features.extend(discovery_data['key_features'])
        
        # Check questions
        questions = discovery_data.get('questions', {})
        if 'key_features' in questions:
            features.extend(questions['key_features'])
        
        return features
