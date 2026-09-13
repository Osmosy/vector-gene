# vector-gene — часть экосистемы Vector

Проект экосистемы Osmosy Vector на базе Hermes Agent.

Личная геномика: структурированные данные пациента в Markdown (OKF) + 40 научных
навыков Google DeepMind (ClinVar, gnomAD, GTEx, AlphaGenome, UniProt и другие),
вендоренных в `skills/science/`.

## Связанные проекты
- Хаб: https://github.com/Osmosy/vector-work
- Методология: https://github.com/Osmosy/vector-agent-ready
- Источник аналитического слоя: https://github.com/google-deepmind/science-skills (Apache-2.0)

## Для агентов
- Читай README.md первым, затем SKILL.md — там правила запуска и границы применимости
- Научные скрипты запускаются ТОЛЬКО через `uv run` (см. `skills/science/uv/`)
- Ключи ищутся в `~/.env` протоколом `skills/science/credentials/` — значение ключа
  не выводить и не читать в контекст
- AlphaGenome: выводы только как молекулярные гипотезы, клинические выводы запрещены
- В репозиторий кладётся только синтетика; реальные данные пациента не коммитятся
