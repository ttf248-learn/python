#!/usr/bin/env python3

import psutil
import graphviz
import argparse
import os
import sys
from collections import defaultdict

def get_process_name(pid):
    """获取单个进程的名称"""
    try:
        return psutil.Process(pid).name()
    except psutil.NoSuchProcess:
        return "N/A (已退出)"
    except psutil.AccessDenied:
        return "N/A (无权限)"

def find_listener_pid(raddr_tuple, listen_map):
    """
    智能查找监听 PID，处理 '0.0.0.0' 和 '::' 通配符。
    
    :param raddr_tuple: (ip, port) 客户端连接的远程地址
    :param listen_map: {(ip, port) -> pid} 系统的监听端口映射
    :return: 匹配的 PID，否则返回 None
    """
    r_ip, r_port = raddr_tuple
    
    # 1. 尝试直接匹配 
    pid = listen_map.get((r_ip, r_port))
    if pid:
        return pid
        
    # 2. 尝试匹配 IPv4 通配符 (0.0.0.0)
    pid = listen_map.get(('0.0.0.0', r_port))
    if pid:
        return pid

    # 3. 尝试匹配 IPv6 通配符 (::) - 常常接受 v4/v6 连接
    pid = listen_map.get(('::', r_port))
    if pid:
        return pid
        
    return None

