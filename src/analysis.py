"""
Analysis and validation tools for taxonomy generation
Provides metrics and statistics for academic evaluation
"""
import json
import pandas as pd
from typing import Dict, List
from collections import Counter, defaultdict
import os


class TaxonomyAnalyzer:
    """Analyze and validate generated taxonomies"""

    def __init__(self, taxonomy_file: str):
        """
        Initialize analyzer with taxonomy data

        Args:
            taxonomy_file: Path to taxonomy JSON file
        """
        with open(taxonomy_file, 'r') as f:
            self.data = json.load(f)

        self.taxonomy = self.data.get('taxonomy', {})
        self.modules = self.data.get('modules', [])

    def generate_summary_statistics(self) -> Dict:
        """
        Generate summary statistics for the taxonomy

        Returns:
            Dictionary of statistics
        """
        stats = {
            'total_modules': len(self.modules),
            'modules_with_outcomes': sum(1 for m in self.modules if m.get('learning_outcomes')),
            'total_skills_extracted': self.data.get('total_skills', 0),
            'total_domains': len(self.taxonomy.get('domains', [])),
            'skills_by_level': self._count_skills_by_level(),
            'skills_by_category': self._count_skills_by_category(),
            'skills_by_blooms': self._count_skills_by_blooms(),
            'average_skills_per_module': self._average_skills_per_module(),
            'module_level_distribution': self._module_level_distribution(),
        }

        return stats

    def _count_skills_by_level(self) -> Dict[int, int]:
        """Count skills grouped by module level"""
        level_counts = defaultdict(int)

        for module in self.modules:
            level = module.get('level', 0)
            skill_count = len(module.get('extracted_skills', []))
            level_counts[level] += skill_count

        return dict(level_counts)

    def _count_skills_by_category(self) -> Dict[str, int]:
        """Count skills by category"""
        categories = []

        for module in self.modules:
            for skill in module.get('extracted_skills', []):
                categories.append(skill.get('category', 'Unknown'))

        return dict(Counter(categories))

    def _count_skills_by_blooms(self) -> Dict[str, int]:
        """Count skills by Bloom's taxonomy level"""
        blooms = []

        for module in self.modules:
            for skill in module.get('extracted_skills', []):
                blooms.append(skill.get('blooms_level', 'Unknown'))

        return dict(Counter(blooms))

    def _average_skills_per_module(self) -> float:
        """Calculate average number of skills per module"""
        if not self.modules:
            return 0.0

        total_skills = sum(len(m.get('extracted_skills', [])) for m in self.modules)
        return total_skills / len(self.modules)

    def _module_level_distribution(self) -> Dict[int, int]:
        """Count modules by level"""
        levels = [m.get('level', 0) for m in self.modules]
        return dict(Counter(levels))

    def generate_module_summary_table(self) -> pd.DataFrame:
        """
        Generate a summary table of all modules

        Returns:
            Pandas DataFrame with module summaries
        """
        rows = []

        for module in self.modules:
            rows.append({
                'Code': module.get('code', ''),
                'Title': module.get('title', ''),
                'Level': module.get('level', 0),
                'Credits': module.get('credits', 0),
                'Learning Outcomes': len(module.get('learning_outcomes', [])),
                'Extracted Skills': len(module.get('extracted_skills', [])),
            })

        return pd.DataFrame(rows)

    def generate_skill_frequency_table(self, top_n: int = 20) -> pd.DataFrame:
        """
        Generate table of most frequently occurring skills

        Args:
            top_n: Number of top skills to return

        Returns:
            Pandas DataFrame with skill frequencies
        """
        skill_counts = Counter()

        for module in self.modules:
            for skill in module.get('extracted_skills', []):
                skill_name = skill.get('skill_name', 'Unknown')
                skill_counts[skill_name] += 1

        # Get top N
        top_skills = skill_counts.most_common(top_n)

        return pd.DataFrame(top_skills, columns=['Skill', 'Frequency'])

    def export_latex_table(self, df: pd.DataFrame, output_file: str):
        """
        Export DataFrame as LaTeX table for paper

        Args:
            df: Pandas DataFrame
            output_file: Output file path
        """
        latex = df.to_latex(index=False, caption="Module Summary", label="tab:modules")

        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        with open(output_file, 'w') as f:
            f.write(latex)

        print(f"✓ LaTeX table saved to: {output_file}")

    def generate_report(self, output_dir: str = "reports"):
        """
        Generate comprehensive analysis report

        Args:
            output_dir: Directory to save report files
        """
        os.makedirs(output_dir, exist_ok=True)

        print("\n" + "="*60)
        print("GENERATING ANALYSIS REPORT")
        print("="*60)

        # Summary statistics
        stats = self.generate_summary_statistics()

        # Module summary table
        module_df = self.generate_module_summary_table()

        # Skill frequency table
        skill_freq_df = self.generate_skill_frequency_table()

        # Save statistics to JSON
        stats_file = os.path.join(output_dir, "statistics.json")
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)
        print(f"✓ Statistics saved to: {stats_file}")

        # Save tables to CSV
        module_csv = os.path.join(output_dir, "module_summary.csv")
        module_df.to_csv(module_csv, index=False)
        print(f"✓ Module summary saved to: {module_csv}")

        skill_csv = os.path.join(output_dir, "skill_frequency.csv")
        skill_freq_df.to_csv(skill_csv, index=False)
        print(f"✓ Skill frequency saved to: {skill_csv}")

        # Export LaTeX tables
        module_latex = os.path.join(output_dir, "module_summary.tex")
        self.export_latex_table(module_df, module_latex)

        skill_latex = os.path.join(output_dir, "skill_frequency.tex")
        self.export_latex_table(skill_freq_df, skill_latex)

        # Generate text report
        report_file = os.path.join(output_dir, "analysis_report.txt")
        self._write_text_report(stats, report_file)

        print(f"\n✓ Analysis complete! All files saved to: {output_dir}/")

    def _write_text_report(self, stats: Dict, output_file: str):
        """Write human-readable text report"""
        with open(output_file, 'w') as f:
            f.write("="*60 + "\n")
            f.write("TAXONOMY GENERATION ANALYSIS REPORT\n")
            f.write("="*60 + "\n\n")

            f.write("SUMMARY STATISTICS\n")
            f.write("-"*60 + "\n")
            f.write(f"Total modules analyzed: {stats['total_modules']}\n")
            f.write(f"Modules with learning outcomes: {stats['modules_with_outcomes']}\n")
            f.write(f"Total skills extracted: {stats['total_skills_extracted']}\n")
            f.write(f"Total domains identified: {stats['total_domains']}\n")
            f.write(f"Average skills per module: {stats['average_skills_per_module']:.2f}\n\n")

            f.write("MODULE LEVEL DISTRIBUTION\n")
            f.write("-"*60 + "\n")
            for level, count in sorted(stats['module_level_distribution'].items()):
                f.write(f"Level {level}: {count} modules\n")
            f.write("\n")

            f.write("SKILLS BY CATEGORY\n")
            f.write("-"*60 + "\n")
            for category, count in sorted(stats['skills_by_category'].items(),
                                          key=lambda x: x[1], reverse=True):
                f.write(f"{category}: {count}\n")
            f.write("\n")

            f.write("SKILLS BY BLOOM'S TAXONOMY LEVEL\n")
            f.write("-"*60 + "\n")
            blooms_order = ['Remember', 'Understand', 'Apply', 'Analyze', 'Evaluate', 'Create']
            for level in blooms_order:
                count = stats['skills_by_blooms'].get(level, 0)
                f.write(f"{level}: {count}\n")
            f.write("\n")

            f.write("SKILLS BY MODULE LEVEL\n")
            f.write("-"*60 + "\n")
            for level, count in sorted(stats['skills_by_level'].items()):
                f.write(f"Level {level}: {count} skills\n")
            f.write("\n")

        print(f"✓ Text report saved to: {output_file}")


def main():
    """Main function to run analysis"""
    analyzer = TaxonomyAnalyzer('data/taxonomy.json')
    analyzer.generate_report()


if __name__ == "__main__":
    main()
