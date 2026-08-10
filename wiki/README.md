# Publishing this wiki to GitHub

The markdown files in this directory are the source of truth for the
[GitHub Wiki](https://github.com/shrippen/PaperTTY/wiki).

They are also kept in-repo so the docs travel with the code.

To re-sync after editing files here:

```bash
git clone https://github.com/shrippen/PaperTTY.wiki.git /tmp/PaperTTY.wiki
cp -a wiki/*.md wiki/_Sidebar.md /tmp/PaperTTY.wiki/
# omit this README.md from the wiki repo
rm -f /tmp/PaperTTY.wiki/README.md
cd /tmp/PaperTTY.wiki
git add -A
git commit -m "Sync wiki from main repo"
git push
```

Note: GitHub only creates the `.wiki.git` remote after the first wiki page exists
(once per repository). After that, git push works normally.
