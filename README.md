# 三个概念对比演示（硬编码 / 绝对路径 / 相对路径 / pathlib）

实训场景对应：`pythonProject` 里一个 py 文件 + `data/` 数据目录 + `config.json` 配置，
**整个文件夹要能打包拷走**（拷 U 盘、打包进虚拟机镜像、发给同学）。

在线看课件：<https://medianigray.github.io/python-path-basics/>

```
path-demo/                  （仓库名 python-path-basics，内容即此目录）
├─ index.html            两页可投屏课件：1 概念 / 2 实证，← → 翻页
├─ 课件-1-概念.png        课件第 1 页截图，可直接插进笔记
├─ 课件-2-实证.png        课件第 2 页截图
├─ demo_paths.py         演示脚本（六节，逐条打印现象）
├─ config.json           外部配置：改这里换人，不用改 py
├─ data/sample.txt       被读的目标文件
└─ 运行结果样例.txt       本机真实跑出来的输出，可先看结果再跑
```

## 怎么跑，看什么

| 跑法 | 命令 | 你会看到 |
|---|---|---|
| 在脚本目录里跑 | `cd path-demo` → `python demo_paths.py` | 相对路径 **能读到**（cwd 正好是脚本目录） |
| 从上一级跑 | `python path-demo\demo_paths.py` | 相对路径 **FileNotFoundError**，pathlib 那段照样能读 |
| 拷走再跑 | 把 `path-demo` 复制到任意位置再运行 | 只有 pathlib 版活着；写死的 `E:\pythonProject` 仍然炸 |

脚本第 3 节还会主动 `os.chdir()` 到临时目录，现场演示「cwd 一换，相对路径就找错」；
第 5 节把整个项目复制到临时目录、再起子进程跑一次，模拟打包搬家的实测。

## 四种写法对照

| 类型 | 例子 | 优点 | 缺点 |
|---|---|---|---|
| 硬编码值 | `NAME = "覃祖悦"` | 写得快 | 换人要改源码 |
| 绝对路径 | `open(r"E:\pythonProject\data\a.txt")` | 定位唯一 | 换电脑/换盘/换文件夹立刻失效 |
| 相对路径 | `open("data/a.txt")` | 结构不变就能用 | 跟着 **cwd** 走，从别处启动就找错 |
| pathlib | `Path(__file__).resolve().parent / "data" / "a.txt"` | 路径自己算，打包即用 | 需要记住这个范式 |

## 为什么 pathlib 版能打包

`__file__` 是「这个 py 文件自己」的位置，`resolve()` 把它变成规范绝对路径，`.parent` 拿到所在目录，
再用 `/` 往下拼。于是：

- 从哪个目录启动都不影响（不依赖 cwd）；
- 整个文件夹换个盘、换个电脑，路径跟着脚本走，照样对；
- Windows 反斜杠、欧拉/Linux 正斜杠，**同一段代码不用改**（`pathlib` 自动处理分隔符）。

> 一句话：路径不要写死，交给 `Path(__file__).parent` 去算；配置不要写死，丢进 `config.json`。

## 欧拉 / Linux 上的同一段代码

```python
from pathlib import Path
BASE = Path(__file__).resolve().parent
print((BASE / "data" / "sample.txt").read_text(encoding="utf-8"))
```

在 `/home/student/pythonProject/demo_paths.py` 下跑，行为与 Windows 完全一致；
换成 `open("/home/student/pythonProject/data/sample.txt")` 就又退化成「写死绝对路径」，换机器照样炸。
