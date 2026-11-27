# -*- coding: utf-8 -*-
"""
三个概念对比演示：硬编码 / 绝对路径 / 相对路径 / pathlib 规范写法
实训场景：一个 py 文件 + data/ 数据目录 + config.json 配置，整个文件夹要能打包拷走。

运行：  python demo_paths.py
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def head(no, title):
    print("\n" + "=" * 62)
    print(f"{no}. {title}")
    print("=" * 62)


BASE = Path(__file__).resolve().parent        # 本 py 文件所在目录（绝对、可靠）
DATA = BASE / "data"
SAMPLE = DATA / "sample.txt"
CONFIG = BASE / "config.json"


def read_text_safe(p):
    return Path(p).read_text(encoding="utf-8").strip()


def main():
    print(f"当前工作目录 cwd = {os.getcwd()}")
    print(f"本脚本所在目录    = {BASE}")

    # ---------------- 1. 硬编码：值写死在代码里 ----------------
    head(1, "硬编码：值直接写死在源码里，运行时不改代码就改不了")
    NAME = "覃祖悦"               # 想换成别的同学？只能回来改这一行，重新保存
    print(f'  NAME = "{NAME}"  →  print 出来就是 {NAME}')
    print("  缺点：内容变了得改源码，没法外部配置。")

    print("\n  [对照] 把「值」放进外部配置文件，代码不动也能换人：")
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    print(f'  config.json → 学号 {cfg["student_id"]} · {cfg["name"]} · {cfg["major"]}')
    print("  改 config.json 就换了人，py 文件一个字都不用动。")

    # ---------------- 2. 绝对路径：从盘符根写死 ----------------
    head(2, "绝对路径（写死）：从根目录开始的完整地址，换机器就炸")
    HARD_ABS = r"E:\pythonProject\data\sample.txt"   # 典型高危写法：把盘符和目录全写进代码
    print(f'  代码里写死：HARD_ABS = r"{HARD_ABS}"')
    try:
        txt = read_text_safe(HARD_ABS)
        print(f"  读到了：{txt}")
    except (FileNotFoundError, OSError) as e:
        print(f"  读失败 → {type(e).__name__}")
        print("  原因：本机没有 E: 这个盘，也没有 E:\\pythonProject 这个目录（换了电脑/盘符同理）。")
        print("  同一个项目换到别的电脑、别的盘，这行代码立刻失效——这就是「硬编码高危」。")
    print(f"  而它在本机的真实绝对路径其实是：{SAMPLE}")

    # ---------------- 3. 相对路径：跟着 cwd 走 ----------------
    head(3, "相对路径：以「当前工作目录」为起点，cwd 一变就找错文件")
    REL = "data/sample.txt"
    print(f'  代码：open("{REL}")  ← 只写相对位置，不写盘符')
    try:
        txt = read_text_safe(REL)
        print(f"  读到了：{txt}")
        print("  前提：此刻 cwd 正好等于 py 所在目录。")
    except FileNotFoundError as e:
        print(f"  读失败 → FileNotFoundError（cwd 不是 py 所在目录）")

    old_cwd = os.getcwd()
    scratch = Path(tempfile.gettempdir())
    os.chdir(scratch)                       # 模拟「从别处运行 / 双击快捷方式 / 定时任务」
    print(f"\n  现在把 cwd 切到别处：os.chdir(r\"{scratch}\")")
    try:
        read_text_safe(REL)
        print("  还能读到？不应该出现。")
    except FileNotFoundError:
        print(f'  open("{REL}") → FileNotFoundError：相对路径跟着 cwd 走，cwd 一变就找错。')

    # ---------------- 4. pathlib 规范写法 ----------------
    head(4, "pathlib 规范写法：脚本自己算路径，cwd 变了也不受影响")
    print('  BASE = Path(__file__).resolve().parent')
    print('  p    = BASE / "data" / "sample.txt"')
    try:
        txt = read_text_safe(BASE / "data" / "sample.txt")
        print(f'  在 cwd = {Path.cwd()} 下照样读到：{txt}')
    except FileNotFoundError as e:
        print(f"  读失败 → {e}")
    os.chdir(old_cwd)

    # ---------------- 5. 打包搬家的实测 ----------------
    head(5, "实证：整个文件夹拷到别处，谁的代码还活着")
    tmp = Path(tempfile.mkdtemp(prefix="plant_"))
    dst = tmp / "project_copy"
    shutil.copytree(BASE, dst)
    print(f"  已把整个项目复制到：{dst}")
    print("  （模拟：拷进 U 盘 / 打包进虚拟机镜像 / 发给同学）")

    probe = (
        "import sys\n"
        "from pathlib import Path\n"
        "base = Path(sys.argv[1])\n"
        "t = (base / 'data' / 'sample.txt').read_text(encoding='utf-8').strip()\n"
        "print('    pathlib 版  → ' + t.split('；')[0][:24])\n"
    )
    r = subprocess.run([sys.executable, "-c", probe, str(dst)],
                       cwd=str(Path(tempfile.gettempdir())), capture_output=True, text=True)
    print(r.stdout.strip() or r.stderr.strip())
    print("  → 路径由脚本自己算，换盘、换目录、换电脑都不用改代码。")

    hard_probe = (
        "import sys\n"
        "from pathlib import Path\n"
        "p = Path(sys.argv[1])\n"
        "try:\n"
        "    p.read_text(encoding='utf-8')\n"
        "    print('    写死绝对路径版 → 居然读到了')\n"
        "except Exception as e:\n"
        "    print('    写死绝对路径版 → ' + type(e).__name__ + '（照样炸）')\n"
    )
    r2 = subprocess.run([sys.executable, "-c", hard_probe, HARD_ABS], capture_output=True, text=True)
    print(r2.stdout.strip() or r2.stderr.strip().splitlines()[-1])

    shutil.rmtree(tmp, ignore_errors=True)

    # ---------------- 小结 ----------------
    head(6, "小结")
    print("  硬编码值    NAME = \"覃祖悦\"                改内容要改源码")
    print("  绝对路径    r\"E:\\pythonProject\\data\\...\"   定位唯一，换机器就炸")
    print("  相对路径    \"data/sample.txt\"               随 cwd 走，cwd 变了就错")
    print("  pathlib     BASE/\"data\"/\"sample.txt\"       跟着脚本走，打包即用 ✔")
    print("\n  一句话：路径不写死，交给 Path(__file__).parent 去算。")


if __name__ == "__main__":
    main()
