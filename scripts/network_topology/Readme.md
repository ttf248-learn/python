# 🌐 Process Network Topology Visualizer (进程网络拓扑可视化工具)

这是一个用于分析和可视化 Linux 系统上指定进程之间网络连接关系的 Python 脚本。它利用 `psutil` 收集网络连接数据，并使用 `graphviz` 库生成清晰、防重叠的拓扑图。

## ✨ 特点

  * **多进程分析：** 一次性分析多个指定的 PID 之间的网络连接。
  * **智能监听匹配：** 自动处理 `0.0.0.0` 和 `::` 等通配符地址的端口匹配。
  * **优化布局：** 采用 `sfdp` 布局引擎和优化的 Graphviz 属性，最大限度减少连线和节点重叠。
  * **清晰展示：** 在图的边上直接标注客户端端口和服务器端口，方便追溯连接路径。
  * **多格式输出：** 支持生成 PNG 图片和交互式 SVG 嵌入的 HTML 文件。

## ⚙️ 环境要求

  * Python 3.x
  * `psutil` 库
  * `graphviz` Python 库
  * **Graphviz C 库** (系统依赖)

## 📥 安装

### 1\. 安装 Python 依赖

```bash
pip install psutil graphviz
```

### 2\. 安装系统 Graphviz 库

`graphviz` Python 库需要底层的 Graphviz C 库来渲染图形。请根据您的操作系统执行相应命令：

| 系统 | 命令 |
| :--- | :--- |
| **Debian/Ubuntu** | `sudo apt-get install graphviz` |
| **RHEL/CentOS/Fedora** | `sudo dnf install graphviz` (或 `yum`) |
| **macOS (使用 Homebrew)** | `brew install graphviz` |

## 🚀 使用方法

### 1\. 保存脚本

将优化后的代码保存为 `net_topo.py`。

### 2\. 运行脚本（推荐使用 `sudo`）

由于获取完整的系统网络连接信息（特别是跨用户进程的连接）需要较高的权限，**强烈建议使用 `sudo` 运行**。

```bash
# 语法: python3 net_topo.py --pids <PID1> <PID2> ... --output-name <文件前缀>
sudo python3 net_topo.py --pids 1234 5678 9101 --output-name service_map
```

#### 📌 参数说明

| 参数 | 类型 | 必需 | 描述 | 示例 |
| :--- | :--- | :--- | :--- | :--- |
| `--pids` | 整数列表 | 是 | 一个或多个要分析的进程 ID (PID)。 | `1234 5678` |
| `--output-name` | 字符串 | 是 | 输出文件的前缀名（不含扩展名）。 | `app_topo` |
| `--formats` | 字符串列表 | 否 | 输出格式，可选 `png`, `html`。默认两者都输出。 | `png` |

### 3\. 查看结果

运行成功后，将在当前目录下生成以下文件：

  * `service_map.png`：生成的图片拓扑图。
  * `service_map.html`：包含可缩放 SVG 图的网页文件，建议用浏览器打开查看。

## 🖼️ 输出结果说明

  * **节点 (Boxes):**

      * 显示 `PID` 和 `Process Name`。
      * 显示进程正在 `Listen` (监听) 的端口列表。
      * 显示进程正在使用的 `Conn` (连接/外发) 的端口列表。

  * **边 (Arrows):**

      * 箭头从 **客户端 (Client / 发起连接方)** 指向 **服务器 (Server / 监听方)**。
      * **连线标签：** 清晰地标注了连接中使用的端口信息：
          * `Client Port`: 客户端使用的本地 (通常是临时) 端口。
          * `Server Port`: 服务器监听的目标端口。

-----

## 🛠️ 故障排除

  * **错误: `failed to execute 'dot'`**

      * **原因：** 缺少 Graphviz C 库。
      * **解决：** 请参考 [安装](https://www.google.com/search?q=%232-%E5%AE%89%E8%A3%85%E7%B3%BB%E7%BB%9F-graphviz-%E5%BA%93) 部分安装系统依赖。

  * **警告: `未找到已建立的 (ESTABLISHED) 连接`**

      * **原因 1：** 脚本没有足够的权限读取所有网络连接。
      * **解决 1：** 尝试使用 `sudo python3 net_topo.py ...` 运行。
      * **原因 2：** 指定的 PID 之间当时确实没有活跃的 `ESTABLISHED` 状态的连接。