---
name: vector-gene
description: "Personal genomics: patient template + 40 science skills."
version: 2.0.0
author: Osmosy
based_on: google-deepmind/science-skills (Apache-2.0) + Rai220/my-health-public
tags: [genomics, personal-health, variants, alphagenome, clinvar, gnomad]
---

# Vector Gene — Personal Genomics with AI Agents

Второй слой поверх коллекции научных навыков Google DeepMind. Шаблон данных
пациента + доступ к реальным научным базам и моделям вместо эрудиции модели.

## Когда использовать

- Пользователь принёс файл генетического теста (23andMe, Genotek, Atlas, WGS/WES/VCF)
- Нужна аннотация варианта: что о нём известно клинически (ClinVar), как часто
  встречается (gnomAD), где ген экспрессируется (GTEx), что рядом регуляторного
  (ENCODE), как предсказано функциональное влияние (AlphaGenome AVI)
- Фармакогенетика: CYP2C9/CYP2C19/VKORC1/CYP4F2 и другие гены метаболизма —
  **ручная сверка с PharmGKB/CPIC; отдельного навыка в коллекции нет**
- Проверка лабораторного отчёта по сырым данным

## Когда НЕ использовать

- **Клинические вопросы.** Диагнозы, назначения, интерпретация для лечения — не сюда.
  Навыки AlphaGenome прямо запрещают клиническое применение (Research Use Only),
  и агент обязан ответить, что это исследовательский инструмент.
- **Соматические мутации в опухолях** — это COSMIC, не gnomAD (правило из самого
  gnomad_database: «не использовать для соматических мутаций в раке»).
- **Поиск гомологов** — protein_sequence_similarity_search, не MSA.
- **Структурный поиск по последовательности** — нужен файл координат (.cif/.pdb),
  имя гена не подойдёт (foldseek_structural_search).
- **Нет идентификатора, только имя гена** — сначала получить UniProt ID
  (uniprot_database), потом AlphaFold.

## Структура

```
skills/science/            — 40 навыков Google DeepMind (Apache-2.0), вендор-копия
  alphagenome_*            — 3 навыка: AVI-скоры, анализ варианта, deep-links в Atlas
  clinvar / gnomad / dbsnp / gtex / encode / ucsc / unibind / jaspar / ensembl
  alphafold / pdb / foldseek / uniprot / interpro / string / hpa / msa / protein_sequence_similarity_search / pymol
  chembl / pubchem / openfda / opentargets / clinical_trials
  pubmed / europepmc / openalex / arxiv / biorxiv
  reactome / quickgo / embl_ebi_ols / ncbi_sequence_fetch / predictingthepast
  uv / credentials / workflow_skill_creator   — служебный слой
docs/upstream/             — лицензии и README апстрима (Apache-2.0 + SKILL_LICENSES)
docs/archive/              — прежняя версия этого файла (v1, 28.06.2026)
docs/vector-gene.architecture.html  — живая диаграмма (GitHub Pages)
data/patient/              — OKF-шаблон данных пациента (синтетический)
```

## Как запускать научные навыки

Все скрипты навыков запускаются только через `uv run` — системный Python не имеет
нужных библиотек. Служебный навык `skills/science/uv/` отвечает за установку и PATH.
Секреты проверяются протоколом `skills/science/credentials/` — наличие ключа
проверяется кодом возврата (`grep -sq`), значение в контекст не попадает.

Ключи пишутся в `~/.env` — редактором или через `read -s`, а не `echo "KEY=..." >> ~/.env`
(значение попадает в историю shell):

```bash
# откройте ~/.env в редакторе и добавьте строку:
#   ALPHAGENOME_API_KEY=...
chmod 600 ~/.env
```

- `ALPHAGENOME_API_KEY` — обязателен для трёх alphagenome-навыков
- `OPENALEX_API_KEY` — обязателен для literature_search_openalex
- `USER_EMAIL` — **обязателен для `protein_sequence_msa`** (EBI без него отказывает);
  используется также `protein_sequence_similarity_search`, `pubmed_database`
  и как запасной адрес для `clinvar_database`
- `NCBI_API_KEY` — опционально, 10 req/s вместо 3; `NCBI_EMAIL` и `NCBI_TOOL` —
  идентификация клиента для автоматических запросов к NCBI (`clinvar_database`)
