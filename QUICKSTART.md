# Quick Start Guide

## 5-Minute Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. (Optional but Recommended) Create Module List

Create a `modules.txt` file with the module codes you want to scrape:

```bash
cp modules.txt.example modules.txt
# Edit modules.txt to add your desired module codes
```

**Example `modules.txt`:**
```
COMP10010
COMP10020
COMP10040
COMP10050
```

If you skip this step, the scraper will use pattern-based generation (slower).

### 3. Run the Pipeline

```bash
python3 main.py
```

**Note:** If you're using my (Claude's) direct taxonomy generation, you don't need an API key!

That's it! The system will:
- Scrape UCD COMP modules (~30-60 minutes depending on number of modules found)
- Extract skills using LLM (~2-4 hours with API rate limits)
- Generate visualizations (~1 minute)
- Create analysis reports (~1 minute)

## Expected Output

After completion, you'll have:

```
hcai_paper/
├── data/
│   ├── comp_modules.json      # ~50-100 modules with learning outcomes
│   └── taxonomy.json           # Hierarchical skill taxonomy
├── figures/
│   ├── skill_distribution.png
│   ├── blooms_distribution.png
│   ├── category_distribution.png
│   ├── level_progression.png
│   └── taxonomy_hierarchy.png
└── reports/
    ├── analysis_report.txt     # Human-readable summary
    ├── statistics.json         # Structured stats
    ├── module_summary.csv      # Module table
    ├── skill_frequency.csv     # Top skills
    └── *.tex                   # LaTeX tables
```

## Common Issues

### Issue: "No modules found"

**Solution**: The scraper uses pattern-based module code generation. If you get few results, check:
- UCD's website structure may have changed
- Module code patterns may differ
- Consider manually updating the code patterns in `src/scraper.py:get_comp_modules()`

### Issue: "ANTHROPIC_API_KEY not found"

**Solution**:
```bash
# Make sure .env file exists and has your key
cat .env  # Should show: ANTHROPIC_API_KEY=sk-...

# Or export directly
export ANTHROPIC_API_KEY=your_key_here
python main.py
```

### Issue: Rate limiting errors

**Solution**: The scraper includes delays, but if you hit API limits:
```python
# In src/taxonomy_generator.py, increase sleep time
time.sleep(2)  # Change from 1 to 2 seconds
```

### Issue: Scraping takes too long

**Solution**: Use a smaller subset for testing:
```bash
# Edit src/scraper.py and reduce the range in get_comp_modules()
# Or manually create a small test dataset
```

## Testing with Sample Data

Want to test without scraping? Create a minimal test dataset:

```python
# test_data.py
import json

sample_modules = [
    {
        "code": "COMP10010",
        "title": "Introduction to Programming I",
        "level": 1,
        "credits": 5,
        "description": "Introduction to programming concepts",
        "learning_outcomes": [
            "understand basic programming constructs",
            "design programs to solve simple problems",
            "evaluate programs to find errors"
        ],
        "extracted_skills": []
    },
    {
        "code": "COMP20010",
        "title": "Data Structures and Algorithms",
        "level": 2,
        "credits": 10,
        "description": "Study of fundamental data structures and algorithms",
        "learning_outcomes": [
            "implement common data structures",
            "analyze algorithm complexity",
            "design efficient algorithms"
        ],
        "extracted_skills": []
    }
]

# Save to data directory
import os
os.makedirs('data', exist_ok=True)
with open('data/comp_modules.json', 'w') as f:
    json.dump(sample_modules, f, indent=2)

print("Test data created! Run: python main.py --skip-scraping")
```

Then run:
```bash
python test_data.py
python main.py --skip-scraping
```

## Individual Component Testing

Test each component separately:

### Test Scraper
```bash
python -m src.scraper
# Creates: data/comp_modules.json
```

### Test Taxonomy Generator
```bash
# Requires: data/comp_modules.json
python -m src.taxonomy_generator
# Creates: data/taxonomy.json
```

### Test Visualizer
```bash
# Requires: data/taxonomy.json
python -m src.visualizer
# Creates: figures/*.png
```

### Test Analyzer
```bash
# Requires: data/taxonomy.json
python -m src.analysis
# Creates: reports/*
```

## Customization

### Change Target University

Edit `src/scraper.py`:

```python
class UCDModuleScraper:
    BASE_URL = "https://your-university.edu/modules"

    # Update extraction methods for your university's HTML structure
```

### Change Module Filter

Edit `src/scraper.py:get_comp_modules()`:

```python
# Change from COMP to other codes
for prefix in ['MATH', 'PHYS', 'CHEM']:
    # ... generate codes
```

### Adjust LLM Parameters

Edit `src/taxonomy_generator.py`:

```python
# Change model
self.model = "claude-3-5-sonnet-20241022"  # or other models

# Adjust temperature
temperature=0.3  # Lower = more consistent, Higher = more creative
```

### Customize Visualizations

Edit `src/visualizer.py`:

```python
# Change figure size
fig, ax = plt.subplots(figsize=(12, 8))  # Adjust width, height

# Change colors
sns.set_palette("viridis")  # Or "plasma", "cividis", etc.

# Change DPI
plt.savefig(output_file, dpi=600)  # Higher = better quality
```

## For Paper Writing

### Key Files for Paper

1. **Method section**: Use `METHODOLOGY.md` as template
2. **Results section**: Use `reports/analysis_report.txt` and visualizations
3. **Tables**: Use `reports/*.tex` for LaTeX tables
4. **Figures**: Use `figures/*.png` (300 DPI, suitable for publication)

### Statistics to Report

From `reports/statistics.json`:
- Total modules analyzed
- Skills extracted
- Distribution metrics
- Bloom's taxonomy levels

### Example Results Text

```
We analyzed X modules from UCD's Computer Science program, extracting
Y distinct skills from Z learning outcomes. The LLM-generated taxonomy
identified N domains, with skills distributed across M sub-categories.
The most common skill category was [Technical/Cognitive/...] (P%),
followed by [category] (Q%). Analysis of Bloom's taxonomy levels
showed that R% of skills were at the "Apply" level or higher,
indicating emphasis on higher-order thinking.
```

## Next Steps

1. **Validate results**: Manually review a sample of extracted skills
2. **Refine taxonomy**: Adjust LLM prompts if needed
3. **Generate figures**: Use visualizations in your paper
4. **Write methods**: Adapt `METHODOLOGY.md` to your paper format
5. **Analyze patterns**: Look for interesting findings in the data

## Getting Help

- Check `README.md` for full documentation
- Review code comments in `src/` directory
- Examine example outputs in generated directories
- Read `METHODOLOGY.md` for research context

## Cost Estimate

Approximate API costs (as of 2025):
- Claude 3.5 Sonnet: ~$3-15 per 100 modules
- Depends on: number of learning outcomes, response length
- Use `--skip-taxonomy` flag to avoid re-running LLM if you already have results

## Pro Tips

1. **Start small**: Test with 5-10 modules before full run
2. **Cache results**: The pipeline saves intermediate outputs - use skip flags!
3. **Version control**: Commit after each major step
4. **Backup API key**: Store securely, don't commit to git
5. **Document changes**: Keep notes on any prompt modifications
6. **Validate early**: Review first few extractions before processing all modules

Enjoy building your taxonomy! 🎓
