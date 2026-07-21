# Semantic color rules

Stargazing separates visual hierarchy from readability. Assign text colors by meaning.

| Token | Purpose | Appropriate examples |
|---|---|---|
| `--sg-tx` | Primary text | Body prose, code, labels, menus, form values, settings names |
| `--sg-tx-2` | Supporting text | Captions, bylines, timestamps, descriptions, subordinate metadata |
| `--sg-tx-3` | Expendable text | Placeholders, disabled labels, line numbers, decorative annotations |

## Body text

Body text always uses `--sg-tx`. A paragraph does not become muted because it is smaller than a heading. Long prose, documentation, code, and important instructions must remain primary.

## Muted text

Muted text supports primary information. It may provide a setting description such as “Subtle grain,” but the setting name itself remains primary. It may identify an article’s date, but the article remains primary.

## Faint text

Faint text deliberately creates low contrast and does not pass body-text contrast requirements. Use it only when losing the text would not prevent understanding or completing a task.

## Semantic mappings

| Role | Light | Dark |
|---|---|---|
| Background | paper | ink |
| Background 2 | base 50 | base 950 |
| UI | base 100 | base 900 |
| UI hover | base 150 | base 850 |
| UI active | base 200 | base 800 |
| Faint text | base 300 | base 700 |
| Muted text | base 600 | base 500 |
| Primary text | ink | base 200 |
| Accent text | accent 600 | accent 400 |

WCAG conformance depends on the actual text size, weight, foreground, and background. Semantic names alone do not establish accessibility.