def build_topology(target_pids, output_name, formats):
    """构建并渲染网络拓扑图 (优化版本)"""
    
    if os.geteuid() != 0:
        print("------------------------------------------------------")
        print("警告：脚本未以 root 权限 (sudo) 运行。")
        print("可能无法获取所有进程的网络连接信息。")
        print("如果未找到连接，请首先尝试使用 'sudo' 运行。")
        print("------------------------------------------------------")

    g = graphviz.Digraph('process_topology', comment='Process Network Topology (Optimized)')
    
    # <<< 核心优化：Graphviz 布局属性 (更激进地拉开节点和连线) >>>
    g.attr(engine='sfdp') # 更改为 sfdp，通常在连接密集时表现优于 fdp
    g.attr(overlap='scale') # 尝试使用 'scale' 模式来缩放并消除重叠
    g.attr(splines='curved') # 使用平滑曲线
    g.attr(rankdir='LR')
    g.attr(sep='1.5,1.5') # 增加节点之间的最小间距
    g.attr(nodesep='1.0') # 增加同一 rank 下节点间的最小间距
    g.attr(ranksep='2.0') # 增加不同 rank (层级) 之间节点间的最小间距

    # <<< 节点属性 - 简化为标准形状，不使用端口锚点 >>>
    g.attr('node', shape='box', style='filled', color='#3498DB', fillcolor='#DAEEF7', 
           fontname='Arial', fontsize='12', margin='0.3,0.2') # 增加内边距
    
    # 边缘属性 (重点：增加 penwidth 和调整颜色)
    g.attr('edge', fontname='Arial', fontsize='9', arrowhead='normal', arrowsize='0.8', 
           penwidth='1.5', color='#2C3E50') # 稍微加粗连线，更容易区分

    target_pid_set = set(target_pids)
    
    # 1. 信息收集 (不变)
    process_ports = defaultdict(lambda: {"listen": set(), "conn": set()})
    listen_map = {}
    all_connections = []

    print("正在扫描系统连接 (这可能需要几秒钟)...")
    try:
        all_conns = psutil.net_connections(kind='inet')
    except psutil.AccessDenied:
        print("\n错误：无权扫描系统网络连接。请使用 'sudo' 运行此脚本。")
        sys.exit(1)

    for conn in all_conns:
        if conn.pid is None:
            continue
            
        if conn.status == 'LISTEN':
            if conn.laddr:
                # 使用 find_listener_pid 检查时会用到这个 map
                listen_map[(conn.laddr.ip, conn.laddr.port)] = conn.pid
                if conn.pid in target_pid_set:
                    process_ports[conn.pid]["listen"].add(conn.laddr.port)
        
        elif conn.status == 'ESTABLISHED':
            all_connections.append(conn)
            if conn.pid in target_pid_set and conn.laddr:
                process_ports[conn.pid]["conn"].add(conn.laddr.port)


    # 2. 创建节点 (Nodes) - 简化展示
    print("正在创建进程节点...")
    valid_pids = set()
    for pid in target_pid_set:
        name = get_process_name(pid)
        if name.startswith("N/A"):
            print(f"警告：无法访问 PID {pid} ({name})，将跳过。")
            continue
        
        valid_pids.add(pid)
        
        # 简化节点标签，核心信息居中显示
        listen_ports = sorted(list(process_ports[pid]["listen"]))
        conn_ports = sorted(list(process_ports[pid]["conn"] - process_ports[pid]["listen"]))
        
        listen_str = f"Listen: {', '.join(map(str, listen_ports))}" if listen_ports else "Listen: None"
        conn_str = f"Conn: {', '.join(map(str, conn_ports))}" if conn_ports else "Conn: None"
        
        label = (f"PID: {pid}\n"
                 f"Process: {name}\n\n"
                 f"{listen_str}\n"
                 f"{conn_str}")
        
        # 不使用端口锚点，让 Graphviz 自动布局连线
        g.node(str(pid), label=label)

    # 3. 创建边 (Edges) - 使用 Edge Label 标识端口
    print("正在绘制连接...")
    edges_found = set()
    
    for conn in all_connections:
        pid_a = conn.pid 
        if pid_a not in valid_pids or not conn.raddr:
            continue

        raddr_tuple = (conn.raddr.ip, conn.raddr.port)
        pid_b = find_listener_pid(raddr_tuple, listen_map) 
        
        if pid_b and pid_b in valid_pids and pid_a != pid_b:
            
            port_a = conn.laddr.port # 客户端的本地端口
            port_b = conn.raddr.port # 服务器的监听端口
            
            # 使用 (客户端PID, 服务器PID, 服务器端口) 作为唯一键
            edge_key = (pid_a, pid_b, port_b) 

            if edge_key not in edges_found:
                
                # 连接标签清晰显示端口信息
                label_text = f"Client Port: {port_a}\nServer Port: {port_b}"
                
                # 直接连接两个进程节点
                g.edge(str(pid_a), str(pid_b), 
                       label=label_text, 
                       tooltip=f"Client {pid_a}:{port_a} -> Server {pid_b}:{port_b}",
                       len='2.0') # 强制连线更长一点
                edges_found.add(edge_key)

    if not edges_found:
        print("在指定的目标 PID 之间未找到已建立的 (ESTABLISHED) 连接。")
    else:
        print(f"成功找到并绘制了 {len(edges_found)} 条连接。")

    # 4. 渲染输出
    print("正在生成输出文件...")
    try:
        if 'png' in formats:
            g.render(output_name, format='png', cleanup=True)
            print(f"✅ 已生成 PNG: {output_name}.png")
            
        if 'html' in formats:
            try:
                # 渲染 SVG 用于嵌入 HTML
                svg_bytes = g.pipe(format='svg')
                html_content = f"""
                <html><head><title>进程网络拓扑图</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f4f4f4; }}
                    h1 {{ text-align: center; color: #333; }}
                    .container {{ border: 1px solid #ccc; padding: 20px; display: inline-block; background-color: #fff; box-shadow: 0 8px 16px rgba(0,0,0,0.2); text-align: center; margin: 0 auto; }}
                    svg {{ max-width: 100%; height: auto; display: block; }}
                </style></head><body>
                <h1>进程网络拓扑图 (PIDs: {', '.join(map(str, target_pids))})</h1>
                <div class="container">{svg_bytes.decode('utf-8')}</div>
                <p>注：连线上的标签显示 Client Port (发起方) 和 Server Port (监听方)。</p>
                </body></html>
                """
                html_filename = f"{output_name}.html"
                with open(html_filename, "w", encoding="utf-8") as f:
                    f.write(html_content)
                print(f"✅ 已生成 HTML: {html_filename}")
            except Exception as e:
                print(f"生成 HTML/SVG 时出错: {e}")

    except Exception as e:
        print(f"渲染输出时出错：{e}")
        if 'failed to execute' in str(e):
            print("\n🚨 错误：无法执行 'dot' 命令。")
            print("请确保已安装 Graphviz C 库。")
            print(" - Ubuntu/Debian: sudo apt-get install graphviz")
            print(" - RHEL/Fedora:   sudo dnf install graphviz")

def main():
    parser = argparse.ArgumentParser(
        description="绘制多个进程之间的网络拓扑图 (优化防重叠版)。",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '--pids', metavar='PID', type=int, nargs='+', required=True,
        help="一个或多个要分析的进程 ID (PID)。"
    )
    parser.add_argument(
        '--output-name', type=str, required=True,
        help="输出文件的前缀名 (不带扩展名)。"
    )
    parser.add_argument(
        '--formats', type=str, nargs='+', choices=['png', 'html'], default=['png', 'html'],
        help="输出格式 (png, html, 或两者)。\n默认为: png html。"
    )
    
    args = parser.parse_args()
    unique_pids = sorted(list(set(args.pids)))
    
    print(f"🚀 开始分析 PIDs: {unique_pids}")
    build_topology(unique_pids, args.output_name, set(args.formats))

if __name__ == "__main__":
    main()