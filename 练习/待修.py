"""待修.py —— 课堂练习：这段代码在本机跑不起来，也打包带走不了。

三处毛病都在，按注释里的 TODO 改掉，让它：
    1) 换台电脑、换一个目录也能跑；
    2) 不在源码里写死人名和盘符；
    3) 把统计结果写到项目里的 output/report.txt（而不是靠当前工作目录）。

改完用：python 待修.py
"""

NAME = "覃祖悦"                                      # TODO 1 硬编码：改成人名不要写在源码里
DATA = r"E:\pythonProject\data\sample.txt"            # TODO 2 写死绝对路径：本机没有 E 盘
REPORT = "output/report.txt"                          # TODO 3 裸相对路径：cwd 一变就写错地方


def read_lines(path):
    with open(path, "r", encoding="utf-8") as f:
        return [ln.rstrip("\n") for ln in f if ln.strip()]


def main():
    print("学生：", NAME)
    print("数据：", DATA)

    try:
        lines = read_lines(DATA)
    except OSError as e:
        print("读数据失败：", type(e).__name__, "—— 路径指的地方不存在")
        print("提示：真实文件就在这个 py 旁边的 data/sample.txt")
        return
    except FileNotFoundError as e:
        print("读数据失败：", type(e).__name__, "—— 相对路径跟着 cwd 走丢了")
        return

    print("读到", len(lines), "行")
    print("最长一行：", max(lines, key=len))

    with open(REPORT, "w", encoding="utf-8") as f:
        f.write("学生：%s\n行数：%d\n" % (NAME, len(lines)))
    print("报告已写入：", REPORT)


if __name__ == "__main__":
    main()
