"""
LLM-Based Taxonomy Generator
Uses Anthropic's Claude to extract skills and generate taxonomies from module learning outcomes
"""
import os
import json
from typing import Dict, List, Optional, Set
from anthropic import Anthropic
from dotenv import load_dotenv
import time


class TaxonomyGenerator:
    """Generate taxonomies of skills and learning outcomes using LLM analysis"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the taxonomy generator

        Args:
            api_key: Anthropic API key (if not provided, loads from environment)
        """
        load_dotenv()
        self.client = Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-3-5-sonnet-20241022"

    def extract_skills_from_outcomes(self, learning_outcomes: List[str], module_context: Dict) -> Dict:
        """
        Extract structured skills from learning outcomes using LLM

        Args:
            learning_outcomes: List of learning outcome strings
            module_context: Dictionary with module info (title, description, level, etc.)

        Returns:
            Dictionary with extracted skills categorized by type
        """
        if not learning_outcomes:
            return {"skills": [], "categories": []}

        prompt = f"""Analyze the following learning outcomes from a university Computer Science module and extract specific skills and competencies.

Module: {module_context.get('title', 'Unknown')}
Level: {module_context.get('level', 'Unknown')}
Description: {module_context.get('description', 'N/A')}

Learning Outcomes:
{chr(10).join(f"{i+1}. {outcome}" for i, outcome in enumerate(learning_outcomes))}

Please extract and categorize the skills into a structured format. For each skill:
1. Identify the specific skill or competency
2. Categorize it (e.g., Technical, Cognitive, Interpersonal, Domain-Specific)
3. Assign a skill type (e.g., Programming, Problem-Solving, Analysis, Design, etc.)
4. Determine the Bloom's taxonomy level (Remember, Understand, Apply, Analyze, Evaluate, Create)

Return a JSON object with the following structure:
{{
  "skills": [
    {{
      "skill_name": "specific skill name",
      "description": "brief description of the skill",
      "category": "Technical|Cognitive|Interpersonal|Domain-Specific",
      "skill_type": "more specific classification",
      "blooms_level": "Remember|Understand|Apply|Analyze|Evaluate|Create",
      "keywords": ["relevant", "keywords"]
    }}
  ]
}}

Be thorough and extract all distinct skills mentioned or implied in the learning outcomes."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.3,  # Lower temperature for more consistent extraction
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            result_text = response.content[0].text

            # Extract JSON from response (handle cases where LLM adds explanation)
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1

            if json_start != -1 and json_end > json_start:
                result_json = json.loads(result_text[json_start:json_end])
                return result_json
            else:
                print(f"Warning: Could not parse JSON from response: {result_text[:200]}")
                return {"skills": []}

        except Exception as e:
            print(f"Error extracting skills: {e}")
            return {"skills": []}

    def build_taxonomy(self, all_modules: List[Dict]) -> Dict:
        """
        Build a hierarchical taxonomy from all module data

        Args:
            all_modules: List of module dictionaries with extracted skills

        Returns:
            Hierarchical taxonomy structure
        """
        print("\n" + "="*60)
        print("BUILDING TAXONOMY FROM MODULE DATA")
        print("="*60)

        # First, extract skills from all modules
        print(f"\nProcessing {len(all_modules)} modules...")

        enriched_modules = []
        all_skills = []

        for i, module in enumerate(all_modules):
            print(f"\n[{i+1}/{len(all_modules)}] Analyzing: {module.get('code', 'Unknown')} - {module.get('title', 'Unknown')}")

            if not module.get('learning_outcomes'):
                print("  ⚠ No learning outcomes found, skipping...")
                continue

            # Extract skills for this module
            skills_data = self.extract_skills_from_outcomes(
                module['learning_outcomes'],
                {
                    'title': module.get('title', ''),
                    'description': module.get('description', ''),
                    'level': module.get('level', 0),
                }
            )

            module['extracted_skills'] = skills_data.get('skills', [])
            enriched_modules.append(module)
            all_skills.extend(skills_data.get('skills', []))

            print(f"  ✓ Extracted {len(skills_data.get('skills', []))} skills")

            # Rate limiting
            time.sleep(1)

        print(f"\n✓ Total skills extracted: {len(all_skills)}")

        # Now build the taxonomy using LLM
        taxonomy = self._generate_taxonomy_structure(all_skills, enriched_modules)

        return {
            'taxonomy': taxonomy,
            'modules': enriched_modules,
            'total_skills': len(all_skills),
            'total_modules': len(enriched_modules)
        }

    def _generate_taxonomy_structure(self, all_skills: List[Dict], modules: List[Dict]) -> Dict:
        """
        Use LLM to generate a hierarchical taxonomy structure from all extracted skills

        Args:
            all_skills: List of all skill dictionaries
            modules: List of module dictionaries

        Returns:
            Hierarchical taxonomy
        """
        print("\n" + "="*60)
        print("GENERATING HIERARCHICAL TAXONOMY")
        print("="*60)

        # Create summary of skills for LLM
        skills_summary = []
        for skill in all_skills:
            skills_summary.append({
                'name': skill.get('skill_name', ''),
                'type': skill.get('skill_type', ''),
                'category': skill.get('category', ''),
            })

        prompt = f"""You are analyzing skills extracted from {len(modules)} Computer Science university modules.

