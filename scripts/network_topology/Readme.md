# 进程网络拓扑图生成器

## 简介

`process_network_topology.py` 是一个用于分析和可视化进程网络拓扑图的Python脚本。它能够接收多个进程ID（PIDs），分析这些进程间的网络通信关系，并生成直观的拓扑图。

## 功能特性

- ✅ **多进程分析**: 支持同时分析多个PID进程
- ✅ **网络拓扑可视化**: 生成进程间网络连接拓扑图
- ✅ **多种输出格式**:
  - PNG格式：静态拓扑图，适合报告和文档
  - HTML格式：交互式拓扑图，支持缩放和查看详情
  - TXT格式：详细的文本分析报告
- ✅ **节点信息**: 节点显示格式为 `PID (进程名)`
- ✅ **端口通信标注**: 清楚显示网络端口和连接方向
- ✅ **进程关系**: 包含父子进程关系
- ✅ **外部连接**: 显示进程与外部服务的连接

## 系统要求

- **操作系统**: Linux
- **Python版本**: 3.8+
- **权限**: 需要读取进程信息的权限（通常需要root或目标进程的所有者权限）

## 安装依赖

在脚本目录中执行以下命令安装依赖：

```bash
pip install -r requirements.txt
```

### 依赖说明

- `psutil`: 获取进程信息、网络连接、进程树等系统信息
- `networkx`: 构建和分析网络拓扑图
- `matplotlib`: 生成静态PNG图像
- `plotly`: 生成交互式HTML图像
- `numpy`: 数值计算支持

## 使用方法

### 基本语法

```bash
python process_network_topology.py -p PID1 PID2 [PID3 ...] [选项]
```

### 参数说明

| 参数 | 简写 | 类型 | 说明 |
|------|------|------|------|
| `--pids` | `-p` | int[] | **必需** - 要分析的进程ID列表 |
| `--output` | `-o` | string | 输出目录 (默认: output) |
| `--html-only` | - | flag | 只生成HTML格式的交互式拓扑图 |
| `--png-only` | - | flag | 只生成PNG格式的静态拓扑图 |
| `--report-only` | - | flag | 只生成文本分析报告 |
| `--verbose` | `-v` | flag | 显示详细信息 |
| `--help` | `-h` | flag | 显示帮助信息 |

### 使用示例

#### 1. 基本用法

分析PID为1234和5678的进程：

```bash
python process_network_topology.py -p 1234 5678
```

#### 2. 指定输出目录

```bash
python process_network_topology.py -p 1234 5678 -o /tmp/topology
```

#### 3. 只生成HTML格式

```bash
python process_network_topology.py -p 1234 5678 --html-only
```

#### 4. 只生成PNG格式

```bash
python process_network_topology.py -p 1234 5678 --png-only
```

#### 5. 分析多个进程

```bash
python process_network_topology.py -p 1234 5678 9012 1314 -v
```

#### 6. 只生成分析报告

```bash
python process_network_topology.py -p 1234 5678 --report-only
```

### 获取进程ID的方法

#### 使用`ps`命令

```bash
# 查看所有进程
ps aux | grep <进程名>

# 查看特定用户的进程
ps -u <用户名>

# 查看进程树
ps auxf
```

#### 使用`pgrep`命令

```bash
# 根据进程名查找PID
pgrep -f <进程名>

# 查看进程的详细信息
pidof <进程名>
```

## 输出文件

脚本会在指定的输出目录中生成以下文件：

1. **process_topology.png** - 静态拓扑图
   - 高分辨率PNG图像
   - 包含节点、边、标签和图例
   - 适合插入报告和文档

2. **process_topology.html** - 交互式拓扑图
   - 可在浏览器中打开
   - 支持缩放、拖拽
   - 鼠标悬停显示详细信息

3. **topology_report.txt** - 详细分析报告
   - 进程信息
   - 网络连接详情
   - 拓扑关系列表

## 输出格式说明

### 节点

