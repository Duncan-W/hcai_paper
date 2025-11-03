#!/usr/bin/env python3
"""
Direct taxonomy generation without API calls
Analyzes the scraped modules and generates taxonomy structure
"""
import json
from typing import Dict, List
from collections import defaultdict


def analyze_learning_outcomes_direct(modules: List[Dict]) -> Dict:
    """
    Directly analyze learning outcomes and extract skills

    This function performs LLM-like analysis without API calls,
    extracting skills and categorizing them based on the module content.
    """

    all_extracted_skills = []
    enriched_modules = []

    for module in modules:
        code = module.get('code', 'Unknown')
        title = module.get('title', 'Unknown')
        level = module.get('level', 0)
        outcomes = module.get('learning_outcomes', [])

        if not outcomes:
            continue

        print(f"\nAnalyzing {code}: {title} (Level {level})")
        print(f"  Learning outcomes: {len(outcomes)}")

        # Extract skills from each learning outcome
        module_skills = []

        for outcome in outcomes:
            skills = extract_skills_from_outcome(outcome, level, code)
            module_skills.extend(skills)
            all_extracted_skills.extend(skills)

        # Add to module data
        module_copy = module.copy()
        module_copy['extracted_skills'] = module_skills
        enriched_modules.append(module_copy)

        print(f"  Extracted skills: {len(module_skills)}")

    return {
        'modules': enriched_modules,
        'all_skills': all_extracted_skills,
        'total_modules': len(enriched_modules),
        'total_skills': len(all_extracted_skills)
    }


def extract_skills_from_outcome(outcome: str, level: int, module_code: str) -> List[Dict]:
    """
    Extract skills from a single learning outcome

    Analyzes the text and identifies:
    - Skill name
    - Category (Technical, Cognitive, etc.)
    - Skill type
    - Bloom's taxonomy level
    """
    outcome_lower = outcome.lower()
    skills = []

    # Determine Bloom's level based on action verbs
    blooms_level = determine_blooms_level(outcome_lower)

    # Determine skill category and type based on content
    if any(word in outcome_lower for word in ['program', 'code', 'compile', 'debug', 'algorithm', 'data structure', 'function', 'method', 'procedure']):
        # Programming skills
        skills.append({
            'skill_name': extract_main_skill(outcome, 'Programming'),
            'description': outcome[:100],
            'category': 'Technical',
            'skill_type': 'Programming',
            'blooms_level': blooms_level,
            'keywords': extract_keywords(outcome_lower, ['program', 'code', 'function', 'algorithm']),
            'module': module_code
        })

    if any(word in outcome_lower for word in ['design', 'develop', 'create', 'build', 'construct']):
        # Design/Development skills
        skills.append({
            'skill_name': extract_main_skill(outcome, 'Design & Development'),
            'description': outcome[:100],
            'category': 'Technical',
            'skill_type': 'Software Design',
            'blooms_level': blooms_level,
            'keywords': extract_keywords(outcome_lower, ['design', 'develop', 'architecture']),
            'module': module_code
        })

    if any(word in outcome_lower for word in ['understand', 'comprehend', 'aware', 'familiar', 'describe', 'explain']):
        # Understanding/Knowledge skills
        skills.append({
            'skill_name': extract_main_skill(outcome, 'Conceptual Understanding'),
            'description': outcome[:100],
            'category': 'Cognitive',
            'skill_type': 'Comprehension',
            'blooms_level': blooms_level,
            'keywords': extract_keywords(outcome_lower, ['understand', 'knowledge', 'theory']),
            'module': module_code
        })

    if any(word in outcome_lower for word in ['test', 'debug', 'evaluate', 'analyze', 'assess']):
        # Analysis/Testing skills
        skills.append({
            'skill_name': extract_main_skill(outcome, 'Analysis & Testing'),
            'description': outcome[:100],
            'category': 'Technical',
            'skill_type': 'Testing & Debugging',
            'blooms_level': blooms_level,
            'keywords': extract_keywords(outcome_lower, ['test', 'debug', 'analyze']),
            'module': module_code
        })

    if any(word in outcome_lower for word in ['architecture', 'organization', 'system', 'structure']):
        # Systems/Architecture skills
        skills.append({
            'skill_name': extract_main_skill(outcome, 'Systems & Architecture'),
            'description': outcome[:100],
            'category': 'Domain-Specific',
            'skill_type': 'Computer Architecture',
            'blooms_level': blooms_level,
            'keywords': extract_keywords(outcome_lower, ['architecture', 'system', 'hardware']),
            'module': module_code
        })

    if any(word in outcome_lower for word in ['logic', 'proof', 'mathematical', 'formal', 'automata']):
        # Theoretical/Mathematical skills
        skills.append({
            'skill_name': extract_main_skill(outcome, 'Theoretical Foundations'),
            'description': outcome[:100],
            'category': 'Domain-Specific',
            'skill_type': 'Theory & Mathematics',
            'blooms_level': blooms_level,
            'keywords': extract_keywords(outcome_lower, ['logic', 'proof', 'mathematical']),
            'module': module_code
        })

    if any(word in outcome_lower for word in ['problem', 'solve', 'solution']):
        # Problem-solving skills
        skills.append({
            'skill_name': extract_main_skill(outcome, 'Problem Solving'),
            'description': outcome[:100],
            'category': 'Cognitive',
            'skill_type': 'Problem-Solving',
            'blooms_level': blooms_level,
            'keywords': extract_keywords(outcome_lower, ['problem', 'solve', 'solution']),
            'module': module_code
        })

    if any(word in outcome_lower for word in ['data', 'information', 'database']):
        # Data-related skills
        skills.append({
            'skill_name': extract_main_skill(outcome, 'Data Management'),
            'description': outcome[:100],
            'category': 'Technical',
            'skill_type': 'Data Science',
            'blooms_level': blooms_level,
            'keywords': extract_keywords(outcome_lower, ['data', 'information', 'analysis']),
            'module': module_code
        })

    # If no specific skills identified, create a general one
    if not skills:
        skills.append({
            'skill_name': outcome[:50],
            'description': outcome[:100],
            'category': 'General',
            'skill_type': 'General Competency',
            'blooms_level': blooms_level,
            'keywords': [],
            'module': module_code
        })

    return skills


