# Vector Gene

[![Ecosystem: Vector](https://img.shields.io/badge/Ecosystem-Vector-blue.svg)](https://osmosy.github.io/)

![Vector Gene](assets/vector-logo.png)

**Vector Gene — личная геномика с AI-агентами.** Паттерн «структурированные данные + domain-инструменты + AI-агент»: один человек без биоинформатического образования + AI = результаты уровня лаборатории за часы, а не месяцы. OKF-шаблон данных, пайплайн FASTQ → выравнивание (hg38) → варианты → ClinVar/gnomAD → AlphaMissense, фармакогенетика (CYP450, VKORC1/CYP2C9). Всё локально, без загрузки данных.

## Что внутри

| Файл | Содержание |
|------|-----------|
| `SKILL.md` | Ядро: OKF-шаблон данных, пайплайн генома, AGENTS.md-инструкции, use cases, privacy |
| `assets/vector-logo.png` | Логотип Vector |

## Ключевые принципы

1. **Structured knowledge → agent → insights** — данные в Markdown (OKF), агент как слой рассуждений.
2. **С нуля, а не доверяя отчёту** — агент пересобирает анализ лаборатории по сырым данным и находит пропущенное.
3. **Всё локально** — никаких загрузок генетических данных, privacy-first.
4. **Гипотезы, а не диагнозы** — выводы агента всегда помечаются «требует проверки врачом».
5. **Синтетические данные в шаблонах** — реальные данные пациента никогда не коммитятся.

## Пайплайн

```
FASTQ → fastqc → bwa mem (hg38) → samtools sort → bcftools call
      → ClinVar / gnomAD / dbSNP / AlphaMissense
```

## Use Cases

- **Drug response prediction** — фармакогенетика: варфарин → VKORC1/CYP2C9/CYP4F2, дозировка по генотипу.
- **Cross-patient comparison** — наследование признаков (например, непереносимость лактозы → MCM6).
- **Lab report verification** — повторный анализ сырых данных, поиск пропущенных вариантов и устаревших референсов.
- **RPG-style dashboard** — интерактивный HTML с генетикой как «характеристиками персонажа».

## Основание

- based_on: [Rai220/my-health-public](https://github.com/Rai220/my-health-public) — personal health record system with AI agent support.
- Инструменты: [ClinVar](https://www.ncbi.nlm.nih.gov/clinvar/), [gnomAD](https://gnomad.broadinstitute.org/), [dbSNP](https://www.ncbi.nlm.nih.gov/snp/), [AlphaMissense](https://github.com/google-deepmind/alphamissense) (DeepMind), [PharmGKB](https://www.pharmgkb.org/).
- Экосистема Vector: github.com/Osmosy.

> ⚠️ Выводы агента — гипотезы для обсуждения с врачом, не медицинские назначения. Реальные данные пациента никогда не загружаются в репозиторий.
