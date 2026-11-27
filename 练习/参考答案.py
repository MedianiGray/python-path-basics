"""参考答案.py —— 待修.py 的修改版，跑得通、也搬得走。

改了三处：
    1) 人名不写在源码里，从上一级目录的 config.json 读；
    2) 所有路径由 Base(__file__) 算，不写盘符；
    3) 输出目录用 BASE / "output"，不存在就建，不依赖 cwd。

用法：python 参考答案.py
"""

import json
from pathlib import Path

BASE = Path(__file__).resolve().parent              # 本 py 所在目录（练习/）
ROOT = BASE.parent                                  # 项目根（path-demo/）
CONFIG = ROOT / "config.json"
DATA = ROOT / "data" / "sample.txt"
OUTPUT_DIR = BASE / "output"
REPORT = OUTPUT_DIR / "report.txt"


def load_name():
    """配置读不到就退回默认值，程序不因为缺配置直接崩。"""
    try:
        cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
        return cfg.get("name", "（未配置）")
    except (OSError, ValueError):
        return "（未配置）"


def read_lines(path):
    with path.open("r", encoding="utf-8") as f:
        return [ln.rstrip("\n") for ln in f if ln.strip()]


def main():
    name = load_name()
    print("学生：", name)
    print("数据：", DATA.relative_to(ROOT).as_posix(), "（相对项目根，便于打印）")

    lines = read_lines(DATA)
    print("读到", len(lines), "行")
    print("最长一行：", max(lines, key=len))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(
        "学生：%s\n行数：%d\n来源：%s\n" % (name, len(lines), DATA.name),
        encoding="utf-8",
    )
    print("报告已写入：", REPORT.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