def determine_blooms_level(text: str) -> str:
    """Determine Bloom's taxonomy level based on action verbs"""
    # Remember level
    if any(verb in text for verb in ['define', 'list', 'name', 'identify', 'recall', 'recognize']):
        return 'Remember'

    # Understand level
    if any(verb in text for verb in ['understand', 'comprehend', 'explain', 'describe', 'summarize', 'interpret', 'classify']):
        return 'Understand'

    # Apply level
    if any(verb in text for verb in ['apply', 'use', 'solve', 'implement', 'execute', 'carry out', 'write', 'run']):
        return 'Apply'

    # Analyze level
    if any(verb in text for verb in ['analyze', 'examine', 'compare', 'contrast', 'differentiate', 'organize', 'test', 'debug']):
        return 'Analyze'

    # Evaluate level
    if any(verb in text for verb in ['evaluate', 'assess', 'judge', 'critique', 'justify', 'argue', 'defend']):
        return 'Evaluate'

    # Create level
    if any(verb in text for verb in ['create', 'design', 'develop', 'construct', 'build', 'formulate', 'generate', 'plan']):
        return 'Create'

    # Default to Apply (most common for CS modules)
    return 'Apply'


def extract_main_skill(outcome: str, context: str) -> str:
    """Extract the main skill name from outcome text"""
    # Clean up the outcome text
    outcome = outcome.strip()

    # Try to get a concise skill name
    if len(outcome) < 60:
        return outcome

    # Extract first clause
    first_part = outcome.split(',')[0].split(';')[0]

    if len(first_part) < 80:
        return first_part

    # Return context-based name
    return f"{context} - {outcome[:40]}..."


def extract_keywords(text: str, candidates: List[str]) -> List[str]:
    """Extract relevant keywords from text"""
    keywords = []
    for keyword in candidates:
        if keyword in text:
            keywords.append(keyword)
    return keywords