- **蓝色圆圈**: 监控的进程节点
  - 标签格式: `PID (进程名)`
  - 例如: `1234 (nginx)`

- **灰色方块**: 外部连接节点
  - 标签格式: `外部连接 IP:端口`
  - 例如: `外部连接 192.168.1.100:80`

### 边

- **箭头**: 网络连接方向
  - 指向箭头表示数据流向
  - 边标签显示端口信息: `端口: 12345 -> 80`

### 颜色含义

- **蓝色节点**: 监控的进程
- **灰色节点**: 外部连接
- **灰色边**: 网络连接
- **箭头**: 连接方向

## 示例输出

### 文本报告示例

```
============================================================
进程网络拓扑分析报告
============================================================

分析时间: 1699531200.0
监控进程数量: 2

============================================================
进程信息
============================================================

PID: 1234
  名称: nginx
  命令: /usr/sbin/nginx -g 'daemon off;'
  状态: running

PID: 5678
  名称: python
  命令: /usr/bin/python3 app.py
  状态: running

============================================================
网络连接信息
============================================================

PID 1234: 0.0.0.0:80 <-> 192.168.1.100:54321
  状态: ESTABLISHED

============================================================
网络拓扑关系
============================================================

1234 --[端口: 80 -> 54321]--> external_1234_80
```

## 注意事项

1. **权限要求**
   - 脚本需要读取目标进程信息的权限
   - 对于其他用户的进程，可能需要root权限

2. **进程状态**
   - 如果进程在分析期间结束，相关信息可能不完整
   -僵尸进程可能无法获取完整的网络信息

3. **网络连接**
   - 只显示TCP和UDP连接
   - 某些系统调用可能需要特殊权限

4. **性能考虑**
   - 分析大量进程可能需要较长时间
   - 生成的图像可能较大（特别是有很多连接时）

5. **数据准确性**
   - 网络连接信息是实时的，可能快速变化
   - 建议在进程相对稳定时进行分析

## 故障排除

### 常见问题

#### 1. "PID不存在" 警告

**原因**: 指定的PID不存在或进程已结束

**解决方案**:
```bash
# 检查进程是否存在
ps -p <PID>
# 或使用
ps aux | grep <PID>
```

#### 2. "无法访问PID" 权限错误

**原因**: 权限不足，无法读取进程信息

**解决方案**:
```bash
# 使用sudo运行
sudo python process_network_topology.py -p <PID1> <PID2>

# 或切换到进程所有者
su - <进程所有者>
python process_network_topology.py -p <PID1> <PID2>
```

#### 3. 图像显示异常

**原因**: 图形界面或字体问题

**解决方案**:
```bash
# 在无头服务器上，使用Agg后端
export MPLBACKEND=Agg
python process_network_topology.py -p <PID1> <PID2>
```

#### 4. 依赖安装失败

**原因**: pip源问题或Python版本不兼容

**解决方案**:
```bash
# 更新pip
python -m pip install --upgrade pip

# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 检查Python版本
python --version
```

## 扩展功能

### 自定义颜色方案

可以修改脚本中的以下部分来自定义节点颜色：

```python
# 在visualize_matplotlib方法中
nx.draw_networkx_nodes(
    self.graph, pos,
    nodelist=process_nodes,
    node_color='lightblue',  # 修改此颜色
    node_size=2000,
    alpha=0.8
)
```

### 添加更多节点属性

可以在`get_process_info`方法中添加更多信息：

```python
proc_info = {
    'pid': pid,
    'name': proc.name(),
    'cmdline': ' '.join(proc.cmdline()),
    'status': proc.status(),
    'create_time': proc.create_time(),
    'cpu_percent': proc.cpu_percent(),  # 添加CPU使用率
    'memory_info': proc.memory_info(),   # 添加内存信息
}
```

## 贡献

欢迎提交问题报告和改进建议！

## 许可证

MIT License

## 更新日志

### v1.0.0 (2025-11-10)
- 初始版本发布
- 支持多进程网络拓扑分析
- 支持PNG和HTML输出格式
- 支持文本分析报告
