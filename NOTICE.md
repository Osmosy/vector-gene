# Лицензии и источники

## Код и документация этого репозитория

Apache-2.0 — см. [LICENSE](LICENSE). Шаблон данных пациентов основан на
[Rai220/my-health-public](https://github.com/Rai220/my-health-public) (без лицензии
в апстриме — структура каталогов воспроизведена как идея, текст написан заново).

## Навыки в `skills/science/`

Вендорная копия [google-deepmind/science-skills](https://github.com/google-deepmind/science-skills),
Apache-2.0. Оригинальные файлы апстрима сохранены без изменений:

| Файл | Что это |
|------|---------|
| [science-skills-LICENSE.txt](upstream/science-skills-LICENSE.txt) | Apache License 2.0 (Copyright 2026 Google LLC) |
| [science-skills-SKILL_LICENSES.md](upstream/science-skills-SKILL_LICENSES.md) | условия использования сторонних баз (таблица «навык → URL») |
| [science-skills-README.md](upstream/science-skills-README.md) | README апстрима, включая дисклеймер «not an official Google product» |
| [science-skills-plugin.json](upstream/science-skills-plugin.json) | манифест плагина апстрима (v1.2.0) |
| [science-skills-CONTRIBUTING.md](upstream/science-skills-CONTRIBUTING.md) | правила контрибуции апстрима |

Копия зафиксирована на дату 2026-09-13 (последний push апстрима — 2026-09-08).

### Что покрывает Apache-2.0, а что нет

- **Скрипты и инструкции навыков** — Apache-2.0, можно свободно использовать,
  изменять и распространять с сохранением копирайта Google и текста лицензии.
- **Данные, полученные через навыки** — под условиями своих источников. Таблица
  источников: [upstream/science-skills-SKILL_LICENSES.md](upstream/science-skills-SKILL_LICENSES.md).
  У части баз условия с требованием атрибуции: GTEx, Human Protein Atlas, Reactome,
  Open Targets, UniProt/InterPro/QuickGO (Terms of Use EMBL-EBI), RCSB PDB, UCSC,
  NCBI (ClinVar, dbSNP, PubMed, sequence fetch).

### Отдельные ограничения

- **AlphaGenome (DeepMind)** — Research Use Only. Доступ к выводам требует API-ключа,
  условия которого запрещают клиническое применение. Навык обязывает агента не давать
  медицинских советов и не переводить высокий балл в диагноз. Публичной страницы с
  текстом условий нет — они принимаются при регистрации ключа.
- **Личные генетические данные** — ограничения задаются соглашением лаборатории, а не
  лицензией навыков. Работа локальным агентом; загрузка в облачную LLM может
  противоречить такому соглашению.
- **PyMOL** — сам навык только управляет установленным PyMOL; лицензия PyMOL отдельная
  (Schrödinger), см. ссылку в SKILL_LICENSES.
