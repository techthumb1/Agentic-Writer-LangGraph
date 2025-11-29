# langgraph_app/template_style_validator.py
# Template-Style Compatibility Validation System
# Prevents content generation mismatches by validating template-style combinations
# RELEVANT FILES: template_loader.py, mcp_enhanced_graph.py, integrated_server.py

import logging
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class CompatibilityLevel(Enum):
    """Compatibility levels between templates and style profiles"""
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"
    INCOMPATIBLE = "incompatible"
    UNKNOWN = "unknown"

@dataclass
class CompatibilityResult:
    """Result of template-style compatibility validation"""
    compatible: bool
    level: CompatibilityLevel
    confidence: float  # 0.0 to 1.0
    reason: str
    suggestions: List[str]
    warnings: List[str]

class TemplateStyleValidator:
    """Validates template-style profile compatibility to prevent content mismatches"""
    
    def __init__(self):
        # Template category characteristics
        self.template_characteristics = {
            'market_analysis': {
                'content_type': 'analytical',
                'structure': 'data_driven',
                'tone_requirements': ['professional', 'objective', 'analytical'],
                'format_needs': ['charts', 'metrics', 'trends'],
                'audience': 'business_analysts',
                'complexity': 'intermediate_to_expert'
            },
            'strategic_brief': {
                'content_type': 'executive',
                'structure': 'concise_strategic',
                'tone_requirements': ['authoritative', 'professional', 'decisive'],
                'format_needs': ['executive_summary', 'recommendations', 'action_items'],
                'audience': 'executives',
                'complexity': 'expert'
            },
            'data_driven_report': {
                'content_type': 'analytical',
                'structure': 'quantitative_analysis',
                'tone_requirements': ['objective', 'technical', 'evidence_based'],
                'format_needs': ['statistical_analysis', 'visualizations', 'methodology'],
                'audience': 'analysts',
                'complexity': 'expert'
            },
            'blog_article': {
                'content_type': 'informational',
                'structure': 'narrative_flow',
                'tone_requirements': ['engaging', 'accessible', 'informative'],
                'format_needs': ['headers', 'examples', 'call_to_action'],
                'audience': 'general',
                'complexity': 'beginner_to_intermediate'
            },
            'business_document': {
                'content_type': 'professional',
                'structure': 'formal_business',
                'tone_requirements': ['professional', 'formal', 'persuasive'],
                'format_needs': ['executive_summary', 'financials', 'implementation'],
                'audience': 'business_stakeholders',
                'complexity': 'intermediate_to_expert'
            }
        }
        
        # Style profile characteristics (derived from existing profiles)
        self.style_characteristics = {
            'market_flash': {
                'content_focus': 'data_driven_analysis',
                'tone': 'business_analytical',
                'structure_preference': 'metric_based',
                'audience_level': 'professional',
                'complexity_match': 'intermediate',
                'format_requirements': ['charts', 'data_points', 'trends']
            },
            'strategic_planning': {
                'content_focus': 'strategic_analysis',
                'tone': 'authoritative_professional',
                'structure_preference': 'strategic_framework',
                'audience_level': 'executive',
                'complexity_match': 'expert',
                'format_requirements': ['strategic_options', 'recommendations', 'implementation']
            },
            'technical_dive': {
                'content_focus': 'technical_analysis',
                'tone': 'technical_professional',
                'structure_preference': 'deep_analysis',
                'audience_level': 'technical_experts',
                'complexity_match': 'expert',
                'format_requirements': ['technical_details', 'code_examples', 'architecture']
            },
            'social_media_voice': {
                'content_focus': 'engagement_focused',
                'tone': 'casual_engaging',
                'structure_preference': 'bite_sized',
                'audience_level': 'general',
                'complexity_match': 'beginner',
                'format_requirements': ['hashtags', 'short_form', 'visual_elements']
            },
            'executive_summary': {
                'content_focus': 'high_level_overview',
                'tone': 'executive_professional',
                'structure_preference': 'concise_structured',
                'audience_level': 'executive',
                'complexity_match': 'intermediate_to_expert',
                'format_requirements': ['key_points', 'decisions', 'action_items']
            }
        }
        
        # Incompatible combinations with specific reasons
        self.incompatible_combinations = {
            ('market_analysis', 'social_media_voice'): 'Analytical content incompatible with casual social media tone',
            ('strategic_brief', 'beginner_tutorial'): 'Executive-level content incompatible with beginner educational style',
            ('data_driven_report', 'brand_storytelling'): 'Quantitative analysis incompatible with narrative storytelling',
            ('business_document', 'conversational_mentor'): 'Formal business content incompatible with casual mentoring tone'
        }

    def validate_compatibility(self, template_type: str, style_profile: str) -> CompatibilityResult:
        """
        Validate compatibility between template type and style profile
        
        Args:
            template_type: Type of content template
            style_profile: Style profile identifier
            
        Returns:
            CompatibilityResult with validation details
        """
        
        # Check for explicit incompatibilities
        if (template_type, style_profile) in self.incompatible_combinations:
            return CompatibilityResult(
                compatible=False,
                level=CompatibilityLevel.INCOMPATIBLE,
                confidence=0.95,
                reason=self.incompatible_combinations[(template_type, style_profile)],
                suggestions=[f"Use {self._suggest_compatible_style(template_type)} style instead"],
                warnings=[f"This combination will produce confused content"]
            )
        
        # Get characteristics
        template_chars = self.template_characteristics.get(template_type)
        style_chars = self.style_characteristics.get(style_profile)
        
        if not template_chars or not style_chars:
            return CompatibilityResult(
                compatible=True,
                level=CompatibilityLevel.UNKNOWN,
                confidence=0.5,
                reason="No compatibility data available",
                suggestions=["Monitor output quality for potential mismatches"],
                warnings=["Unknown compatibility - review generated content carefully"]
            )
        
        # Calculate compatibility score
        score, details = self._calculate_compatibility_score(template_chars, style_chars)
        
        # Determine compatibility level
        if score >= 0.8:
            level = CompatibilityLevel.HIGH
            compatible = True
        elif score >= 0.6:
            level = CompatibilityLevel.MODERATE
            compatible = True
        elif score >= 0.4:
            level = CompatibilityLevel.LOW
            compatible = True
        else:
            level = CompatibilityLevel.INCOMPATIBLE
            compatible = False
        
        # Generate suggestions and warnings
        suggestions = self._generate_suggestions(template_type, style_profile, score, details)
        warnings = self._generate_warnings(template_type, style_profile, score, details)
        
        return CompatibilityResult(
            compatible=compatible,
            level=level,
            confidence=min(score + 0.1, 1.0),
            reason=self._generate_reason(score, details),
            suggestions=suggestions,
            warnings=warnings
        )

    def _calculate_compatibility_score(self, template_chars: Dict, style_chars: Dict) -> Tuple[float, Dict]:
        """Calculate compatibility score based on characteristics alignment"""
        
        details = {}
        total_score = 0.0
        weight_sum = 0.0
        
        # Content type alignment (weight: 0.3)
        content_alignment = self._check_content_alignment(
            template_chars['content_type'], 
            style_chars['content_focus']
        )
        total_score += content_alignment * 0.3
        weight_sum += 0.3
        details['content_alignment'] = content_alignment
        
        # Audience level alignment (weight: 0.25)
        audience_alignment = self._check_audience_alignment(
            template_chars['audience'],
            style_chars['audience_level']
        )
        total_score += audience_alignment * 0.25
        weight_sum += 0.25
        details['audience_alignment'] = audience_alignment
        
        # Complexity alignment (weight: 0.2)
        complexity_alignment = self._check_complexity_alignment(
            template_chars['complexity'],
            style_chars['complexity_match']
        )
        total_score += complexity_alignment * 0.2
        weight_sum += 0.2
        details['complexity_alignment'] = complexity_alignment
        
        # Tone compatibility (weight: 0.15)
        tone_compatibility = self._check_tone_compatibility(
            template_chars['tone_requirements'],
            style_chars['tone']
        )
        total_score += tone_compatibility * 0.15
        weight_sum += 0.15
        details['tone_compatibility'] = tone_compatibility
        
        # Format requirements alignment (weight: 0.1)
        format_alignment = self._check_format_alignment(
            template_chars['format_needs'],
            style_chars['format_requirements']
        )
        total_score += format_alignment * 0.1
        weight_sum += 0.1
        details['format_alignment'] = format_alignment
        
        final_score = total_score / weight_sum if weight_sum > 0 else 0.0
        return final_score, details

    def _check_content_alignment(self, template_content: str, style_focus: str) -> float:
        """Check alignment between template content type and style focus"""
        alignments = {
            ('analytical', 'data_driven_analysis'): 1.0,
            ('analytical', 'strategic_analysis'): 0.8,
            ('analytical', 'technical_analysis'): 0.7,
            ('executive', 'strategic_analysis'): 1.0,
            ('executive', 'high_level_overview'): 1.0,
            ('professional', 'strategic_analysis'): 0.8,
            ('informational', 'engagement_focused'): 0.7,
            ('analytical', 'engagement_focused'): 0.2,
            ('executive', 'engagement_focused'): 0.1,
        }
        return alignments.get((template_content, style_focus), 0.5)

    def _check_audience_alignment(self, template_audience: str, style_audience: str) -> float:
        """Check alignment between target audiences"""
        alignments = {
            ('business_analysts', 'professional'): 1.0,
            ('executives', 'executive'): 1.0,
            ('analysts', 'professional'): 0.9,
            ('analysts', 'technical_experts'): 0.8,
            ('business_stakeholders', 'executive'): 0.8,
            ('business_stakeholders', 'professional'): 0.9,
            ('general', 'general'): 1.0,
            ('executives', 'general'): 0.3,
            ('business_analysts', 'general'): 0.4,
        }
        return alignments.get((template_audience, style_audience), 0.5)

    def _check_complexity_alignment(self, template_complexity: str, style_complexity: str) -> float:
        """Check alignment between complexity levels"""
        complexity_scores = {
            'beginner': 1, 'beginner_to_intermediate': 2, 'intermediate': 3,
            'intermediate_to_expert': 4, 'expert': 5
        }
        
        template_score = complexity_scores.get(template_complexity, 3)
        style_score = complexity_scores.get(style_complexity, 3)
        
        diff = abs(template_score - style_score)
        return max(0.0, 1.0 - (diff * 0.2))

    def _check_tone_compatibility(self, template_tones: List[str], style_tone: str) -> float:
        """Check compatibility between tone requirements"""
        tone_matches = {
            'professional': ['business_analytical', 'authoritative_professional', 'executive_professional', 'technical_professional'],
            'analytical': ['business_analytical', 'technical_professional'],
            'authoritative': ['authoritative_professional', 'executive_professional'],
            'objective': ['business_analytical', 'technical_professional'],
            'engaging': ['casual_engaging'],
            'technical': ['technical_professional'],
            'formal': ['authoritative_professional', 'executive_professional']
        }
        
        max_compatibility = 0.0
        for tone in template_tones:
            compatible_styles = tone_matches.get(tone, [])
            if style_tone in compatible_styles:
                max_compatibility = max(max_compatibility, 1.0)
            elif any(partial in style_tone for partial in ['professional', 'analytical']):
                max_compatibility = max(max_compatibility, 0.6)
        
        return max_compatibility

    def _check_format_alignment(self, template_formats: List[str], style_formats: List[str]) -> float:
        """Check alignment between format requirements"""
        if not template_formats or not style_formats:
            return 0.5
        
        matches = len(set(template_formats) & set(style_formats))
        total = len(set(template_formats) | set(style_formats))
        return matches / total if total > 0 else 0.5

    def _suggest_compatible_style(self, template_type: str) -> str:
        """Suggest a compatible style for given template type"""
        suggestions = {
            'market_analysis': 'market_flash',
            'strategic_brief': 'strategic_planning',
            'data_driven_report': 'technical_dive',
            'blog_article': 'content_marketing',
            'business_document': 'executive_summary'
        }
        return suggestions.get(template_type, 'professional_standard')

    def _generate_reason(self, score: float, details: Dict) -> str:
        """Generate human-readable reason for compatibility score"""
        if score >= 0.8:
            return "Excellent alignment between template structure and style requirements"
        elif score >= 0.6:
            return "Good compatibility with minor style adjustments needed"
        elif score >= 0.4:
            return "Moderate compatibility - may require style customization"
        else:
            return "Poor compatibility - significant content structure mismatch"

    def _generate_suggestions(self, template_type: str, style_profile: str, score: float, details: Dict) -> List[str]:
        """Generate improvement suggestions based on compatibility analysis"""
        suggestions = []
        
        if score < 0.6:
            suggestions.append(f"Consider using {self._suggest_compatible_style(template_type)} style profile instead")
        
        if details.get('audience_alignment', 1.0) < 0.5:
            suggestions.append("Adjust audience targeting to match style profile expectations")
        
        if details.get('tone_compatibility', 1.0) < 0.5:
            suggestions.append("Review tone requirements for better style alignment")
        
        if details.get('complexity_alignment', 1.0) < 0.5:
            suggestions.append("Consider adjusting content complexity level")
        
        if score >= 0.6:
            suggestions.append("Monitor generated content for style consistency")
        
        return suggestions

    def _generate_warnings(self, template_type: str, style_profile: str, score: float, details: Dict) -> List[str]:
        """Generate warnings for potential issues"""
        warnings = []
        
        if score < 0.4:
            warnings.append("High risk of content structure confusion")
            warnings.append("Generated content may mix incompatible formats")
        
        if score < 0.6 and details.get('content_alignment', 1.0) < 0.4:
            warnings.append("Content type mismatch detected")
        
        if details.get('audience_alignment', 1.0) < 0.3:
            warnings.append("Audience mismatch may result in inappropriate content level")
        
        if details.get('tone_compatibility', 1.0) < 0.3:
            warnings.append("Tone incompatibility may create inconsistent messaging")
        
        return warnings

    def get_recommended_combinations(self) -> Dict[str, List[str]]:
        """Get recommended template-style combinations"""
        return {
            'market_analysis_template': ['market_flash', 'market_research_report', 'business_case_analysis'],
            'strategic_brief_template': ['strategic_planning', 'executive_summary', 'board_presentation'],
            'data_driven_report_template': ['technical_dive', 'performance_analysis', 'market_flash'],
            'business_proposal': ['executive_summary', 'strategic_planning', 'roi_analysis'],
            'blog_article_generator': ['content_marketing', 'thought_leadership', 'popular_sci']
        }

    def batch_validate_templates(self, template_style_pairs: List[Tuple[str, str]]) -> Dict[Tuple[str, str], CompatibilityResult]:
        """Validate multiple template-style combinations at once"""
        results = {}
        for template_type, style_profile in template_style_pairs:
            results[(template_type, style_profile)] = self.validate_compatibility(template_type, style_profile)
        return results

    def generate_compatibility_report(self, template_types: List[str], style_profiles: List[str]) -> Dict[str, Any]:
        """Generate comprehensive compatibility report"""
        
        report = {
            'total_combinations': len(template_types) * len(style_profiles),
            'highly_compatible': [],
            'moderately_compatible': [],
            'incompatible': [],
            'detailed_results': {},
            'recommendations': {}
        }
        
        for template_type in template_types:
            for style_profile in style_profiles:
                result = self.validate_compatibility(template_type, style_profile)
                
                combination = (template_type, style_profile)
                report['detailed_results'][combination] = result
                
                if result.level == CompatibilityLevel.HIGH:
                    report['highly_compatible'].append(combination)
                elif result.level == CompatibilityLevel.MODERATE:
                    report['moderately_compatible'].append(combination)
                elif result.level == CompatibilityLevel.INCOMPATIBLE:
                    report['incompatible'].append(combination)
        
        # Generate recommendations
        for template_type in template_types:
            best_styles = []
            for style_profile in style_profiles:
                result = report['detailed_results'][(template_type, style_profile)]
                if result.level in [CompatibilityLevel.HIGH, CompatibilityLevel.MODERATE]:
                    best_styles.append((style_profile, result.confidence))
            
            # Sort by confidence and take top 3
            best_styles.sort(key=lambda x: x[1], reverse=True)
            report['recommendations'][template_type] = [style for style, _ in best_styles[:3]]
        
        return report


# Global validator instance
validator = TemplateStyleValidator()

def validate_template_style_match(template_type: str, style_profile: str) -> CompatibilityResult:
    """Global function to validate template-style compatibility"""
    return validator.validate_compatibility(template_type, style_profile)

def get_compatibility_recommendations(template_type: str) -> List[str]:
    """Get recommended style profiles for a template type"""
    recommended = validator.get_recommended_combinations()
    return recommended.get(template_type, [])

def check_combination_safety(template_name: str, style_profile: str) -> bool:
    """Quick safety check for template-style combination"""
    # Extract template type from name if needed
    from .template_loader import get_template
    
    template = get_template(template_name)
    if not template:
        return False
    
    template_type = template.get('template_type', template_name)
    result = validator.validate_compatibility(template_type, style_profile)
    
    return result.compatible and result.level != CompatibilityLevel.INCOMPATIBLE