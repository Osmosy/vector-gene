---
name: vector-gene
description: Personal genomics analysis with AI agents. Template for structured health data (OKF-style Markdown), agent-driven genomic analysis pipeline (FASTQ → variants → ClinVar/gnomAD → AlphaMissense), drug response prediction, and cross-patient comparison. Use when working with genetic test data (23andMe, Genotek, Atlas, WGS/WES), building personal health dashboards, or creating AI-powered medical second opinions.
based_on: Rai220/my-health-public — personal health record system with AI agent support
---

# Vector Gene — Personal Genomics with AI Agents

## Overview

Pattern for AI-driven personal genomics: structured health data in Markdown
+ domain tools (samtools, bcftools, AlphaMissense API) + AI agent as reasoning layer.

One person without bioinformatics training + AI agent = results comparable
to professional lab analysis, done in hours instead of months.

## Data Template (OKF-style)

```
patient/
├── SUMMARY.md          # One-page overview
├── HISTORY.md          # Medical history, timeline
├── MEASUREMENTS.md     # Vitals, lab results over time
├── MEDS.md             # Current and past medications
├── PROBLEMS.md         # Active health issues
├── TESTS.md            # Test results (blood, imaging, etc.)
├── VISITS.md           # Doctor visits log
├── HYPOTHESES.md       # Agent-generated hypotheses to verify
├── QUESTIONS.md        # Questions for doctor
├── TREATMENT_PLAN.md   # Current treatment plan
├── TODO.md             # Next steps
├── genetic/
│   ├── raw/            # FASTQ, VCF, 23andMe raw data
│   ├── variants.md     # Curated variant list
│   └── analysis.md     # Agent analysis output
├── drugs/
│   └── responses.md    # Drug response predictions
└── reports/            # Lab reports, scans (PDF)
```

## Genomic Analysis Pipeline

### Input Data Types

| Source | Format | Typical size |
|--------|--------|-------------|
| 23andMe/Genotek/Atlas | TXT/CSV, ~700K SNPs | ~25 MB |
| Whole Exome (WES) | FASTQ pair | ~8 GB |
| Whole Genome (WGS) | FASTQ pair | ~100 GB |

### Pipeline (agent-driven)

```bash
# 1. Quality control
fastqc raw/*.fastq.gz -o qc/

# 2. Alignment to reference genome
bwa mem -t 8 ref/hg38.fa raw/sample_R1.fastq.gz raw/sample_R2.fastq.gz | \
  samtools sort -o aligned/sample.bam

# 3. Variant calling
bcftools mpileup -f ref/hg38.fa aligned/sample.bam | \
  bcftools call -mv -o variants/sample.vcf

# 4. Annotation (agent does this via API/DB queries)
# - ClinVar: clinical significance
# - gnomAD: population frequency
# - dbSNP: known variant IDs
# - AlphaMissense: pathogenicity prediction for missense variants
```

### Agent Instructions (AGENTS.md)

```
Ты — AI-ассистент для анализа медицинских и генетических данных.
Работаешь с пациентом через Telegram/Hermes.

Принципы:
1. Объясняй медицинские термины простым языком
2. Выявляй скрытые взаимосвязи между показателями
3. Проверяй полноту обследований — что пропущено?
4. Для генетических вариантов: ClinVar → gnomAD → AlphaMissense
5. Формируй гипотезы, но всегда помечай их как «требует проверки врачом»
6. Для лекарств: проверяй фармакогенетику (CYP450 и другие гены метаболизма)
```

## Key Tools

### Genomics CLI (conda)
```bash
conda install -c bioconda bwa samtools bcftools fastqc
```

### Variant Databases (API/Web)
- ClinVar: https://www.ncbi.nlm.nih.gov/clinvar/
- gnomAD: https://gnomad.broadinstitute.org/
- dbSNP: https://www.ncbi.nlm.nih.gov/snp/

### AlphaMissense (DeepMind)
Predicts pathogenicity of missense variants using AlphaFold protein structure.
API or precomputed database: https://github.com/google-deepmind/alphamissense

### PharmGKB (Pharmacogenomics)
Drug-gene interactions: https://www.pharmgkb.org/

## Use Cases

### 1. Drug Response Prediction
```
Q: "Как на меня подействует варфарин?"
A: Проверяю VKORC1, CYP2C9, CYP4F2 → расчёт дозировки по генотипу
```

### 2. Cross-Patient Comparison
```
Q: "От кого ребёнок унаследовал непереносимость лактозы?"
A: Сравниваю MCM6 варианты родителей и ребёнка → ответ
```

### 3. RPG-Style Dashboard
Generate interactive HTML dashboard with genetic traits as "character stats":
- Class (based on genetic predispositions)
- Skills (cognitive, physical traits)
- Perks & Debuffs (beneficial and risk variants)
- Appearance (pigmentation genes)
- Biochemical pathways (dopamine, serotonin)

### 4. Lab Report Verification
Agent re-analyzes raw data from scratch, comparing against lab report.
Catches missed variants, outdated reference genomes, incomplete panels.

## Privacy & Ethics

- All data stays LOCAL (Markdown files, never uploaded)
- Agent runs on local model or API with zero-data-retention policy
- Results are HYPOTHESES — always verify with medical professional
- Never make treatment decisions based solely on agent output
- Template uses SYNTHETIC data — real patient data never committed

## References

- Rai220/my-health-public: https://github.com/Rai220/my-health-public
- AlphaMissense: https://github.com/google-deepmind/alphamissense
- ClinVar: https://www.ncbi.nlm.nih.gov/clinvar/
- gnomAD: https://gnomad.broadinstitute.org/
- PharmGKB: https://www.pharmgkb.org/
