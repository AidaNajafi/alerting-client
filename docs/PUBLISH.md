# Publish to GitHub

Local git repo is initialized on `main`. Create a public GitHub repo and push:

```bash
cd /home/aida/alerting-client
git remote add origin git@github.com:<org>/alerting-client.git
git push -u origin main
```

Consumers:

```bash
poetry add "git+https://github.com/<org>/alerting-client.git"
```

Optional later: publish wheels to PyPI / GitHub Releases.
