"""
Visualization tools for taxonomy and module analysis
Generates figures suitable for academic papers and posters
"""
import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import networkx as nx
from collections import Counter, defaultdict
from typing import Dict, List
import os


class TaxonomyVisualizer:
    """Create visualizations for taxonomy analysis"""

    def __init__(self, style: str = 'seaborn-v0_8-paper'):
        """Initialize visualizer with matplotlib style"""
        try:
            plt.style.use(style)
        except:
            plt.style.use('default')

        sns.set_palette("husl")
        self.output_dir = "figures"
        os.makedirs(self.output_dir, exist_ok=True)

    def load_taxonomy(self, taxonomy_file: str) -> Dict:
        """Load taxonomy from JSON file"""
        with open(taxonomy_file, 'r') as f:
            return json.load(f)

    def plot_skill_distribution(self, taxonomy_data: Dict, output_file: str = None):
        """
        Plot distribution of skills across domains

        Args:
            taxonomy_data: Taxonomy dictionary
            output_file: Output filename (optional)
        """
        if output_file is None:
            output_file = os.path.join(self.output_dir, "skill_distribution.png")

        domains = taxonomy_data['taxonomy'].get('domains', [])

        # Count skills per domain
        domain_counts = []
        domain_names = []

        for domain in domains:
            name = domain.get('name', 'Unknown')
            skill_count = 0

            for sub_cat in domain.get('sub_categories', []):
                skill_count += len(sub_cat.get('skills', []))

            domain_names.append(name)
            domain_counts.append(skill_count)

        # Create horizontal bar chart
        fig, ax = plt.subplots(figsize=(10, 6))

        y_pos = np.arange(len(domain_names))
        ax.barh(y_pos, domain_counts, color=sns.color_palette("husl", len(domain_names)))

        ax.set_yticks(y_pos)
        ax.set_yticklabels(domain_names)
        ax.invert_yaxis()
        ax.set_xlabel('Number of Skills', fontsize=12)
        ax.set_title('Distribution of Skills Across Domains', fontsize=14, fontweight='bold')

        # Add value labels
        for i, v in enumerate(domain_counts):
            ax.text(v + 0.5, i, str(v), va='center', fontsize=10)

        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_file}")
        plt.close()

    def plot_blooms_taxonomy_distribution(self, taxonomy_data: Dict, output_file: str = None):
        """
        Plot distribution of Bloom's taxonomy levels across skills

        Args:
            taxonomy_data: Taxonomy dictionary
            output_file: Output filename (optional)
        """
        if output_file is None:
            output_file = os.path.join(self.output_dir, "blooms_distribution.png")

        # Extract Bloom's levels from all skills
        blooms_levels = []

        for module in taxonomy_data.get('modules', []):
            for skill in module.get('extracted_skills', []):
                level = skill.get('blooms_level', 'Unknown')
                blooms_levels.append(level)

        # Count occurrences
        level_counts = Counter(blooms_levels)

        # Order by Bloom's taxonomy hierarchy
        ordered_levels = ['Remember', 'Understand', 'Apply', 'Analyze', 'Evaluate', 'Create']
        ordered_counts = [level_counts.get(level, 0) for level in ordered_levels]

        # Create bar chart
        fig, ax = plt.subplots(figsize=(10, 6))

        x_pos = np.arange(len(ordered_levels))
        colors = plt.cm.viridis(np.linspace(0.2, 0.9, len(ordered_levels)))

        bars = ax.bar(x_pos, ordered_counts, color=colors)

        ax.set_xticks(x_pos)
        ax.set_xticklabels(ordered_levels, rotation=45, ha='right')
        ax.set_ylabel('Number of Skills', fontsize=12)
        ax.set_title("Distribution of Skills by Bloom's Taxonomy Level", fontsize=14, fontweight='bold')

        # Add value labels
        for i, v in enumerate(ordered_counts):
            ax.text(i, v + 0.5, str(v), ha='center', va='bottom', fontsize=10)

        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_file}")
        plt.close()

    def plot_skill_category_distribution(self, taxonomy_data: Dict, output_file: str = None):
        """
        Plot distribution of skill categories (Technical, Cognitive, etc.)

        Args:
            taxonomy_data: Taxonomy dictionary
            output_file: Output filename (optional)
        """
        if output_file is None:
            output_file = os.path.join(self.output_dir, "category_distribution.png")

        # Extract categories
        categories = []

        for module in taxonomy_data.get('modules', []):
            for skill in module.get('extracted_skills', []):
                category = skill.get('category', 'Unknown')
                categories.append(category)

        # Count occurrences
        category_counts = Counter(categories)

        # Create pie chart
        fig, ax = plt.subplots(figsize=(10, 8))

        labels = list(category_counts.keys())
        sizes = list(category_counts.values())
        colors = sns.color_palette("husl", len(labels))

        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            colors=colors,
            autopct='%1.1f%%',
            startangle=90,
            textprops={'fontsize': 11}
        )

        # Make percentage text bold
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')

        ax.set_title('Distribution of Skill Categories', fontsize=14, fontweight='bold', pad=20)

        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_file}")
        plt.close()

    def plot_module_level_progression(self, taxonomy_data: Dict, output_file: str = None):
        """
        Plot how skill complexity progresses across module levels

        Args:
            taxonomy_data: Taxonomy dictionary
            output_file: Output filename (optional)
        """
        if output_file is None:
            output_file = os.path.join(self.output_dir, "level_progression.png")

        # Group skills by module level and Bloom's level
        level_blooms = defaultdict(lambda: defaultdict(int))

        for module in taxonomy_data.get('modules', []):
            module_level = module.get('level', 0)

            for skill in module.get('extracted_skills', []):
                blooms = skill.get('blooms_level', 'Unknown')
                level_blooms[module_level][blooms] += 1

        # Create stacked bar chart
        fig, ax = plt.subplots(figsize=(12, 6))

        levels = sorted(level_blooms.keys())
        blooms_order = ['Remember', 'Understand', 'Apply', 'Analyze', 'Evaluate', 'Create']

        # Prepare data for stacking
        data_dict = {blooms: [] for blooms in blooms_order}

        for level in levels:
            for blooms in blooms_order:
                data_dict[blooms].append(level_blooms[level].get(blooms, 0))

        # Create stacked bars
        bottom = np.zeros(len(levels))
        colors = plt.cm.viridis(np.linspace(0.2, 0.9, len(blooms_order)))

        for i, blooms in enumerate(blooms_order):
            ax.bar(levels, data_dict[blooms], bottom=bottom, label=blooms, color=colors[i])
            bottom += np.array(data_dict[blooms])

        ax.set_xlabel('Module Level', fontsize=12)
        ax.set_ylabel('Number of Skills', fontsize=12)
        ax.set_title("Skill Progression Across Module Levels (Bloom's Taxonomy)", fontsize=14, fontweight='bold')
        ax.legend(title="Bloom's Level", bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.set_xticks(levels)

        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_file}")
        plt.close()

    def plot_taxonomy_hierarchy(self, taxonomy_data: Dict, output_file: str = None):
        """
        Create a network graph visualization of the taxonomy hierarchy

        Args:
            taxonomy_data: Taxonomy dictionary
            output_file: Output filename (optional)
        """
        if output_file is None:
            output_file = os.path.join(self.output_dir, "taxonomy_hierarchy.png")

        # Build network graph
        G = nx.DiGraph()

        # Add root node
        G.add_node("Root", level=0, node_type="root")

        # Add domains, sub-categories, and skills
        domains = taxonomy_data['taxonomy'].get('domains', [])

        for domain in domains:
            domain_name = domain.get('name', 'Unknown')
            G.add_node(domain_name, level=1, node_type="domain")
            G.add_edge("Root", domain_name)

            for sub_cat in domain.get('sub_categories', []):
                sub_cat_name = sub_cat.get('name', 'Unknown')
                node_id = f"{domain_name}::{sub_cat_name}"
                G.add_node(node_id, level=2, node_type="subcategory", label=sub_cat_name)
                G.add_edge(domain_name, node_id)

                # Optionally add top skills (limit to avoid clutter)
                for skill in sub_cat.get('skills', [])[:3]:  # Top 3 skills per subcategory
                    skill_name = skill.get('name', 'Unknown')
                    skill_id = f"{node_id}::{skill_name}"
                    G.add_node(skill_id, level=3, node_type="skill", label=skill_name)
                    G.add_edge(node_id, skill_id)

        # Create layout
        fig, ax = plt.subplots(figsize=(16, 12))

        # Use hierarchical layout
        pos = nx.spring_layout(G, k=2, iterations=50, seed=42)

        # Draw nodes by type
        root_nodes = [n for n, d in G.nodes(data=True) if d.get('node_type') == 'root']
        domain_nodes = [n for n, d in G.nodes(data=True) if d.get('node_type') == 'domain']
        subcat_nodes = [n for n, d in G.nodes(data=True) if d.get('node_type') == 'subcategory']
        skill_nodes = [n for n, d in G.nodes(data=True) if d.get('node_type') == 'skill']

        nx.draw_networkx_nodes(G, pos, nodelist=root_nodes, node_color='red',
                               node_size=1000, alpha=0.9, ax=ax)
        nx.draw_networkx_nodes(G, pos, nodelist=domain_nodes, node_color='lightblue',
                               node_size=700, alpha=0.8, ax=ax)
        nx.draw_networkx_nodes(G, pos, nodelist=subcat_nodes, node_color='lightgreen',
                               node_size=400, alpha=0.7, ax=ax)
        nx.draw_networkx_nodes(G, pos, nodelist=skill_nodes, node_color='yellow',
                               node_size=200, alpha=0.6, ax=ax)

        # Draw edges
        nx.draw_networkx_edges(G, pos, alpha=0.3, arrows=True, arrowsize=10, ax=ax)

        # Draw labels (use short labels for readability)
        labels = {}
        for node, data in G.nodes(data=True):
            if data.get('node_type') == 'root':
                labels[node] = node
            elif data.get('node_type') == 'domain':
                labels[node] = node[:20]  # Truncate long names
            else:
                labels[node] = data.get('label', node)[:15]

        nx.draw_networkx_labels(G, pos, labels, font_size=8, ax=ax)

        ax.set_title('Taxonomy Hierarchy Visualization (Sample)', fontsize=16, fontweight='bold')
        ax.axis('off')

        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_file}")
        plt.close()

    def generate_all_visualizations(self, taxonomy_file: str):
        """Generate all visualizations"""
        print("\n" + "="*60)
        print("GENERATING VISUALIZATIONS")
        print("="*60)

        taxonomy_data = self.load_taxonomy(taxonomy_file)

        self.plot_skill_distribution(taxonomy_data)
        self.plot_blooms_taxonomy_distribution(taxonomy_data)
        self.plot_skill_category_distribution(taxonomy_data)
        self.plot_module_level_progression(taxonomy_data)
        self.plot_taxonomy_hierarchy(taxonomy_data)

        print(f"\n✓ All visualizations saved to: {self.output_dir}/")


def main():
    """Main function to generate visualizations"""
    visualizer = TaxonomyVisualizer()
    visualizer.generate_all_visualizations('data/taxonomy.json')


if __name__ == "__main__":
    main()
