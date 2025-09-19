import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

@dataclass
class CodingTemplate:
    """Data model for coding templates"""
    name: str
    content: str
    created_at: datetime
    updated_at: datetime
    
    def validate(self) -> Dict[str, Any]:
        """Validate template content and return validation results"""
        issues = []
        suggestions = []
        character_count = len(self.content.strip())
        
        # Check minimum length
        if character_count < 50:
            issues.append(f"Template too short ({character_count} chars). Minimum 50 characters required.")
        
        # Check for meaningful content
        if not self.content.strip():
            issues.append("Template cannot be empty.")
        elif len(self.content.split()) < 10:
            issues.append("Template should contain more descriptive content (at least 10 words).")
        
        # Check for coding-related keywords
        coding_keywords = ['architecture', 'framework', 'library', 'pattern', 'service', 'api', 
                          'database', 'authentication', 'testing', 'security', 'performance',
                          'deployment', 'monitoring', 'logging', 'validation', 'error handling']
        
        technology_keywords = [
            # Programming Languages
            'python', 'java', 'javascript', 'typescript', 'c#', 'go', 'rust', 'php', 'ruby', 'swift', 'kotlin',
            # Frameworks & Libraries  
            'react', 'angular', 'vue', 'spring', 'django', 'flask', 'express', 'laravel', 'rails', '.net',
            # Databases
            'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch', 'dynamodb', 'oracle', 'sqlite',
            # Cloud & Infrastructure
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'serverless', 'lambda', 'microservices',
            # Architecture Patterns
            'rest', 'graphql', 'grpc', 'soap', 'mvc', 'mvvm', 'clean architecture', 'hexagonal',
            # Development Tools
            'git', 'jenkins', 'github', 'gitlab', 'ci/cd', 'webpack', 'babel', 'npm', 'yarn', 'maven', 'gradle'
        ]
        
        has_coding_keywords = any(keyword in self.content.lower() for keyword in coding_keywords)
        has_tech_keywords = any(keyword in self.content.lower() for keyword in technology_keywords)
        
        if not has_coding_keywords:
            suggestions.append("Consider adding specific architectural patterns, coding practices, or development approaches.")
        
        if not has_tech_keywords:
            suggestions.append("Consider specifying technology stack, frameworks, or platforms to be used.")
        
        if character_count < 200:
            suggestions.append("Consider adding more detailed coding standards and architectural guidelines for better AI guidance.")
        
        # Calculate quality score
        score = 0
        if character_count >= 50:
            score += 20
        if character_count >= 200:
            score += 25
        if character_count >= 500:
            score += 15
        if len(self.content.split()) >= 20:
            score += 15
        if len(self.content.split()) >= 50:
            score += 10
        if has_coding_keywords:
            score += 10
        if has_tech_keywords:
            score += 5
        
        return {
            'is_valid': len(issues) == 0,
            'character_count': character_count,
            'word_count': len(self.content.split()),
            'issues': issues,
            'suggestions': suggestions,
            'score': min(score, 100)
        }
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'name': self.name,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'CodingTemplate':
        """Create instance from dictionary"""
        return cls(
            name=data['name'],
            content=data['content'],
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at'])
        )

@dataclass
class ValidationResult:
    """Template validation result"""
    is_valid: bool
    character_count: int
    word_count: int
    issues: List[str]
    suggestions: List[str]
    score: int  # 0-100 quality score

class TemplateService:
    """Service for managing coding templates"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.templates_dir = Path(".openflux/templates")
        self._ensure_templates_directory()
    
    def _ensure_templates_directory(self):
        """Ensure templates directory exists"""
        try:
            self.templates_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            self.logger.error(f"Failed to create templates directory: {e}")
    
    def save_template(self, name: str, content: str) -> bool:
        """Save a coding template"""
        try:
            # Validate name
            if not name or not name.strip():
                raise ValueError("Template name cannot be empty")
            
            # Clean name for filename
            safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip()
            if not safe_name:
                raise ValueError("Template name must contain valid characters")
            
            # Create template
            now = datetime.now()
            template = CodingTemplate(
                name=name.strip(),
                content=content.strip(),
                created_at=now,
                updated_at=now
            )
            
            # Validate template
            validation = template.validate()
            if not validation['is_valid']:
                raise ValueError(f"Template validation failed: {', '.join(validation['issues'])}")
            
            # Save to file
            filename = f"{safe_name.replace(' ', '_')}.json"
            filepath = self.templates_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(template.to_dict(), f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Template '{name}' saved successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save template '{name}': {e}")
            return False
    
    def load_template(self, name: str) -> Optional[str]:
        """Load template content by name"""
        try:
            templates = self.list_templates()
            for template_info in templates:
                if template_info['name'] == name:
                    return template_info['content']
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to load template '{name}': {e}")
            return None
    
    def list_templates(self) -> List[Dict]:
        """List all available templates"""
        templates = []
        try:
            if not self.templates_dir.exists():
                return templates
            
            for filepath in self.templates_dir.glob("*.json"):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    template = CodingTemplate.from_dict(data)
                    templates.append({
                        'name': template.name,
                        'content': template.content,
                        'created_at': template.created_at,
                        'updated_at': template.updated_at,
                        'filename': filepath.name
                    })
                    
                except Exception as e:
                    self.logger.warning(f"Failed to load template from {filepath}: {e}")
                    continue
            
            # Sort by updated_at descending
            templates.sort(key=lambda x: x['updated_at'], reverse=True)
            return templates
            
        except Exception as e:
            self.logger.error(f"Failed to list templates: {e}")
            return []
    
    def delete_template(self, name: str) -> bool:
        """Delete a template by name"""
        try:
            templates = self.list_templates()
            for template_info in templates:
                if template_info['name'] == name:
                    filepath = self.templates_dir / template_info['filename']
                    filepath.unlink()
                    self.logger.info(f"Template '{name}' deleted successfully")
                    return True
            
            self.logger.warning(f"Template '{name}' not found for deletion")
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to delete template '{name}': {e}")
            return False
    
    def validate_template(self, content: str) -> ValidationResult:
        """Validate template content"""
        try:
            # Create temporary template for validation
            temp_template = CodingTemplate(
                name="temp",
                content=content,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            validation_dict = temp_template.validate()
            return ValidationResult(
                is_valid=validation_dict['is_valid'],
                character_count=validation_dict['character_count'],
                word_count=validation_dict['word_count'],
                issues=validation_dict['issues'],
                suggestions=validation_dict['suggestions'],
                score=validation_dict['score']
            )
            
        except Exception as e:
            self.logger.error(f"Template validation failed: {e}")
            return ValidationResult(
                is_valid=False,
                character_count=0,
                word_count=0,
                issues=[f"Validation error: {str(e)}"],
                suggestions=[],
                score=0
            )
    
    def get_template_preview(self, content: str) -> str:
        """Generate a preview of how the template will be used in AI prompts"""
        if not content.strip():
            return "No template content to preview."
        
        preview = f"""
Template Integration Preview:

The following coding template will be included in AI prompts:

--- CODING TEMPLATE ---
{content[:500]}{'...' if len(content) > 500 else ''}
--- END TEMPLATE ---

This template will influence:
• Requirements generation - ensuring business requirements align with your technical approach
• Design document creation - incorporating your architectural patterns and technology choices  
• Implementation tasks - following your development practices and coding standards

The AI will reference this template when making decisions about:
- Architecture patterns and technology stack
- System design and component structure
- Development approaches and methodologies
- Testing strategies and quality practices
- Security and performance considerations
"""
        return preview.strip()