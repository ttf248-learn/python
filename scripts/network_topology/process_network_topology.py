#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
进程网络拓扑图生成器

支持输入多个PID进程编号，绘制进程间网络拓扑图，
输出HTML和PNG格式的拓扑图。

节点显示格式：PID (进程名)
连接显示方向和端口信息
"""

import argparse
import os
import sys
from typing import Dict, List, Set, Tuple, Optional
import json
import re
from pathlib import Path
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import font_manager
import psutil
from collections import defaultdict
import plotly.graph_objects as go
import plotly.express as px
from plotly.offline import plot as plotly_plot
import numpy as np


class ProcessNetworkTopology:
    """进程网络拓扑图生成器"""

    def __init__(self, pids: List[int], output_dir: str = "output"):
        """
        初始化拓扑图生成器

        Args:
            pids: 进程ID列表
            output_dir: 输出目录
        """
        self.pids = pids
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 网络图
        self.graph = nx.DiGraph()

        # 存储进程信息
        self.processes_info = {}

        # 存储网络连接信息
        self.connections = []

    def get_process_info(self, pid: int) -> Optional[Dict]:
        """
        获取进程信息

        Args:
            pid: 进程ID

        Returns:
            进程信息字典，如果进程不存在则返回None
        """
        try:
            proc = psutil.Process(pid)
            return {
                'pid': pid,
                'name': proc.name(),
                'cmdline': ' '.join(proc.cmdline()),
                'status': proc.status(),
                'create_time': proc.create_time()
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None

    def get_process_connections(self, pid: int) -> List[Dict]:
        """
        获取进程的网络连接

        Args:
            pid: 进程ID

        Returns:
            连接信息列表
        """
        try:
            proc = psutil.Process(pid)
            connections = []

            # 使用net_connections()替代已弃用的connections()
            for conn in proc.net_connections():
                conn_info = {
                    'pid': pid,
                    'family': conn.family,
                    'type': conn.type,
                    'local_addr': conn.laddr,
                    'remote_addr': conn.raddr,
                    'status': conn.status if hasattr(conn, 'status') else 'UNKNOWN'
                }
                connections.append(conn_info)

            return connections
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return []

    def get_process_tree(self) -> Dict[int, List[int]]:
        """
        获取进程树结构

        Returns:
            进程树字典 {父PID: [子PID列表]}
        """
        tree = defaultdict(list)
        existing_pids = set(self.pids)

        for pid in self.pids:
            try:
                proc = psutil.Process(pid)
                parent = proc.parent()
                if parent and parent.pid in existing_pids:
                    tree[parent.pid].append(pid)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        return dict(tree)

    def analyze_connections(self):
        """分析网络连接关系"""
        # 获取所有进程信息
        for pid in self.pids:
            proc_info = self.get_process_info(pid)
            if proc_info:
                self.processes_info[pid] = proc_info
                # 添加节点到图中
                self.graph.add_node(
                    pid,
                    label=f"{pid}\n({proc_info['name']})",
                    name=proc_info['name']
                )

        # 获取网络连接
        for pid in self.pids:
            connections = self.get_process_connections(pid)
            self.connections.extend(connections)

        # 添加连接边
        for conn in self.connections:
            if conn['remote_addr'] and conn['local_addr']:
                # 本地连接到其他进程的端口
                remote_ip, remote_port = conn['remote_addr']
                local_ip, local_port = conn['local_addr']

                # 检查远程IP是否对应其他监控的进程
                for other_pid in self.pids:
                    if other_pid != conn['pid']:
                        other_proc = self.get_process_info(other_pid)
                        if other_proc:
                            # 尝试通过端口匹配
                            # 这里简化处理，实际中可能需要更复杂的匹配逻辑
                            pass

                # 添加进程间的网络连接
                if conn['pid'] in self.processes_info:
                    # 创建虚拟节点表示外部连接
                    external_id = f"external_{conn['pid']}_{remote_port}"
                    if external_id not in self.graph:
                        self.graph.add_node(
                            external_id,
                            label=f"外部连接\n{remote_ip}:{remote_port}",
                            external=True
                        )

                    # 添加双向边
                    self.graph.add_edge(
                        conn['pid'],
                        external_id,
                        label=f"端口: {local_port} -> {remote_port}",
                        direction=conn['status']
                    )

    def get_port_connections(self) -> List[Tuple[int, int, str]]:
        """
        获取进程间端口通信关系

        Returns:
            (源PID, 目标PID, 端口信息) 元组列表
        """
        port_connections = []

        # 创建端口到进程的映射
        port_to_process = defaultdict(list)

        for pid in self.pids:
            connections = self.get_process_connections(pid)
            for conn in connections:
                if conn['local_addr']:
                    port = conn['local_addr'][1]
                    port_to_process[port].append(pid)

        # 查找监听同一端口的进程（可能的通信关系）
        for port, pids in port_to_process.items():
            if len(pids) > 1:
                for i in range(len(pids)):
                    for j in range(i + 1, len(pids)):
                        port_connections.append((pids[i], pids[j], f"端口 {port}"))

        return port_connections

    def build_topology(self):
        """构建完整的网络拓扑"""
        # 基础连接
        self.analyze_connections()

        # 添加进程树连接
        tree = self.get_process_tree()
        for parent_pid, child_pids in tree.items():
            for child_pid in child_pids:
                self.graph.add_edge(
                    parent_pid,
                    child_pid,
                    label="父子进程",
                    relationship="parent-child"
                )

        # 添加端口通信连接
        port_connections = self.get_port_connections()
        for src_pid, dst_pid, port_info in port_connections:
            self.graph.add_edge(
                src_pid,
                dst_pid,
                label=port_info,
                relationship="port-communication"
            )

    def visualize_matplotlib(self, output_file: str = None):
        """
        使用matplotlib绘制拓扑图

        Args:
            output_file: 输出文件名
        """
        if not output_file:
            output_file = self.output_dir / "process_topology.png"

        plt.figure(figsize=(16, 12))

        # 使用spring布局
        pos = nx.spring_layout(self.graph, k=3, iterations=50, seed=42)

        # 分别绘制不同类型的节点
        process_nodes = [n for n in self.graph.nodes() if not str(n).startswith('external_')]
        external_nodes = [n for n in self.graph.nodes() if str(n).startswith('external_')]

        # 绘制进程节点
        nx.draw_networkx_nodes(
            self.graph, pos,
            nodelist=process_nodes,
            node_color='lightblue',
            node_size=2000,
            alpha=0.8
        )

        # 绘制外部节点
        if external_nodes:
            nx.draw_networkx_nodes(
                self.graph, pos,
                nodelist=external_nodes,
                node_color='lightgray',
                node_size=1500,
                alpha=0.6,
                node_shape='s'
            )

        # 绘制边
        nx.draw_networkx_edges(
            self.graph, pos,
            edge_color='gray',
            arrows=True,
            arrowsize=20,
            arrowstyle='->',
            width=2,
            alpha=0.6
        )

        # 绘制标签
        labels = nx.get_node_attributes(self.graph, 'label')
        nx.draw_networkx_labels(self.graph, pos, labels, font_size=8, font_weight='bold')

        # 绘制边标签
        edge_labels = nx.get_edge_attributes(self.graph, 'label')
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels, font_size=6)

        # 添加图例
        process_patch = mpatches.Patch(color='lightblue', label='进程节点')
        external_patch = mpatches.Patch(color='lightgray', label='外部连接')
        plt.legend(handles=[process_patch, external_patch], loc='upper right')

        plt.title("进程网络拓扑图", fontsize=16, fontweight='bold', pad=20)
        plt.axis('off')
        plt.tight_layout()

        plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"✓ PNG拓扑图已保存到: {output_file}")
        plt.close()

    def visualize_plotly(self, output_file: str = None):
        """
        使用Plotly生成交互式HTML拓扑图

        Args:
            output_file: 输出文件名
        """
        if not output_file:
            output_file = self.output_dir / "process_topology.html"

        # 使用spring布局
        pos = nx.spring_layout(self.graph, k=3, iterations=50, seed=42)

        # 准备节点数据
        node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode='markers+text',
            hoverinfo='text',
            textposition="middle center",
            marker=dict(
                size=[],
                color=[],
                colorscale='Viridis',
                line=dict(width=2)
            )
        )

        for node in self.graph.nodes():
            x, y = pos[node]
            node_trace['x'] += tuple([x])
            node_trace['y'] += tuple([y])

            # 设置节点信息
            is_external = str(node).startswith('external_')
            node_label = self.graph.nodes[node].get('label', str(node))

            if is_external:
                node_trace['marker']['color'] += tuple(['lightgray'])
                node_trace['marker']['size'] += tuple([20])
            else:
                node_trace['marker']['color'] += tuple(['lightblue'])
                node_trace['marker']['size'] += tuple([30])

            node_trace['text'] += tuple([node_label])
            node_trace['hoverinfo'] += tuple(['text'])

        # 准备边数据
        edge_trace = []
        for edge in self.graph.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_trace.append(go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                mode='lines',
                line=dict(width=2, color='gray'),
                hoverinfo='none'
            ))

        # 创建图形
        fig = go.Figure(data=edge_trace + [node_trace],
                       layout=go.Layout(
                           title='进程网络拓扑图',
                           titlefont_size=16,
                           showlegend=False,
                           hovermode='closest',
                           margin=dict(b=20, l=5, r=5, t=40),
                           annotations=[dict(
                               text="节点: 进程PID和进程名<br>边: 网络连接关系",
                               showarrow=False,
                               xref="paper", yref="paper",
                               x=0.005, y=-0.002,
                               xanchor="left", yanchor="bottom",
                               font=dict(size=12)
                           )],
                           xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                       ))

        # 保存为HTML
        plotly_plot(fig, filename=str(output_file), auto_open=False)
        print(f"✓ HTML交互式拓扑图已保存到: {output_file}")

    def generate_report(self) -> str:
        """
        生成文本报告

        Returns:
            报告内容
        """
        report = []
        report.append("=" * 60)
        report.append("进程网络拓扑分析报告")
        report.append("=" * 60)
        report.append(f"\n分析时间: {psutil.boot_time()}")
        report.append(f"监控进程数量: {len(self.pids)}")

        # 进程信息
        report.append("\n" + "=" * 60)
        report.append("进程信息")
        report.append("=" * 60)
        for pid in self.pids:
            if pid in self.processes_info:
                info = self.processes_info[pid]
                report.append(f"\nPID: {pid}")
                report.append(f"  名称: {info['name']}")
                report.append(f"  命令: {info['cmdline']}")
                report.append(f"  状态: {info['status']}")

        # 网络连接
        report.append("\n" + "=" * 60)
        report.append("网络连接信息")
        report.append("=" * 60)
        for conn in self.connections:
            if conn['local_addr'] and conn['remote_addr']:
                local = f"{conn['local_addr'][0]}:{conn['local_addr'][1]}"
                remote = f"{conn['remote_addr'][0]}:{conn['remote_addr'][1]}"
                report.append(f"\nPID {conn['pid']}: {local} <-> {remote}")
                report.append(f"  状态: {conn['status']}")

        # 拓扑关系
        report.append("\n" + "=" * 60)
        report.append("网络拓扑关系")
        report.append("=" * 60)
        for edge in self.graph.edges(data=True):
            src, dst, data = edge
            label = data.get('label', 'Unknown')
            report.append(f"\n{src} --[{label}]--> {dst}")

        return "\n".join(report)

    def save_report(self, report: str, output_file: str = None):
        """
        保存报告到文件

        Args:
            report: 报告内容
            output_file: 输出文件名
        """
        if not output_file:
            output_file = self.output_dir / "topology_report.txt"

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"✓ 分析报告已保存到: {output_file}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='进程网络拓扑图生成器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 分析PID为1234和5678的进程
  python process_network_topology.py -p 1234 5678

  # 指定输出目录
  python process_network_topology.py -p 1234 5678 -o /tmp/topology

  # 只生成HTML格式
  python process_network_topology.py -p 1234 5678 --html-only

  # 只生成PNG格式
  python process_network_topology.py -p 1234 5678 --png-only
        """
    )

    parser.add_argument(
        '-p', '--pids',
        type=int,
        nargs='+',
        required=True,
        help='要分析的进程ID列表'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        default='output',
        help='输出目录 (默认: output)'
    )

    parser.add_argument(
        '--html-only',
        action='store_true',
        help='只生成HTML格式的交互式拓扑图'
    )

    parser.add_argument(
        '--png-only',
        action='store_true',
        help='只生成PNG格式的静态拓扑图'
    )

    parser.add_argument(
        '--report-only',
        action='store_true',
        help='只生成文本分析报告'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='显示详细信息'
    )

    args = parser.parse_args()

    # 验证PID
    valid_pids = []
    for pid in args.pids:
        try:
            if psutil.pid_exists(pid):
                valid_pids.append(pid)
            else:
                print(f"警告: PID {pid} 不存在", file=sys.stderr)
        except Exception as e:
            print(f"警告: 无法访问PID {pid}: {e}", file=sys.stderr)

    if not valid_pids:
        print("错误: 没有有效的PID可以分析", file=sys.stderr)
        sys.exit(1)

    if args.verbose:
        print(f"✓ 找到 {len(valid_pids)} 个有效进程")

    # 创建拓扑分析器
    topology = ProcessNetworkTopology(valid_pids, args.output)

    # 构建拓扑
    print("正在分析进程网络拓扑...")
    topology.build_topology()

    if args.verbose:
        print(f"✓ 发现 {len(topology.graph.nodes)} 个节点")
        print(f"✓ 发现 {len(topology.graph.edges)} 条边")

    # 生成报告
    report = topology.generate_report()

    # 保存报告
    topology.save_report(report)

    # 生成图形
    if not args.report_only:
        if not args.html_only:
            print("\n正在生成PNG拓扑图...")
            topology.visualize_matplotlib()

        if not args.png_only:
            print("正在生成HTML交互式拓扑图...")
            topology.visualize_plotly()

    print("\n✓ 分析完成!")


if __name__ == '__main__':
    main()
