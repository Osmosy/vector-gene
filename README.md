<div align="center">

<img src="assets/vector-logo.png" alt="Vector Gene" width="200"/>

# Vector Gene

[![Architecture: live](https://img.shields.io/badge/Architecture-live_diagram-4f8ff7.svg)](https://osmosy.github.io/vector-gene/docs/vector-gene.architecture.html)

**Личная геномика с AI-агентами: шаблон данных пациента + 40 научных навыков Google DeepMind**

[![Hermes Agent](https://img.shields.io/badge/Hermes-Agent-blue.svg)](https://github.com/NousResearch/hermes-agent)
[![Ecosystem: Vector](https://img.shields.io/badge/Ecosystem-Vector-blue.svg)](https://osmosy.github.io/)
[![Skills: 40](https://img.shields.io/badge/Skills-40-orange.svg)](skills/science)
[![Databases: 30+](https://img.shields.io/badge/Databases-30%2B-green.svg)](#навыки)
[![Source: Google DeepMind](https://img.shields.io/badge/Source-Google%20DeepMind-blueviolet.svg)](https://github.com/google-deepmind/science-skills)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-yellow.svg)](LICENSE)

**Документация:** [Навыки](#навыки) · [Архитектура (live)](https://osmosy.github.io/vector-gene/docs/vector-gene.architecture.html) · [Ограничения](#ограничения)

</div>

---

Личная геномика силами одного человека и AI-агента. Структурированные данные в Markdown
+ 40 доменных навыков, которые ходят в реальные научные базы и модели, + агент как слой
рассуждений. Файлы пациента хранятся локально; наружу уходят только запросы к базам
(варианты, rsID, последовательности) — без персональных данных.

Второй слой — коллекция [Science Skills](https://github.com/google-deepmind/science-skills)
от Google DeepMind (Apache-2.0), вендорится в `skills/science/`: 40 навыков, 66 Python-скриптов,
8334 строки инструкций. Аналитика берётся оттуда, а не изобретается заново.

## Архитектура

```
Данные пациента (OKF, локально)
  data/patient/*.md, genetic/raw/, drugs/responses.md
        │
        ▼
Hermes Agent — слой рассуждений
        │
        ├── ГЕНОМИКА   clinvar · gnomad · dbsnp · gtex · encode · ucsc · unibind · jaspar · ensembl
        ├── МОДЕЛИ     alphagenome ×3 (AVI-скоры, анализ варианта, deep-links в Atlas)
        ├── БЕЛКИ      alphafold · pdb · foldseek · uniprot · interpro · string · hpa · msa · pymol
        ├── ХИМИЯ      chembl · pubchem · openfda · opentargets · clinical_trials
        ├── ЛИТЕРАТУРА pubmed · europepmc · openalex · arxiv · biorxiv
        └── СЛУЖЕБНЫЕ  uv · credentials · workflow_skill_creator
        │
        ▼
Гипотезы для врача (никогда — диагнозы)
```

Полная живая диаграмма: [docs/vector-gene.architecture.html](docs/vector-gene.architecture.html)

## Навыки

40 навыков в `skills/science/`, сгруппированы по домену. Каждый — каталог с `SKILL.md`,
`scripts/` и `references/`; зависимости объявляются на уровне навыка.

| Группа | Навыков | Что закрывает |
|--------|---------|---------------|
| Геномика и варианты | 12 | AlphaGenome ×3, ClinVar, dbSNP, gnomAD, Ensembl, GTEx, ENCODE, UCSC, UniBind, JASPAR |
| Белки и структуры | 10 | AlphaFold DB, PDB, Foldseek, UniProt, InterPro, STRING, HPA, MSA, поиск гомологов, PyMOL |
| Химия, лекарства, клиника | 5 | ChEMBL, PubChem, openFDA, Open Targets, ClinicalTrials.gov |
| Литература | 5 | PubMed, Europe PMC, OpenAlex, arXiv, bioRxiv/medRxiv |
| Пути и онтологии | 3 | Reactome, QuickGO, EMBL-EBI OLS |
| Последовательности | 1 | NCBI sequence fetch |
| Гуманитарные науки | 1 | PredictingThePast (Aeneas, Ithaca — древние тексты) |
| Инфраструктура | 3 | uv, credentials, workflow_skill_creator |

## Пайплайн

```
FASTQ → fastqc → bwa mem (hg38) → samtools sort → bcftools call
      → ClinVar / gnomAD / dbSNP / GTEx / ENCODE → AlphaGenome
```

Для готовых SNP-таблиц (23andMe, Genotek, Atlas) первые шаги не нужны — аннотация
начинается сразу. Сквозные цепочки, которые коллекция держит намеренно:

- `dbSNP → ClinVar → gnomAD → AlphaGenome → GTEx → ENCODE` — некодирующий вариант
- `UniProt → InterPro → AlphaFold → Foldseek → STRING → PyMOL` — незнакомый белок
- `Open Targets → ChEMBL → ClinicalTrials → openFDA → PubMed` — терапевтическая мишень

## Правило интерпретации

Высокий квантиль без проверки магнитуды — ловушка. Квантиль 0.99 при сыром балле 0.01
означает «значимого молекулярного эффекта не предсказано», а не находку. Три из шести
готовых кейсов в `alphagenome_single_variant_analysis` — отрицательные результаты и
границы модели. Подробнее — в [SKILL.md](SKILL.md#правило-интерпретации-из-alphagenome_single_variant_analysis).

## Быстрый старт

```bash
git clone https://github.com/Osmosy/vector-gene.git && cd vector-gene

# Научные скрипты работают только через uv (системный Python не подходит)
npx skills add google-deepmind/science-skills/     # либо использовать вендор-копию skills/science/

# Ключи — только для части навыков
echo "ALPHAGENOME_API_KEY=..." >> ~/.env    # обязателен для трёх alphagenome-навыков
echo "OPENALEX_API_KEY=..." >> ~/.env       # обязателен для literature_search_openalex
```

ClinVar, dbSNP, PubMed, openFDA, NCBI работают без ключа, но с лимитами частоты.
Опционально: `NCBI_API_KEY` (10 запросов/с вместо 3), `NCBI_EMAIL`/`NCBI_TOOL` —
идентификация клиента в запросах к NCBI (требование их политики для автоматических обращений).
Проверка ключа идёт протоколом `skills/science/credentials/` — значение в контекст
модели не попадает.

## Ограничения

- **AlphaGenome — Research Use Only.** Клиническое применение запрещено условиями
  доступа к API; выводы только как гипотезы.
- **WGS требует ресурсов** (~100 ГБ FASTQ и выравнивание на hg38) — на ноутбуке
  реалистично считать 23andMe/VCF, а не полный геном.
- **AlphaMissense без публичного API** — только веса модели или precomputed-база.
- **Навыки — обёртки над внешними API**: недоступность базы ломает навык.
- **У источников данных свои лицензии** (GTEx, HPA, Reactome, Open Targets, UniProt,
  RCSB, UCSC, NCBI) — с требованием атрибуции. См. [docs/upstream/](docs/upstream/).

## Приватность

- **Файлы пациента остаются на машине.** `data/patient/` — локальный markdown;
  реальные данные в репозиторий не коммитятся, в шаблонах только синтетика.
- **Наружу уходят запросы к базам.** Навыки обращаются к ClinVar/NCBI, gnomAD, GTEx,
  ENCODE, UCSC, Ensembl, UniProt, PDB, AlphaFold DB, ChEMBL, PubChem, openFDA,
  Open Targets, ClinicalTrials.gov, PubMed/Europe PMC/OpenAlex/arXiv/bioRxiv,
  Reactome, QuickGO, OLS, Foldseek/BLAST. В запросе — rsID, координаты варианта или
  последовательность; имя, документы и файл целиком не отправляются.
- **AlphaGenome — отдельный случай.** Вариант (последовательность и координаты)
  уходит в Google по API-ключу; ключ хранится в `~/.env` (права 600) и в контекст
  модели не попадает — проверка через `skills/science/credentials/`.
- Выводы агента — гипотезы для врача, не назначения.

## Источник

Аналитический слой — [google-deepmind/science-skills](https://github.com/google-deepmind/science-skills)
(Apache-2.0), вендорится в `skills/science/` с сохранением лицензии и файла условий
`SKILL_LICENSES.md`. Шаблон данных пациентов основан на
[Rai220/my-health-public](https://github.com/Rai220/my-health-public).

> Выводы агента — гипотезы для обсуждения с врачом, не медицинские назначения.
> Реальные данные пациента никогда не загружаются в репозиторий.