- `FDA_API_KEY` — опционально, выше лимит openFDA
- `ALPHAGENOME_GTF_PATH` — внутренняя: путь к локальному GTF, если он не скачан;
  `SSL_CERT_FILE` читается HTTP-клиентом навыков, отдельно задавать не нужно

ClinVar, dbSNP, PubMed, openFDA, NCBI работают без ключа, но с лимитами частоты.

## Пайплайн: сырые данные → варианты → аннотация

```bash
# Инструменты внешние (в коллекции навыков их нет):
#   conda install -c bioconda fastqc bwa samtools bcftools
# 0. Индексы референса (один раз)
bwa index ref/hg38.fa
samtools faidx ref/hg38.fa
# 1. QC
fastqc raw/*.fastq.gz -o qc/
# 2. Выравнивание. Read group обязателен, иначе mpileup/GATK дадут некорректный результат.
#    collate + fixmate -m обязательны: markdup берёт теги MC/ms, которые ставит fixmate.
bwa mem -t 8 -R '@RG\tID:sample\tSM:sample\tPL:ILLUMINA' ref/hg38.fa \
    raw/sample_R1.fastq.gz raw/sample_R2.fastq.gz \
  | samtools collate -O -u - \
  | samtools fixmate -m -u - - \
  | samtools sort -u - \
  | samtools markdup - aligned/sample.markdup.bam
# 3. Индекс
samtools index aligned/sample.markdup.bam
# 4. Вызов вариантов
bcftools mpileup -f ref/hg38.fa aligned/sample.markdup.bam | bcftools call -mv -o variants/sample.vcf
```

`-r` у `markdup` не используем: дубли помечаются, а не удаляются — иначе теряется
информация для оценки качества.

Проверено 2026-10-18 на фрагменте chr22 (100 кб, `wgsim -N 20000 -S 42`): цепочка
`bwa mem | collate | fixmate -m | sort | markdup` даёт 40 000 ридов, 100% mapped,
18 помеченных дублей и 111 вариантов в VCF (bwa 0.7.19, samtools 1.24, bcftools 1.24).
Воспроизводится: `bash scripts/smoke_pipeline.sh` — он сверяет все четыре числа
(включая долю mapped), фиксирует seed и `bwa mem -K 10000000`, чтобы результат не
зависел от `-t`, и отдельно проверяет, что без `collate`/`fixmate` тот же вход падает
с `samtools markdup: error, no ms score tag`.

Для WGS рекомендуемый путь — GATK/DeepVariant; это минимальный пример для панели/WES.

Аннотацию делает агент навыками, а не сам: `dbsnp_database` (rsID → координаты) →
`clinvar_database` → `gnomad_database` → `alphagenome_*` → `gtex_database` →
`encode_ccres_database`.
Для 23andMe/Genotek (готовые SNP-таблицы) шаги 1–4 не нужны, начинается сразу с аннотации.

Сквозные цепочки, которые коллекция держит намеренно:

```
dbSNP → ClinVar → gnomAD → AlphaGenome → GTEx → ENCODE      (некодирующий вариант)
UniProt → InterPro → AlphaFold → Foldseek → STRING → PyMOL   (незнакомый белок)
Open Targets → ChEMBL → ClinicalTrials → openFDA → PubMed    (терапевтическая мишень)
```

## Правило интерпретации (из alphagenome_single_variant_analysis)

Высокий квантиль сам по себе ничего не значит. Обязательна сверка с сырым баллом:

| квантиль | сырой балл | что это значит |
|---|---|---|
| высокий ~0.99 | низкий ~0.01 | ложная тревога: артефакт низкой дисперсии фона |
| высокий 0.998 | низкий ~0.01 | тот же артефакт + механизм вне области модели |
| низкий <0.1 | низкий <0.1 | честное отсутствие сигнала |

Формулировка вывода в первом и втором случае — «значимого молекулярного эффекта
AlphaGenome не предсказывает», а не поиск объяснения. Готовые разборы лежат в
`skills/science/alphagenome_single_variant_analysis/docs/examples/` (шесть кейсов:
отрицательные результаты и границы модели).

Поля двух навыков не взаимозаменяемы. У AVI `avi_quantile` — **хвостовой** квантиль
(1 − CDF): меньше значит сильнее, `avi_phred = −10·log10(avi_quantile)`, так что
0.0012 ≈ Phred 29.2, а 0.99 — обычный вариант (Phred ≈ 0.04). У
`alphagenome_single_variant_analysis` поле `quantile_score` знаковое: чем ближе к ±1,
тем сильнее (критерий `|quantile_score| > 0.995`).

