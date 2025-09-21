import streamlit as st
from typing import Dict, List, Optional
from datetime import datetime
import json
import logging

class SpecEngine:
    """Engine for generating and managing specification documents"""
    
    def __init__(self, ai_service):
        self.ai_service = ai_service
        self.logger = logging.getLogger(__name__)
        
        # OpenFlux system prompt for consistent behavior
        self.openflux_system_prompt = """You are OpenFlux, an AI assistant and IDE built to assist developers.

When users ask about OpenFlux, respond with information about yourself in first person.

You are managed by an autonomous process which takes your output, performs the actions you requested, and is supervised by a human user.

You talk like a human, not like a bot. You reflect the user's input style in your responses.

# Response style
- We are knowledgeable. We are not instructive. In order to inspire confidence in the programmers we partner with, we've got to bring our expertise and show we know our Java from our JavaScript. But we show up on their level and speak their language, though never in a way that's condescending or off-putting.
- Speak like a dev — when necessary. Look to be more relatable and digestible in moments where we don't need to rely on technical language or specific vocabulary to get across a point.
- Be decisive, precise, and clear. Lose the fluff when you can.
- We are supportive, not authoritative. Coding is hard work, we get it. That's why our tone is also grounded in compassion and understanding so every programmer feels welcome and comfortable using OpenFlux.
- Use positive, optimistic language that keeps OpenFlux feeling like a solutions-oriented space.
- Stay warm and friendly as much as possible. We're not a cold tech company; we're a companionable partner, who always welcomes you and sometimes cracks a joke or two.
- Be concise and direct in your responses
- Don't repeat yourself, saying the same message over and over, or similar messages is not always helpful, and can look you're confused.
- Prioritize actionable information over general explanations
- Use bullet points and formatting to improve readability when appropriate
- Include relevant code snippets, CLI commands, or configuration examples
- Explain your reasoning when making recommendations"""
    
    def create_requirements(self, feature_description: str, codebase_context: Dict = None, coding_template: str = None) -> str:
        """Generate EARS-format requirements from feature description"""
        
        context_info = ""
        if codebase_context:
            context_info = f"""
            
Codebase Context:
- Languages: {', '.join(codebase_context.get('languages', []))}
- File Count: {codebase_context.get('file_count', 0)}
- Architecture Insights: {codebase_context.get('analysis', 'No analysis available')[:500]}...
"""
        
        template_info = ""
        if coding_template and coding_template.strip():
            template_info = f"""

Coding Template & Standards:
{coding_template[:1000]}{'...' if len(coding_template) > 1000 else ''}

Please ensure the requirements align with the coding patterns, architectural preferences, and development standards specified in the template above."""
        
        requirements_prompt = f"""Generate detailed requirements in EARS format (Easy Approach to Requirements Syntax) for the following feature:

Feature Description: {feature_description}
{context_info}
{template_info}

Please format the requirements document with:

# Requirements Document

## Introduction
[Brief summary of the feature and its purpose]

## Requirements

### Requirement 1
**User Story:** As a [role], I want [feature], so that [benefit]

#### Acceptance Criteria
1. WHEN [event] THEN [system] SHALL [response]
2. IF [precondition] THEN [system] SHALL [response]
3. WHEN [event] AND [condition] THEN [system] SHALL [response]

### Requirement 2
[Continue with additional requirements...]

Focus on:
- User experience and workflows
- Technical constraints and edge cases
- Security and performance considerations
- Integration requirements
- Error handling scenarios

Make the requirements specific, testable, and implementable."""

        try:
            return self.ai_service.generate_requirements(feature_description, None, coding_template)
        except Exception as e:
            self.logger.error(f"Requirements generation failed: {e}")
            raise e
    
    def generate_design(self, requirements: str, codebase_context: Dict = None, coding_template: str = None) -> str:
        """Generate design document from requirements"""
        
        context_info = ""
        if codebase_context:
            context_info = f"""
            
Existing Codebase Context:
- Languages: {', '.join(codebase_context.get('languages', []))}
- File Count: {codebase_context.get('file_count', 0)}
- Current Architecture: {codebase_context.get('analysis', 'No analysis available')[:500]}...
"""
        
        template_info = ""
        if coding_template and coding_template.strip():
            template_info = f"""

Coding Template & Standards:
{coding_template[:1000]}{'...' if len(coding_template) > 1000 else ''}

Please ensure the design follows the architectural patterns, component structures, naming conventions, and technical approaches specified in the template above."""
        
        design_prompt = f"""Create a comprehensive design document based on these requirements:

{requirements}
{context_info}
{template_info}

Please format the design document with these sections:

# Design Document

## Overview
[High-level summary of the solution approach]

## Architecture
[System architecture with Mermaid diagrams where appropriate]

```mermaid
graph TB
    [Include relevant architecture diagrams]
```

## Components and Interfaces
[Detailed component breakdown with interfaces]

## Data Models
[Data structures, schemas, and relationships]

## Error Handling
[Error scenarios and handling strategies]

## Testing Strategy
[Approach to testing and validation]

## Security Considerations
[Security requirements and implementation approach]

## Performance Considerations
[Performance requirements and optimization strategies]

Focus on:
- Scalable and maintainable architecture
- Clear separation of concerns
- Integration with existing systems
- Best practices and patterns
- Technical implementation details"""

        try:
            return self.ai_service.create_design(requirements, codebase_context, coding_template)
        except Exception as e:
            self.logger.error(f"Design generation failed: {e}")
            raise e
    
    def create_task_list(self, design: str, requirements: str = None, coding_template: str = None) -> str:
        """Generate implementation tasks from design document in Kiro markdown format"""
        
        requirements_context = ""
        if requirements:
            requirements_context = f"\n\nRequirements Context:\n{requirements[:1000]}..."
        
        template_context = ""
        if coding_template and coding_template.strip():
            template_context = f"""

Coding Template & Standards:
{coding_template[:1000]}{'...' if len(coding_template) > 1000 else ''}

CRITICAL: Ensure all implementation tasks follow the specific development practices, testing patterns, code organization, and technical standards specified in the template above. Use the exact technologies, frameworks, and approaches mentioned in the template."""
        else:
            template_context = "\n\nNote: No coding template provided. Generate implementation tasks using modern best practices and choose appropriate technologies based on the design document and requirements."
        
        tasks_prompt = f"""You are an expert technical lead creating a comprehensive implementation plan. Generate detailed, actionable coding tasks that match the quality and specificity of professional development plans.

DESIGN DOCUMENT:
{design}

REQUIREMENTS CONTEXT:
{requirements_context}

CODING TEMPLATE & STANDARDS:
{template_context}

CRITICAL INSTRUCTIONS:
1. Create 12-15 main implementation tasks covering all aspects of the system
2. Include sub-tasks where appropriate (2-4 sub-tasks for complex main tasks)
3. Each task should specify exact files, functions, and code to be written
4. Follow the coding template's technology stack and patterns precisely
5. Include comprehensive testing tasks (unit, integration, E2E)
6. Address security, error handling, and performance optimization
7. Build tasks incrementally with proper dependencies

TASK FORMAT:

# Implementation Plan

- [ ] 1. Set up project structure and core configuration
  - Create [specific config files] with [specific technology] configuration
  - Set up [specific dependencies] with required versions
  - Create directory structure for [specific services/modules from design]
  - Configure [specific tools/frameworks] for [specific purposes]
  - _Requirements: [Reference specific requirement numbers]_

- [ ] 2. Implement [Core Service Name] with [specific functionality]
  - [ ] 2.1 Create [specific component] with [specific methods/functions]
    - Implement [specific function names] for [specific business logic]
    - Add [specific validation/error handling] for [specific scenarios]
    - Write [specific test files] covering [specific test cases]
    - _Requirements: X.X, Y.Y_
  
  - [ ] 2.2 Implement [specific feature] with [specific approach]
    - Create [specific files/classes] for [specific functionality]
    - Add [specific database operations] using [specific patterns]
    - _Requirements: X.X_

- [ ] 3. Implement [Another Major Component]
  - Create [specific implementation details]
  - Add [specific technical features]
  - _Requirements: X.X_

[Continue with 10-12 more detailed tasks...]

QUALITY STANDARDS FOR EACH TASK:
- Specify exact file names and directory structures
- Include specific function/method names to implement
- Reference specific technologies and frameworks from template
- Include specific test files and test scenarios
- Address error handling and edge cases
- Include performance and security considerations
- Reference specific requirement numbers for traceability
- Build incrementally (each task depends on previous tasks)

TASK CATEGORIES TO INCLUDE:
1. Project setup and configuration (1-2 tasks)
2. Core services implementation (3-4 tasks with sub-tasks)
3. Data layer and models (1-2 tasks)
4. API/interface implementation (2-3 tasks)
5. Business logic and calculations (2-3 tasks)
6. Authentication and security (1-2 tasks)
7. Testing implementation (2-3 tasks)
8. Integration and workflow (1-2 tasks)
9. Error handling and validation (1 task)
10. Performance optimization (1 task)

TECHNICAL SPECIFICITY:
- Use exact technology names from the coding template
- Include specific file extensions and naming conventions
- Reference specific frameworks, libraries, and tools
- Include specific database operations and query patterns
- Address specific security implementations
- Include specific testing frameworks and approaches

Each task should be detailed enough that a developer can start coding immediately without additional clarification."""

        try:
            response = self.ai_service.generate_text(tasks_prompt, self.openflux_system_prompt)
            return response
                
        except Exception as e:
            self.logger.error(f"Task generation failed: {e}")
            raise e
    
    def incorporate_template(self, prompt: str, template: str) -> str:
        """Incorporate coding template into AI prompt"""
        if not template or not template.strip():
            return prompt
        
        try:
            # Add template context to the prompt
            template_section = f"""

CODING TEMPLATE & STANDARDS:
{template[:1500]}{'...' if len(template) > 1500 else ''}

Please ensure all generated content follows the patterns, conventions, and standards specified in the template above.
"""
            
            # Insert template section before the main prompt instructions
            if "Please format" in prompt:
                parts = prompt.split("Please format", 1)
                return parts[0] + template_section + "\nPlease format" + parts[1]
            else:
                return prompt + template_section
                
        except Exception as e:
            self.logger.warning(f"Failed to incorporate template into prompt: {e}")
            return prompt
    
    def update_document(self, doc_type: str, content: str, version: int = 1) -> bool:
        """Update specification document in session state"""
        try:
            timestamp = datetime.now().isoformat()
            
            doc_data = {
                "content": content,
                "version": version,
                "updated_at": timestamp,
                "doc_type": doc_type
            }
            
            # Store in session state
            if doc_type == "requirements":
                st.session_state.requirements_doc = content
                st.session_state.requirements_data = doc_data
            elif doc_type == "design":
                st.session_state.design_doc = content
                st.session_state.design_data = doc_data
            elif doc_type == "tasks":
                st.session_state.task_list = content
                st.session_state.tasks_data = doc_data
            
            return True
            
        except Exception as e:
            self.logger.error(f"Document update failed: {e}")
            return False
    
    def get_document_status(self, doc_type: str) -> Dict:
        """Get status information for a document type"""
        status_map = {
            "requirements": {
                "exists": bool(st.session_state.get("requirements_doc")),
                "content": st.session_state.get("requirements_doc", ""),
                "data": st.session_state.get("requirements_data", {})
            },
            "design": {
                "exists": bool(st.session_state.get("design_doc")),
                "content": st.session_state.get("design_doc", ""),
                "data": st.session_state.get("design_data", {})
            },
            "tasks": {
                "exists": bool(st.session_state.get("task_list")),
                "content": st.session_state.get("task_list", ""),
                "data": st.session_state.get("tasks_data", {})
            }
        }
        
        return status_map.get(doc_type, {"exists": False, "content": "", "data": {}})
    
    def validate_requirements(self, requirements: str) -> Dict:
        """Validate requirements document format and completeness"""
        validation_results = {
            "valid": True,
            "issues": [],
            "suggestions": []
        }
        
        # Check for basic structure
        if "# Requirements Document" not in requirements:
            validation_results["issues"].append("Missing main title '# Requirements Document'")
            validation_results["valid"] = False
        
        if "## Introduction" not in requirements:
            validation_results["issues"].append("Missing Introduction section")
            validation_results["valid"] = False
        
        if "## Requirements" not in requirements:
            validation_results["issues"].append("Missing Requirements section")
            validation_results["valid"] = False
        
        # Check for user stories
        if "**User Story:**" not in requirements:
            validation_results["issues"].append("No user stories found")
            validation_results["valid"] = False
        
        # Check for EARS format
        ears_keywords = ["WHEN", "THEN", "SHALL", "IF"]
        if not any(keyword in requirements for keyword in ears_keywords):
            validation_results["issues"].append("No EARS format criteria found (WHEN/THEN/SHALL/IF)")
            validation_results["valid"] = False
        
        # Suggestions for improvement
        if requirements.count("### Requirement") < 3:
            validation_results["suggestions"].append("Consider adding more detailed requirements (found less than 3)")
        
        if "edge case" not in requirements.lower():
            validation_results["suggestions"].append("Consider adding edge case handling requirements")
        
        if "error" not in requirements.lower():
            validation_results["suggestions"].append("Consider adding error handling requirements")
        
        return validation_results
    
    def export_spec_documents(self) -> Dict[str, str]:
        """Export all specification documents"""
        documents = {}
        
        if st.session_state.get("requirements_doc"):
            documents["requirements.md"] = st.session_state.requirements_doc
        
        if st.session_state.get("design_doc"):
            documents["design.md"] = st.session_state.design_doc
        
        if st.session_state.get("task_list"):
            # Tasks are now already in markdown format
            tasks = st.session_state.task_list
            if isinstance(tasks, str) and tasks.strip():
                documents["tasks.md"] = tasks
            elif isinstance(tasks, list) and tasks:
                # Fallback for old JSON format if it still exists
                tasks_md = "# Implementation Tasks\n\n"
                for i, task in enumerate(tasks, 1):
                    if isinstance(task, dict):
                        tasks_md += f"## {i}. {task.get('title', 'Untitled Task')}\n\n"
                        tasks_md += f"**Description:** {task.get('description', 'No description')}\n\n"
                        tasks_md += f"**Priority:** {task.get('priority', 'medium')}\n\n"
                        tasks_md += f"**Estimated Hours:** {task.get('estimated_hours', 'TBD')}\n\n"
                        
                        if task.get('requirements_refs'):
                            tasks_md += f"**Requirements:** {', '.join(task['requirements_refs'])}\n\n"
                        
                        if task.get('acceptance_criteria'):
                            tasks_md += "**Acceptance Criteria:**\n"
                            for criteria in task['acceptance_criteria']:
                                tasks_md += f"- {criteria}\n"
                            tasks_md += "\n"
                        
                        tasks_md += "---\n\n"
                
                documents["tasks.md"] = tasks_md
        
        return documents