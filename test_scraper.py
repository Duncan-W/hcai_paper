#!/usr/bin/env python3
"""
Quick test script to validate the scraper on a single known module
"""
from src.scraper import UCDModuleScraper
import json


def test_single_module():
    """Test scraper on COMP10010 (known to exist)"""
    print("="*60)
    print("TESTING SCRAPER ON COMP10010")
    print("="*60)

    scraper = UCDModuleScraper()

    # Fetch a known module
    module = scraper.fetch_module_descriptor("COMP10010")

    if module:
        print("\n✓ Module found!")
        print(f"\nCode: {module['code']}")
        print(f"Title: {module['title']}")
        print(f"Level: {module['level']}")
        print(f"Credits: {module['credits']}")
        print(f"Coordinator: {module['coordinator']}")

        print(f"\nDescription ({len(module['description'])} chars):")
        print(f"  {module['description'][:200]}...")

        print(f"\nLearning Outcomes ({len(module['learning_outcomes'])} found):")
        for i, outcome in enumerate(module['learning_outcomes'], 1):
            print(f"  {i}. {outcome[:80]}...")

        print(f"\nSyllabus ({len(module['syllabus'])} chars):")
        print(f"  {module['syllabus'][:200]}...")

        print(f"\nAssessment ({len(module['assessment'])} chars):")
        print(f"  {module['assessment'][:200]}...")

        # Save to file for inspection
        with open('test_module.json', 'w', encoding='utf-8') as f:
            json.dump(module, f, indent=2, ensure_ascii=False)

        print(f"\n✓ Full module data saved to: test_module.json")

        # Validate quality
        print("\n" + "="*60)
        print("VALIDATION")
        print("="*60)

        issues = []

        if not module['description']:
            issues.append("⚠ No description extracted")
        if not module['learning_outcomes']:
            issues.append("⚠ No learning outcomes extracted")
        elif len(module['learning_outcomes']) < 3:
            issues.append(f"⚠ Only {len(module['learning_outcomes'])} learning outcomes (expected more)")
        if not module['assessment']:
            issues.append("⚠ No assessment info extracted")
        if module['level'] == 0:
            issues.append("⚠ Level not extracted")
        if module['credits'] == 0:
            issues.append("⚠ Credits not extracted")

        if issues:
            print("\nIssues found:")
            for issue in issues:
                print(f"  {issue}")
        else:
            print("\n✓ All fields extracted successfully!")

        return True

    else:
        print("\n✗ Module not found or failed to parse")
        return False


if __name__ == "__main__":
    test_single_module()
