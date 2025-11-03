#!/usr/bin/env python3
"""
Main orchestration script for taxonomy generation pipeline

This script runs the complete pipeline:
1. Scrape UCD COMP module data
2. Extract skills using LLM
3. Generate hierarchical taxonomy
4. Create visualizations
5. Generate analysis reports
"""
import argparse
import os
from src.scraper import UCDModuleScraper
from src.taxonomy_generator import TaxonomyGenerator
from src.visualizer import TaxonomyVisualizer
from src.analysis import TaxonomyAnalyzer


def main():
    parser = argparse.ArgumentParser(
        description='Generate taxonomy from UCD module data'
    )
    parser.add_argument(
        '--skip-scraping',
        action='store_true',
        help='Skip scraping step (use existing data/comp_modules.json)'
    )
    parser.add_argument(
        '--skip-taxonomy',
        action='store_true',
        help='Skip taxonomy generation (use existing data/taxonomy.json)'
    )
    parser.add_argument(
        '--only-visualize',
        action='store_true',
        help='Only generate visualizations from existing taxonomy'
    )
    parser.add_argument(
        '--only-analyze',
        action='store_true',
        help='Only generate analysis reports from existing taxonomy'
    )
    parser.add_argument(
        '--full-scrape',
        action='store_true',
        help='Scrape all modules (not just test subset). WARNING: This may take hours!'
    )
    parser.add_argument(
        '--max-modules',
        type=int,
        default=10,
        help='Maximum number of modules to scrape (default: 10). Set to 0 for unlimited.'
    )

    args = parser.parse_args()

    print("="*60)
    print("LLM-BASED TAXONOMY GENERATION FOR UNIVERSITY MODULES")
    print("="*60)

    # Step 1: Scrape modules
    if not args.skip_scraping and not args.only_visualize and not args.only_analyze:
        test_mode = not args.full_scrape
        mode_text = "TEST MODE (limited search)" if test_mode else "FULL MODE (comprehensive search)"
        print(f"\n[STEP 1] Scraping UCD COMP modules... ({mode_text})")

        scraper = UCDModuleScraper()
        modules = scraper.scrape_all_comp_modules(
            test_mode=test_mode,
            max_modules=args.max_modules if not args.full_scrape else 0
        )

        if not modules:
            print("ERROR: No modules found. Exiting.")
            return

    # Step 2: Generate taxonomy
    if not args.skip_taxonomy and not args.only_visualize and not args.only_analyze:
        print("\n[STEP 2] Generating taxonomy using LLM...")

        # Check for API key
        if not os.getenv('ANTHROPIC_API_KEY'):
            print("ERROR: ANTHROPIC_API_KEY not found in environment.")
            print("Please create a .env file with your API key.")
            print("See .env.example for reference.")
            return

        generator = TaxonomyGenerator()

        # Load scraped modules
        import json
        with open('data/comp_modules.json', 'r') as f:
            modules = json.load(f)

        taxonomy_data = generator.build_taxonomy(modules)
        generator.save_taxonomy(taxonomy_data, 'data/taxonomy.json')

    # Step 3: Generate visualizations
    if not args.only_analyze:
        print("\n[STEP 3] Generating visualizations...")
        visualizer = TaxonomyVisualizer()
        visualizer.generate_all_visualizations('data/taxonomy.json')

    # Step 4: Generate analysis reports
    if not args.only_visualize:
        print("\n[STEP 4] Generating analysis reports...")
        analyzer = TaxonomyAnalyzer('data/taxonomy.json')
        analyzer.generate_report()

    print("\n" + "="*60)
    print("PIPELINE COMPLETE!")
    print("="*60)
    print("\nOutput files:")
    print("  - Data: data/comp_modules.json, data/taxonomy.json")
    print("  - Figures: figures/*.png")
    print("  - Reports: reports/*.csv, reports/*.tex, reports/*.txt")
    print("\nYou can now use these outputs for your academic paper.")


if __name__ == "__main__":
    main()
