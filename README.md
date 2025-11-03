# LLM-Based Taxonomy Generation for University Module Learning Outcomes

## Overview

This project demonstrates how Large Language Models (LLMs) can automatically generate taxonomies of learning outcomes and skills from university module directories. It serves as a proof-of-concept for a research paper exploring automated skill trajectory analysis in higher education.

## Purpose

The goal is to show that an LLM can:
1. Extract learning outcomes from university module descriptors
2. Identify and categorize specific skills and competencies
3. Generate a hierarchical taxonomy of these skills
4. Provide structured data suitable for future student performance analysis

## Current Scope

- **Data Source**: University College Dublin (UCD) Computer Science modules
- **Target**: Publicly available module descriptors from [UCD Hub](https://hub.ucd.ie/usis/!W_HU_MENU.P_PUBLISH?p_tag=MODULESCURRENT)
- **Use Case**: Proof-of-concept for academic paper/poster submission

## Project Structure

```
hcai_paper/
├── src/
│   ├── scraper.py              # UCD module web scraper
│   ├── taxonomy_generator.py   # LLM-based taxonomy generation
│   ├── visualizer.py           # Visualization tools
│   └── analysis.py             # Analysis and validation
├── data/                       # Generated data (created after running)
│   ├── comp_modules.json       # Scraped module data
│   └── taxonomy.json           # Generated taxonomy
├── figures/                    # Visualizations (created after running)
├── reports/                    # Analysis reports (created after running)
├── main.py                     # Main orchestration script
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Installation

### Prerequisites

- Python 3.8 or higher
- Anthropic API key (for Claude LLM access)

### Setup

1. **Clone the repository**:
   ```bash
   cd /path/to/hcai_paper
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your API key**:
   ```bash
   cp .env.example .env
   # Edit .env and add your Anthropic API key
   ```

## Usage

### Using a Module List File (Recommended)

The scraper can read module codes from a `modules.txt` file:

1. **Create the file:**
   ```bash
   cp modules.txt.example modules.txt
   ```

2. **Edit `modules.txt`** to include your desired module codes (one per line):
   ```
   COMP10010
   COMP10020
   COMP10030
   # Add more modules...
   ```

3. **Run the scraper:**
   ```bash
   python3 main.py
   ```

The scraper will automatically detect and use `modules.txt` if it exists.

**Benefits:**
- ✓ Only scrapes modules you care about
- ✓ Much faster than pattern-based searching
- ✓ Easy to manage and update
- ✓ Can mix modules from different disciplines

### Pattern-Based Scraping (Fallback)

If no `modules.txt` exists, the scraper falls back to pattern-based generation:

**Test mode (default - recommended for first run):**

By default, the scraper runs in test mode and only fetches ~10 modules:

```bash
python3 main.py
```

This is perfect for:
- Testing the pipeline works
- Validating outputs before full run
- Low cost (~10 modules × 4-5 outcomes = ~$0.50 API cost)

**Full scrape (comprehensive):**

To scrape all available COMP modules (may find 50-100+ modules):

```bash
python3 main.py --full-scrape
```

**Custom limits:**

```bash
# Fetch up to 20 modules
python3 main.py --max-modules 20

# Unlimited (with full scrape only)
python3 main.py --full-scrape --max-modules 0
```

### Partial Runs

If you want to skip certain steps (useful if you already have intermediate data):

```bash
# Skip scraping (use existing data/comp_modules.json)
python main.py --skip-scraping

# Skip taxonomy generation (use existing data/taxonomy.json)
python main.py --skip-taxonomy

# Only generate visualizations
python main.py --only-visualize

# Only generate analysis reports
python main.py --only-analyze
```

### Individual Components

You can also run components separately:

```bash
# Scrape modules
python -m src.scraper

# Generate taxonomy
python -m src.taxonomy_generator

# Generate visualizations
python -m src.visualizer

# Generate analysis reports
python -m src.analysis
```

## Output Files

After running the pipeline, you'll find:

### Data Files
- `data/comp_modules.json` - Raw scraped module data with learning outcomes
- `data/taxonomy.json` - Generated hierarchical taxonomy with skill classifications

### Visualizations (in `figures/`)
- `skill_distribution.png` - Distribution of skills across domains
- `blooms_distribution.png` - Distribution by Bloom's taxonomy levels
- `category_distribution.png` - Skill category breakdown (Technical, Cognitive, etc.)
- `level_progression.png` - Skill complexity progression across module levels
- `taxonomy_hierarchy.png` - Network graph of taxonomy structure

### Reports (in `reports/`)
- `analysis_report.txt` - Human-readable summary statistics
- `statistics.json` - Structured statistics for further analysis
- `module_summary.csv` - Table of all analyzed modules
- `skill_frequency.csv` - Most frequently occurring skills
- `*.tex` - LaTeX tables for direct inclusion in papers

## Methodology

### 1. Data Collection
The scraper fetches module descriptors from UCD's public module directory, extracting:
- Module code, title, and description
- Learning outcomes
- Assessment methods
- Module level and credits
- Syllabus content

### 2. Skill Extraction
For each module's learning outcomes, the LLM:
- Identifies specific skills and competencies
- Categorizes skills (Technical, Cognitive, Interpersonal, Domain-Specific)
- Assigns skill types (Programming, Problem-Solving, Analysis, etc.)
- Maps to Bloom's taxonomy levels (Remember → Create)

### 3. Taxonomy Generation
The system aggregates all extracted skills and uses the LLM to:
- Group similar skills into categories
- Create hierarchical structure (Domains → Sub-categories → Skills)
- Identify proficiency levels
- Track which modules teach which skills

### 4. Validation & Analysis
The system generates:
- Summary statistics
- Distribution analyses
- Frequency counts
- Cross-level comparisons

## Key Features

✓ **Automated extraction** - No manual coding of learning outcomes
✓ **Hierarchical taxonomy** - Multi-level skill organization
✓ **Bloom's taxonomy mapping** - Cognitive complexity analysis
✓ **Publication-ready outputs** - LaTeX tables, high-res figures
✓ **Reproducible** - All steps documented and rerunnable
✓ **Extensible** - Easy to adapt to other universities or disciplines

## Future Work

This proof-of-concept sets the stage for:
- Integration with student performance data
- Fine-grained skill trajectory analysis
- Predictive modeling of student outcomes
- Cross-institutional comparisons
- Curriculum optimization recommendations

## Technical Notes

### LLM Configuration
- Model: Claude 3.5 Sonnet (latest)
- Temperature: 0.3 for extraction, 0.5 for taxonomy generation
- Uses structured prompts for consistency

### Scraping Considerations
- Respectful rate limiting (0.5s delays)
- Handles dynamic content and AJAX-loaded data
- Graceful error handling for missing modules

### Data Privacy
- Only uses publicly available module descriptors
- No student data involved in this proof-of-concept

## Citation

If you use this code or methodology in your research, please cite:

```
[Citation details to be added upon publication]
```

## License

[License to be determined]

## Contact

For questions or collaboration opportunities, please contact [your contact information].

## Acknowledgments

- University College Dublin for providing public module data
- Anthropic for Claude API access