def build_taxonomy_structure(all_skills: List[Dict]) -> Dict:
    """
    Build hierarchical taxonomy from extracted skills
    """
    print("\nBuilding taxonomy structure...")

    # Group skills by category and type
    taxonomy_tree = defaultdict(lambda: defaultdict(list))

    for skill in all_skills:
        category = skill.get('category', 'General')
        skill_type = skill.get('skill_type', 'General')
        taxonomy_tree[category][skill_type].append(skill)

    # Build formal taxonomy structure
    domains = []

    for category, skill_types in taxonomy_tree.items():
        sub_categories = []

        for skill_type, skills in skill_types.items():
            # Group similar skills
            unique_skills = consolidate_similar_skills(skills)

            sub_categories.append({
                'name': skill_type,
                'description': f'{skill_type} skills in {category} category',
                'skills': unique_skills
            })

        domains.append({
            'name': category,
            'description': f'{category} competencies',
            'sub_categories': sub_categories
        })

    return {'domains': domains}


def consolidate_similar_skills(skills: List[Dict]) -> List[Dict]:
    """Consolidate similar skills and track module appearances"""
    skill_map = defaultdict(lambda: {'modules': set(), 'blooms': [], 'descriptions': []})

    for skill in skills:
        name = skill.get('skill_name', 'Unknown')
        module = skill.get('module', 'Unknown')
        blooms = skill.get('blooms_level', 'Unknown')
        desc = skill.get('description', '')

        skill_map[name]['modules'].add(module)
        skill_map[name]['blooms'].append(blooms)
        skill_map[name]['descriptions'].append(desc)

    consolidated = []
    for name, data in skill_map.items():
        # Determine proficiency levels based on Bloom's levels
        blooms_set = set(data['blooms'])
        proficiency = determine_proficiency_levels(blooms_set)

        consolidated.append({
            'name': name,
            'proficiency_levels': proficiency,
            'appears_in_modules': sorted(list(data['modules'])),
            'bloom_levels': sorted(list(blooms_set))
        })

    return consolidated


def determine_proficiency_levels(blooms_levels: set) -> List[str]:
    """Determine proficiency levels based on Bloom's taxonomy"""
    blooms_hierarchy = {
        'Remember': 1,
        'Understand': 2,
        'Apply': 3,
        'Analyze': 4,
        'Evaluate': 5,
        'Create': 6
    }

    max_level = max(blooms_hierarchy.get(b, 3) for b in blooms_levels)

    if max_level <= 2:
        return ['Beginner']
    elif max_level <= 4:
        return ['Beginner', 'Intermediate']
    else:
        return ['Beginner', 'Intermediate', 'Advanced']


def main():
    """Main function"""
    print("="*60)
    print("DIRECT TAXONOMY GENERATION (NO API)")
    print("="*60)

    # Load modules
    print("\nLoading modules from data/comp_modules.json...")
    with open('data/comp_modules.json', 'r') as f:
        modules = json.load(f)

    print(f"Loaded {len(modules)} modules")

    # Analyze outcomes and extract skills
    print("\n" + "="*60)
    print("ANALYZING LEARNING OUTCOMES")
    print("="*60)

    analysis = analyze_learning_outcomes_direct(modules)

    print(f"\n✓ Analyzed {analysis['total_modules']} modules")
    print(f"✓ Extracted {analysis['total_skills']} skills")

    # Build taxonomy
    print("\n" + "="*60)
    print("BUILDING TAXONOMY")
    print("="*60)

    taxonomy = build_taxonomy_structure(analysis['all_skills'])

    # Combine results
    result = {
        'taxonomy': taxonomy,
        'modules': analysis['modules'],
        'total_skills': analysis['total_skills'],
        'total_modules': analysis['total_modules']
    }

    # Save
    output_file = 'data/taxonomy.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Taxonomy saved to: {output_file}")

    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Modules analyzed: {result['total_modules']}")
    print(f"Skills extracted: {result['total_skills']}")
    print(f"Domains identified: {len(taxonomy['domains'])}")

    for domain in taxonomy['domains']:
        print(f"\n  • {domain['name']}: {len(domain['sub_categories'])} sub-categories")
        for sub in domain['sub_categories']:
            print(f"    - {sub['name']}: {len(sub['skills'])} unique skills")


if __name__ == "__main__":
    main()
