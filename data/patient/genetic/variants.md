# variants — SYNTHETIC

> **SYNTHETIC.** Вымышленные варианты; координаты условны.
> Зиготность записывается аллелями (`G/A`, `A/A`), а не словами вида «гомозигота
> по референсу»: важно, какой аллель референсный, а какой — вариант.

| Ген | Вариант (HGVS) | rsID | Генотип | Источник данных |
|-----|----------------|------|---------|-----------------|
| LDLR | NM_000527.5:c.682G>A (p.Glu228Lys) | rs121908029 | G/A | синтетическая таблица 23andMe-подобного формата |
| CYP2C19 | *2 (NM_000769.4:c.681G>A) | rs4244285 | *1/*2 | синтетическая таблица |
| VKORC1 | c.-1639G>A | rs9923231 | A/A | синтетическая таблица |

Сверка rsID с базами (2026-10-18):

- `rs121908029` — LDLR `NM_000527.5:c.682G>A` (`p.Glu228Lys`), ClinVar VCV000003691,
  Pathogenic, reviewed by expert panel. В первой версии шаблона стояло `c.1775G>A`
  (`p.Gly592Glu`) — это другой вариант, к этому rsID он не относится.
- `rs4244285` — CYP2C19 `NM_000769.4:c.681G>A` (*2).
- `rs9923231` — VKORC1 `c.-1639G>A`: референсный аллель G, вариант A.
  Генотип `A/A` — гомозигота по варианту, повышенная чувствительность к варфарину.

Чем именно проверено (прогон 2026-10-18, `uv run` сам ставит зависимости скрипта):

```bash
# ген и тип варианта
uv run skills/science/dbsnp_database/scripts/dbsnp_cli.py get-variant rs121908029 \
  --output /tmp/rs121908029.json
# ClinVar: rsID -> ID вариантов, затем ID -> значимость, звёзды, HGVS
uv run skills/science/clinvar_database/scripts/clinvar_api.py search \
  --query "rs121908029" --output /tmp/cv_search.json
uv run skills/science/clinvar_database/scripts/clinvar_api.py summary \
  --variant_ids 3691 --output /tmp/cv_summary.json
```

Что вернули навыки: `search` — 3 записи `251393, 226333, 3691`; `summary(3691)` —
Pathogenic, `reviewed by expert panel`, `NM_000527.5(LDLR):c.682G>A (p.Glu228Lys)`,
phenotype «Hypercholesterolemia, familial, 1». `dbsnp_cli` для трёх rsID дал гены
LDLR / CYP2C19 / VKORC1 соответственно.

Сырые файлы (FASTQ/VCF/таблицы) кладутся в `genetic/raw/` и не коммитятся.
