# Methodology for Academic Paper

## Research Question

**Can Large Language Models automatically generate meaningful taxonomies of learning outcomes and skills from university module descriptors?**

## Hypothesis

LLMs can effectively:
1. Extract structured skill information from unstructured learning outcome text
2. Categorize skills using established frameworks (Bloom's taxonomy, skill categories)
3. Generate hierarchical taxonomies that align with domain expert knowledge
4. Provide consistent and reproducible classifications

## Dataset

### Source
- **Institution**: University College Dublin (UCD)
- **Department**: Computer Science (COMP modules)
- **Data Type**: Publicly available module descriptors
- **Access**: Web-based module directory (https://hub.ucd.ie/usis/)

### Data Collection
1. **Automated Scraping**: Python-based web scraper
2. **Extraction Points**:
   - Module code and title
   - Learning outcomes (primary focus)
   - Module description
   - Assessment methods
   - Module level (1-4)
   - Credit value

3. **Data Quality**:
   - Only modules with explicit learning outcomes included
   - Manual validation of scraping accuracy (sample-based)

## LLM-Based Processing Pipeline

### Phase 1: Skill Extraction

**Model**: Claude 3.5 Sonnet (Anthropic)
**Temperature**: 0.3 (lower for consistency)

**Process**:
1. For each module's learning outcomes, construct prompt with:
   - Module context (title, level, description)
   - All learning outcome statements
   - Structured extraction request

2. LLM extracts for each outcome:
   - **Skill name**: Specific competency
   - **Description**: Brief elaboration
   - **Category**: Technical | Cognitive | Interpersonal | Domain-Specific
   - **Skill type**: Fine-grained classification (e.g., "Programming", "Analysis")
   - **Bloom's level**: Remember | Understand | Apply | Analyze | Evaluate | Create
   - **Keywords**: Relevant terms for retrieval

3. Output format: Structured JSON for programmatic analysis

### Phase 2: Taxonomy Generation

**Model**: Claude 3.5 Sonnet (Anthropic)
**Temperature**: 0.5 (higher for creative organization)

**Process**:
1. Aggregate all extracted skills across all modules
2. Prompt LLM to organize into hierarchical taxonomy:
   - **Level 1**: Domains (broad skill areas)
   - **Level 2**: Sub-categories (related skill groups)
   - **Level 3**: Individual skills
   - **Metadata**: Proficiency levels, module associations

3. Handle redundancy through consolidation
4. Output: Hierarchical JSON structure

## Validation Methods

### 1. Internal Consistency
- Cross-module skill alignment
- Bloom's taxonomy level progression across module levels
- Category distribution reasonableness

### 2. Structural Analysis
- Taxonomy depth and breadth
- Skill distribution across domains
- Coverage completeness

### 3. Manual Validation (Recommended)
- Domain expert review of sample classifications
- Inter-rater reliability on skill categorizations
- Comparison with curriculum documentation

### 4. Quantitative Metrics
- **Skill density**: Skills per learning outcome
- **Taxonomy balance**: Distribution across branches
- **Level progression**: Correlation between module level and Bloom's level
- **Consistency**: Repeated runs produce similar results

## Reproducibility

### Ensures Reproducibility Through:
1. **Code availability**: All source code provided
2. **Version control**: Git repository with full history
3. **Dependency management**: requirements.txt with pinned versions
4. **Data provenance**: URLs and timestamps of scraped data
5. **Prompt templates**: Exact LLM prompts documented in code
6. **Seed setting**: Where applicable for deterministic behavior
7. **Output preservation**: All intermediate and final outputs saved

### Limitations to Reproducibility:
- **LLM non-determinism**: Even at low temperature, LLM outputs may vary slightly
- **Data currency**: Module descriptors may change over time
- **API changes**: Anthropic API may update model versions

## Analysis Outputs

### Quantitative Results
- Summary statistics (counts, distributions)
- Cross-tabulations (level × category, level × Bloom's)
- Frequency analyses

### Qualitative Results
- Hierarchical taxonomy structure
- Representative examples of skill extraction
- Domain categorization

### Visualizations
- Distribution bar charts
- Progression analyses
- Taxonomy network graphs
- Heatmaps of skill-module associations

## Limitations

### Data Limitations
1. Single institution (UCD)
2. Single discipline (Computer Science)
3. Reliance on quality of written learning outcomes
4. No ground truth for "correct" taxonomy
5. Limited to publicly available data

### Methodological Limitations
1. LLM prompt engineering impact
2. Potential biases in LLM training data
3. Subjective interpretation of skill boundaries
4. No validation against student performance data (yet)
5. Language-specific (English only)

### Scope Limitations
1. Proof-of-concept only
2. No student outcomes analysis
3. No longitudinal tracking
4. No cross-institutional comparison

## Future Research Directions

### Immediate Extensions
1. **Multi-institutional**: Compare across universities
2. **Multi-disciplinary**: Apply to other fields
3. **Validation study**: Expert panel review
4. **Inter-rater reliability**: Multiple human coders vs. LLM

### Long-term Applications
1. **Student trajectory analysis**: Link to grades and performance
2. **Curriculum optimization**: Identify gaps and redundancies
3. **Personalized learning**: Skill-based recommendations
4. **Predictive modeling**: Forecast student success
5. **Job market alignment**: Compare to industry skill demands

## Ethical Considerations

### Data Ethics
- Only public data used
- No student personal information
- Institutional data usage respects terms of service

### AI Ethics
- Transparency about LLM use
- Human oversight maintained
- Limitations clearly stated
- Not replacing human expertise, augmenting it

### Educational Context
- Tool for analysis, not student evaluation
- Supports educators, doesn't replace them
- Maintains academic integrity standards

## Contribution to Field

### Novel Aspects
1. **Automation**: First (to our knowledge) fully automated taxonomy generation from module descriptors
2. **Scalability**: Can process hundreds of modules rapidly
3. **Structured output**: Machine-readable taxonomies for further analysis
4. **Multi-framework**: Combines skill categories with Bloom's taxonomy
5. **Open methodology**: Fully documented and reproducible

### Academic Significance
- Demonstrates practical application of LLMs in education research
- Provides foundation for data-driven curriculum analysis
- Enables large-scale comparative studies
- Opens pathway to skill-based student analytics

## Publication Strategy

### Target Venues
- **Primary**: Education technology conferences (e.g., Learning Analytics and Knowledge, Educational Data Mining)
- **Secondary**: AI in education workshops
- **Tertiary**: Higher education research journals

### Paper Sections (Typical Structure)
1. **Abstract**: Problem, method, results, implications
2. **Introduction**: Motivation and research question
3. **Related Work**: Curriculum analysis, LLMs in education
4. **Methodology**: This document's content
5. **Results**: Statistics, visualizations, examples
6. **Discussion**: Validation, limitations, implications
7. **Future Work**: Extensions and applications
8. **Conclusion**: Summary and contribution

### Supplementary Materials
- Full dataset (if permissible)
- Complete taxonomy output
- Source code repository
- Extended visualizations

## Timeline Estimate

For proof-of-concept paper:

1. **Data collection**: 1-2 hours (automated scraping)
2. **LLM processing**: 2-4 hours (depends on module count and API rate limits)
3. **Analysis and visualization**: 2-3 hours (automated generation)
4. **Manual validation**: 4-8 hours (sample-based expert review)
5. **Paper writing**: 20-40 hours (depending on venue requirements)

**Total**: Approximately 1-2 weeks of work

## Acknowledgment Template

```
This research utilized Claude (Anthropic) for automated skill extraction
and taxonomy generation. Module data was sourced from University College
Dublin's public course directory. We thank [domain experts] for validation
assistance.
```

## Keywords for Paper

- Learning outcomes
- Skill taxonomy
- Large language models
- Curriculum analysis
- Educational data mining
- Bloom's taxonomy
- Higher education
- Computer science education
- Automated content analysis
- AI in education
