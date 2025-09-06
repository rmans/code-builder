from typing import Dict, Any


class ValidationMethods:
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