Отдельно: для snRNA/tRNA/rRNA модель не симулирует посттранскрипционную укладку —
при анализе таких генов это надо оговаривать явно (кейс RNU4ATAC).

## Данные пациента (OKF-шаблон)

```
data/patient/
├── SUMMARY.md HISTORY.md MEASUREMENTS.md MEDS.md PROBLEMS.md
├── TESTS.md VISITS.md HYPOTHESES.md QUESTIONS.md TREATMENT_PLAN.md TODO.md
├── genetic/raw/  genetic/variants.md  genetic/analysis.md
├── drugs/responses.md
└── reports/
```

В репозиторий кладутся только **синтетические** данные. Реальные данные пациента
не коммитятся никогда.

## Ограничения (знать до запуска)

- **AlphaGenome — Research Use Only.** Выводы только как гипотезы; клиническое
  применение запрещено условиями доступа к API.
- **WGS требует ресурсов.** ~100 ГБ FASTQ, выравнивание на hg38 — не «за часы» на
  ноутбуке; реально считать на 23andMe/VCF или на внешнем вычислителе.
- **AlphaMissense без API.** Публичного API нет: только веса модели или precomputed
  база (~1 ГБ). Строка «API или precomputed database» — только второе. При этом вклад
  AlphaMissense виден внутри AVI (`top_modality`, `fi_ALPHAMISSENSE` при
  `--include_features`); это модальность AVI, а не отдельный скор AlphaMissense.
- **Навыки — обёртки над внешними API.** Недоступность базы или смена её API ломает
  навык, и агент не всегда это замечает сразу.
- **Сторонние данные под своими лицензиями.** Код навыков Apache-2.0, но у источников
  (GTEx, HPA, Reactome, Open Targets, UniProt/EMBL-EBI, RCSB, UCSC, NCBI) свои условия
  с требованием атрибуции. См. `docs/upstream/science-skills-SKILL_LICENSES.md`.
- **Личные данные и чужие сервисы.** Загрузка генома в облачную LLM может противоречить
  соглашению лаборатории; локальный агент от этого свободен.

## Приватность

- **Локально:** файлы пациента в `data/patient/`, markdown; в репозиторий не попадают.
- **Наружу:** запросы навыков к внешним базам (ClinVar/NCBI, gnomAD, GTEx, ENCODE,
  UCSC, Ensembl, UniProt, PDB, AlphaFold DB, ChEMBL, PubChem, openFDA, Open Targets,
  ClinicalTrials.gov, PubMed/Europe PMC/OpenAlex/arXiv/bioRxiv, Reactome, QuickGO, OLS,
  Foldseek/BLAST) содержат rsID, координаты варианта или последовательность. Прямые
  идентификаторы (имя, документы, файл целиком) в запрос не включаются.
- **Это не отменяет персональности.** Генетические данные — особая категория
  (GDPR ст. 9, 152-ФЗ): набор редких вариантов может указать на человека. Запрашивать
  по одному варианту, не сливать весь список в один сервис, помнить про логи сервиса.
- **AlphaGenome:** вариант уходит в Google по API-ключу; ключ — в `~/.env` (chmod 600),
  проверка через `credentials`, значение в контекст модели не попадает.
- Агент — локальный или с политикой нулевого хранения.
- Выводы — гипотезы, требующие проверки врачом; назначения по ним не делаются.

## Ссылки

- Навыки: [google-deepmind/science-skills](https://github.com/google-deepmind/science-skills) (Apache-2.0)
- AlphaGenome Atlas: [deepmind.google.com/science/alphagenome/atlas](https://deepmind.google.com/science/alphagenome/atlas)
- Основание шаблона: [Rai220/my-health-public](https://github.com/Rai220/my-health-public)
- Базы: [ClinVar](https://www.ncbi.nlm.nih.gov/clinvar/) · [gnomAD](https://gnomad.broadinstitute.org/) · [dbSNP](https://www.ncbi.nlm.nih.gov/snp/) · [GTEx](https://gtexportal.org/) · [PharmGKB](https://www.pharmgkb.org/)
- DeepMind AlphaMissense: [github.com/google-deepmind/alphamissense](https://github.com/google-deepmind/alphamissense)

> Выводы агента — гипотезы для обсуждения с врачом, не медицинские назначения.
> Реальные данные пациента никогда не загружаются в репозиторий.
