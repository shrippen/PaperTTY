# Design Reference

PaperTTY has no GUI of its own: it draws the terminal on an e-paper panel. The only designed
surface is the landing page (`docs/`), and it is generated from **Kante**, the shared shrippen
design system: <https://github.com/shrippen/Kante> (checkout `../Kante`).

- **Stylesheet**: the page links `https://shrippen.github.io/v1/shrippen.css` and `shrippen.js`
  (Kante's build); template `templates/landing.html` in Kante.
- **No own values**: colours, fonts, sizes, cuts and motion come from Kante's roles
  (`--fg1`, `--primary`, `--link`, `--bg-hard` …). Inline SVG figures use the same variables,
  never `#hex`.
- **Missing elements** are added to Kante first, then used here.
- **Badges**: shields.io with `labelColor=1c1c20`; value colours as in Kante's README.
- **Dark only** for the landing page, as Kante prescribes for landing pages.
- **Screenshots** come from the demo mode (`demo/shots.json`), never from real data.

Full spec: Kante's `README.md` (tokens in `tokens/palette.json`).
