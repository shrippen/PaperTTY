# Publishing this wiki to GitHub

The markdown files in this directory are GitHub Wiki–compatible (`Home.md`, `_Sidebar.md`, one page per driver).

After the main repository has been pushed, publish with:

```bash
# one-time: enable Wiki in GitHub repo settings, then:
git clone https://github.com/shrippen/PaperTTY.wiki.git /tmp/PaperTTY.wiki
cp -a wiki/. /tmp/PaperTTY.wiki/
cd /tmp/PaperTTY.wiki
git add -A
git commit -m "Sync display driver wiki pages"
git push
```

Or keep using these files as in-repo documentation linked from the README.
