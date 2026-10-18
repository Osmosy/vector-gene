# Вендорные ресурсы и артефакты проверки

## Что здесь лежит

| Путь | Что это | Коммитится |
|------|---------|------------|
| `upstream/` | файлы апстрима science-skills: лицензия, SKILL_LICENSES, README, манифест, CONTRIBUTING | да |
| `archive/` | прежняя версия SKILL.md (v1, 28.06.2026) | да |
| `vector-gene.architecture.html` | живая диаграмма (Archify, showcase) | да |
| `*.visual-check.json` | отчёт визуальной проверки диаграммы | нет (генерируется) |
| `*.visual-check.html` | contact sheet скриншотов проверки | нет |
| `*.visual-check.*.png` | скриншоты 1440×900 и 2048×1320, light/dark | нет |

Артефакты проверки не коммитятся: они воспроизводятся командой

```bash
cd ~/.hermes/skills/archify
node bin/archify.mjs visual-check <путь>/docs/vector-gene.architecture.html --json
```

## Обновление вендорной копии

Копия science-skills зафиксирована на 2026-10-18, коммит апстрима
`99f3085bcb40514cdba7833205b3dedbf473b26d` (manifest 1.3.0, дата коммита 2026-10-15;
тега `v1.3.0` в апстриме нет — последний тег `v1.2.4`).
Обновление — повторное копирование `skills/` апстрима в `skills/science/` плюс
обновление `upstream/` и хеша в этом файле и в `NOTICE.md`. При обновлении перечитать
`SKILL_LICENSES.md`: условия сторонних баз меняются, ответственность за их соблюдение
на пользователе.
