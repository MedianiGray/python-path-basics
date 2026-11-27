"""把 path-demo 目录同步到 GitHub 仓库 MedianiGray/python-path-basics。

为什么需要它：本机 github.com 域名被污染，`git push` 会报
    fatal: unable to access 'https://github.com/...': Recv failure: Connection was reset
但 api.github.com 通，所以走 GitHub Contents API 直传，效果与 push 等价（远端会产生一条 commit）。

用法：
    python tools/publish.py            # 全量同步
    python tools/publish.py index.html # 只传某个文件

token 取自 git 凭据管理器（之前登录 GitHub 时存下的），无需手填。
"""
import base64
import json
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OWNER, REPO, BRANCH = "MedianiGray", "python-path-basics", "main"
SKIP = {".git", "__pycache__", "output"}


def token():
    git = shutil.which("git") or r"I:\ProgramFiles\Git\cmd\git.exe"
    out = subprocess.run(
        [git, "credential", "fill"],
        input="protocol=https\nhost=github.com\n\n",
        capture_output=True, text=True,
    ).stdout
    for line in out.splitlines():
        if line.startswith("password="):
            return line.split("=", 1)[1].strip()
    sys.exit("未找到 GitHub 凭据，请先执行一次 git push 或 gh auth login")


def api(method, path, body=None, tok=""):
    url = "https://api.github.com" + urllib.parse.quote(path, safe="/(),?=&")
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", "Bearer " + tok)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "path-demo-publish")
    if data:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
            return r.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")


def main():
    tok = token()
    only = set(sys.argv[1:])
    files = [
        p for p in sorted(ROOT.rglob("*"))
        if p.is_file()
        and not any(part in SKIP for part in p.relative_to(ROOT).parts)
        and (not only or p.relative_to(ROOT).as_posix() in only)
    ]
    st, repo = api("GET", f"/repos/{OWNER}/{REPO}", tok=tok)
    if st != 200:
        sys.exit(f"仓库不可访问：{st} {repo.get('message')}")

    for p in files:
        rel = p.relative_to(ROOT).as_posix()
        body = {
            "message": "sync " + rel,
            "content": base64.b64encode(p.read_bytes()).decode(),
            "branch": BRANCH,
        }
        st, cur = api("GET", f"/repos/{OWNER}/{REPO}/contents/{rel}?ref={BRANCH}", tok=tok)
        if st == 200 and isinstance(cur, dict) and cur.get("sha"):
            body["sha"] = cur["sha"]
            body["message"] = "update " + rel
        st, r = api("PUT", f"/repos/{OWNER}/{REPO}/contents/{rel}", body, tok=tok)
        flag = "OK " if st < 300 else "FAIL"
        print(f"{flag} {rel}  {st}  {(r.get('commit') or {}).get('sha', r.get('message', ''))}")
    print("\n站点：https://medianigray.github.io/python-path-basics/")


if __name__ == "__main__":
    main()