Below is a list of {len(all_skills)} skills that have been extracted:

{json.dumps(skills_summary, indent=2)}

Please create a hierarchical taxonomy that organizes these skills. The taxonomy should:

1. Group similar skills together into meaningful categories
2. Create a hierarchical structure (2-4 levels deep) that goes from general to specific
3. Identify skill domains (e.g., Software Development, Systems & Architecture, Data & Analytics, Theory & Algorithms, etc.)
4. Under each domain, create sub-categories that group related skills
5. Handle redundancy - if multiple modules mention the same skill, consolidate them
6. Be comprehensive but not overly granular

Return a JSON object with this structure:
{{
  "domains": [
    {{
      "name": "Domain Name",
      "description": "Brief description",
      "sub_categories": [
        {{
          "name": "Sub-category Name",
          "description": "Brief description",
          "skills": [
            {{
              "name": "Skill name",
              "proficiency_levels": ["Beginner", "Intermediate", "Advanced"],
              "appears_in_modules": ["COMP10010", ...]
            }}
          ]
        }}
      ]
    }}
  ]
}}

Be thorough and create a well-organized taxonomy suitable for academic publication."""

        try:
            print("\nQuerying LLM to generate taxonomy structure...")

            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=0.5,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            result_text = response.content[0].text

            # Extract JSON
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1

            if json_start != -1 and json_end > json_start:
                taxonomy = json.loads(result_text[json_start:json_end])
                print("✓ Taxonomy generated successfully")
                return taxonomy
            else:
                print("Warning: Could not parse taxonomy JSON")
                return {}

        except Exception as e:
            print(f"Error generating taxonomy: {e}")
            return {}

    def save_taxonomy(self, taxonomy_data: Dict, output_file: str):
        """Save taxonomy to JSON file"""
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(taxonomy_data, f, indent=2, ensure_ascii=False)

        print(f"\n✓ Taxonomy saved to: {output_file}")


def main():
    """Main function to test taxonomy generation"""
    # Load scraped modules
    with open('data/comp_modules.json', 'r') as f:
        modules = json.load(f)

    # Generate taxonomy
    generator = TaxonomyGenerator()
    taxonomy_data = generator.build_taxonomy(modules)

    # Save results
    generator.save_taxonomy(taxonomy_data, 'data/taxonomy.json')

    # Print summary
    print("\n" + "="*60)
    print("TAXONOMY GENERATION COMPLETE")
    print("="*60)
    print(f"Modules analyzed: {taxonomy_data['total_modules']}")
    print(f"Skills extracted: {taxonomy_data['total_skills']}")
    print(f"Domains identified: {len(taxonomy_data['taxonomy'].get('domains', []))}")


if __name__ == "__main__":
    main()
