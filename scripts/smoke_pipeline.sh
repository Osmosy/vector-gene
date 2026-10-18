#!/usr/bin/env bash
# Smoke-тест пайплайна из SKILL.md: FASTQ -> выровненный BAM -> VCF.
#
# Проверяет две вещи:
#   1. цепочка bwa mem | collate | fixmate -m | sort | markdup работает и даёт те же
#      счётчики, что указаны в SKILL.md;
#   2. без collate/fixmate та же команда падает с «no ms score tag» — это и есть
#      причина, по которой шаги обязательны.
#
# Референс не хранится в репозитории: скрипт берёт фрагмент chr22 (hg38, 100 кб)
# через UCSC API. Риды генерируются wgsim с фиксированным seed, поэтому счётчики
# воспроизводимы для указанных версий инструментов.
#
# Требуется: curl, python3, bwa, samtools, bcftools, wgsim (bioconda).
# Проверено на bwa 0.7.19, samtools 1.24, bcftools 1.24, wgsim 1.0 (bioconda,
# сборка h577a1d6_10: бинарник печатает «Version: 1.24» — это версия htslib внутри неё).
#
# Использование:  bash scripts/smoke_pipeline.sh [каталог]
# Выход: 0 — счётчики совпали, 1 — расхождение или падение.

set -euo pipefail

WORK="${1:-$(mktemp -d "${TMPDIR:-/tmp}/vg-smoke.XXXXXX")}"
CHROM="chr22"
START=20000000
END=20100000
PAIRS=20000
SEED=42
THREADS="${THREADS:-4}"

# Ожидаемые значения при этих параметрах (bwa 0.7.19, samtools 1.24, bcftools 1.24).
EXP_TOTAL=40000
EXP_MAPPED=40000
EXP_MAPPED_PCT=100.00
EXP_DUP=18
EXP_VARIANTS=111

need() {
  command -v "$1" >/dev/null 2>&1 || { echo "нет в PATH: $1 (нужен bioconda: bwa samtools bcftools wgsim)" >&2; exit 2; }
}
for tool in curl python3 bwa samtools bcftools wgsim; do need "$tool"; done

mkdir -p "$WORK"/{ref,raw,aligned,variants}
cd "$WORK"

echo "== версии =="
samtools --version | head -1
bcftools --version | head -1
bwa 2>&1 | grep -m1 '^Version' || true

echo "== референс: $CHROM:$START-$END (hg38, UCSC API) =="
# UCSC — внешняя точка: три попытки, иначе сетевой сбой выглядел бы как ошибка пайплайна.
fetch_ref() {
  local attempt
  for attempt in 1 2 3; do
    if curl -sf "https://api.genome.ucsc.edu/getData/sequence?genome=hg38;chrom=${CHROM};start=${START};end=${END}" -o ref.json; then
      return 0
    fi
    echo "UCSC API не ответил (попытка $attempt), повтор через 5 с" >&2
    sleep 5
  done
  return 1
}
fetch_ref || { echo "не удалось получить референс с UCSC API" >&2; exit 1; }
python3 -c "import json,sys; s=json.load(open('ref.json'))['dna'].upper(); print('>%s_%s_%s' % ('$CHROM','$START','$END')); [print(s[i:i+60]) for i in range(0,len(s),60)]" \
  > ref/frag.fa
[ -s ref/frag.fa ] || { echo "пустой референс" >&2; exit 1; }

bwa index ref/frag.fa >/dev/null 2>&1
samtools faidx ref/frag.fa

echo "== риды: wgsim -N $PAIRS, seed $SEED =="
wgsim -N "$PAIRS" -1 150 -2 150 -e 0.001 -S "$SEED" ref/frag.fa raw/r1.fastq raw/r2.fastq >/dev/null 2>&1

echo "== конвейер из SKILL.md =="
bwa mem -t "$THREADS" -K 10000000 -R '@RG\tID:sample\tSM:sample\tPL:ILLUMINA' ref/frag.fa raw/r1.fastq raw/r2.fastq 2>/dev/null \
  | samtools collate -O -u - \
  | samtools fixmate -m -u - - \
  | samtools sort -u - \
  | samtools markdup - aligned/sample.markdup.bam
samtools index aligned/sample.markdup.bam
bcftools mpileup -f ref/frag.fa aligned/sample.markdup.bam 2>/dev/null \
  | bcftools call -mv -o variants/sample.vcf 2>/dev/null

FLAGSTAT=$(samtools flagstat aligned/sample.markdup.bam)
TOTAL=$(printf '%s\n' "$FLAGSTAT" | awk 'NR==1{print $1}')
MAPPED=$(printf '%s\n' "$FLAGSTAT" | grep -m1 ' mapped ' | awk '{print $1}')
MAPPED_PCT=$(printf '%s\n' "$FLAGSTAT" | grep -m1 ' mapped ' | sed -E 's/.*\(([0-9.]+)%.*/\1/')
DUP=$(printf '%s\n' "$FLAGSTAT" | grep -m1 'duplicates' | awk '{print $1}')
VARIANTS=$(grep -vc '^#' variants/sample.vcf || true)

echo "== результат =="
echo "ридов:      $TOTAL (ожидается $EXP_TOTAL)"
echo "mapped:     $MAPPED ($MAPPED_PCT%, ожидается $EXP_MAPPED / $EXP_MAPPED_PCT%)"
echo "дублей:     $DUP (ожидается $EXP_DUP)"
echo "вариантов:  $VARIANTS (ожидается $EXP_VARIANTS)"

STATUS=0
[ "$TOTAL" = "$EXP_TOTAL" ] || { echo "расхождение: риды" >&2; STATUS=1; }
[ "$MAPPED" = "$EXP_MAPPED" ] || { echo "расхождение: mapped" >&2; STATUS=1; }
[ "$MAPPED_PCT" = "$EXP_MAPPED_PCT" ] || { echo "расхождение: доля mapped ($MAPPED_PCT%)" >&2; STATUS=1; }
[ "$DUP" = "$EXP_DUP" ] || { echo "расхождение: дубли" >&2; STATUS=1; }
[ "$VARIANTS" = "$EXP_VARIANTS" ] || { echo "расхождение: варианты" >&2; STATUS=1; }

echo "== негативная проверка: без collate/fixmate =="
bwa mem -t "$THREADS" -K 10000000 -R '@RG\tID:sample\tSM:sample\tPL:ILLUMINA' ref/frag.fa raw/r1.fastq raw/r2.fastq 2>/dev/null \
  | samtools sort -o aligned/old.bam - 2>/dev/null
if samtools markdup -r aligned/old.bam aligned/old.markdup.bam 2>err.txt; then
  echo "ошибка: markdup прошёл без fixmate — ожидался отказ" >&2
  STATUS=1
elif grep -q 'no ms score tag' err.txt; then
  echo "OK: без fixmate markdup падает с «no ms score tag»"
else
  echo "неожиданная ошибка:" >&2; cat err.txt >&2; STATUS=1
fi

echo "== каталог прогона: $WORK =="
exit $STATUS
