#!/usr/bin/env python3
"""
Template Engine for Claude Module System
Supports template inheritance and variable substitution
"""

import os
import re
import yaml
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class TemplateEngine:
    def __init__(self, template_dir: str = ".claude/templates"):
        self.template_dir = template_dir
        self.base_templates = self._load_base_templates()
        
    def _load_base_templates(self) -> Dict[str, str]:
        """Load all base templates"""
        templates = {}
        base_dir = os.path.join(self.template_dir, "base")
        
        if os.path.exists(base_dir):
            for file in os.listdir(base_dir):
                if file.endswith('.md'):
                    template_name = file.replace('.md', '')
                    with open(os.path.join(base_dir, file), 'r') as f:
                        templates[template_name] = f.read()
        
        return templates
    
    def create_from_template(self, template_name: str, variables: Dict[str, str], output_path: str):
        """Create a new module from a template"""
        # Get base template
        if template_name not in self.base_templates:
            raise ValueError(f"Template '{template_name}' not found")
        
        template_content = self.base_templates[template_name]
        
        # Add default variables
        variables.setdefault('DATE', datetime.now().strftime('%Y-%m-%d'))
        variables.setdefault('AUTHOR', os.environ.get('USER', 'Unknown'))
        
        # Substitute variables
        content = self._substitute_variables(template_content, variables)
        
        # Create output directory if needed
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Write file
        with open(output_path, 'w') as f:
            f.write(content)
        
        print(f"Created module: {output_path}")
        
        # Validate the created module
        self._validate_module(output_path)
    
    def _substitute_variables(self, template: str, variables: Dict[str, str]) -> str:
        """Substitute variables in template"""
        content = template
        
        # Find all variables in template
        variable_pattern = r'\$\{([A-Z_]+)\}'
        found_variables = set(re.findall(variable_pattern, content))
        
        # Check for missing required variables
        missing = found_variables - set(variables.keys())
        if missing:
            print(f"Warning: Missing variables will need to be filled in: {missing}")
        
        # Substitute provided variables
        for var, value in variables.items():
            pattern = f'${{{var}}}'
            content = content.replace(pattern, str(value))
        
        return content
    
    def _validate_module(self, filepath: str):
        """Basic validation of created module"""
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Check for remaining template variables
        remaining_vars = re.findall(r'\$\{([A-Z_]+)\}', content)
        if remaining_vars:
            print(f"⚠️  Template variables still need to be filled in: {remaining_vars}")
        
        # Check YAML frontmatter
        if content.startswith('---'):
            yaml_end = content.find('---', 3)
            if yaml_end != -1:
                try:
                    frontmatter = yaml.safe_load(content[3:yaml_end])
                    print("✅ Valid YAML frontmatter")
                except yaml.YAMLError as e:
                    print(f"❌ Invalid YAML frontmatter: {e}")
            else:
                print("❌ Incomplete YAML frontmatter")
        else:
            print("❌ Missing YAML frontmatter")
    
    def list_templates(self) -> List[str]:
        """List available templates"""
        return list(self.base_templates.keys())
    
    def show_template_variables(self, template_name: str) -> List[str]:
        """Show all variables in a template"""
        if template_name not in self.base_templates:
            raise ValueError(f"Template '{template_name}' not found")
        
        template_content = self.base_templates[template_name]
        variable_pattern = r'\$\{([A-Z_]+)\}'
        variables = sorted(set(re.findall(variable_pattern, template_content)))
        
        return variables
    
    def create_interactive(self, template_name: str, output_path: str):
        """Interactive mode - prompt for each variable"""
        variables = self.show_template_variables(template_name)
        values = {}
        
        print(f"\nCreating module from template: {template_name}")
        print("Please provide values for the following variables:\n")
        
        for var in variables:
            # Skip auto-filled variables
            if var in ['DATE', 'AUTHOR']:
                continue
            
            # Provide helpful prompts
            prompt = self._get_variable_prompt(var)
            value = input(f"{var} {prompt}: ").strip()
            
            if value:
                values[var] = value
        
        # Create module
        self.create_from_template(template_name, values, output_path)
    
    def _get_variable_prompt(self, var: str) -> str:
        """Get helpful prompt for variable"""
        prompts = {
            'MODULE_NAME': '(PascalCase, e.g., DataProcessor)',
            'COMMAND_NAME': '(lowercase, e.g., analyze)',
            'PROCESS_NAME': '(descriptive, e.g., CodeReview)',
            'WORKFLOW_NAME': '(descriptive, e.g., FeatureDevelopment)',
            'SCOPE': '(persistent|context|temporary)',
            'PRIORITY': '(low|medium|high)',
            'PURPOSE_DESCRIPTION': '(one sentence describing the purpose)',
            'TRIGGER_1': '(phrase that activates this module)',
            'USAGE_PATTERN': '(e.g., <subcommand> [options])',
        }
        return prompts.get(var, '')
    
    def extend_template(self, base_template: str, extensions: Dict[str, str], output_name: str):
        """Create an extended template from a base template"""
        if base_template not in self.base_templates:
            raise ValueError(f"Base template '{base_template}' not found")
        
        # Start with base template
        content = self.base_templates[base_template]
        
        # Apply extensions
        for section, additional_content in extensions.items():
            # Find section in template
            section_pattern = f'## {section}\n'
            if section_pattern in content:
                # Insert after section header
                insert_pos = content.find(section_pattern) + len(section_pattern)
                content = content[:insert_pos] + additional_content + '\n' + content[insert_pos:]
            else:
                # Append as new section
                content += f"\n## {section}\n{additional_content}\n"
        
        # Save extended template
        output_path = os.path.join(self.template_dir, f"{output_name}.md")
        with open(output_path, 'w') as f:
            f.write(content)
        
        print(f"Created extended template: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Claude Template Engine')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create module from template')
    create_parser.add_argument('template', help='Template name')
    create_parser.add_argument('output', help='Output file path')
    create_parser.add_argument('--var', action='append', help='Variable in KEY=VALUE format')
    create_parser.add_argument('--interactive', '-i', action='store_true', help='Interactive mode')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List available templates')
    
    # Show command
    show_parser = subparsers.add_parser('show', help='Show template variables')
    show_parser.add_argument('template', help='Template name')
    
    # Extend command
    extend_parser = subparsers.add_parser('extend', help='Create extended template')
    extend_parser.add_argument('base', help='Base template name')
    extend_parser.add_argument('name', help='New template name')
    extend_parser.add_argument('--section', action='append', help='Section to add in SECTION=CONTENT format')
    
    args = parser.parse_args()
    
    engine = TemplateEngine()
    
    if args.command == 'create':
        if args.interactive:
            engine.create_interactive(args.template, args.output)
        else:
            # Parse variables
            variables = {}
            if args.var:
                for var in args.var:
                    if '=' in var:
                        key, value = var.split('=', 1)
                        variables[key] = value
            
            engine.create_from_template(args.template, variables, args.output)
    
    elif args.command == 'list':
        templates = engine.list_templates()
        print("Available templates:")
        for t in templates:
            print(f"  - {t}")
    
    elif args.command == 'show':
        variables = engine.show_template_variables(args.template)
        print(f"Variables in {args.template}:")
        for v in variables:
            prompt = engine._get_variable_prompt(v)
            print(f"  - {v} {prompt}")
    
    elif args.command == 'extend':
        extensions = {}
        if args.section:
            for section in args.section:
                if '=' in section:
                    name, content = section.split('=', 1)
                    extensions[name] = content
        
        engine.extend_template(args.base, extensions, args.name)
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()