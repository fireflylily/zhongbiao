#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI标书系统性能基准测试工具
"""

import asyncio
import time
import json
import statistics
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import psutil
import sys
import threading
from dataclasses import dataclass
from typing import List, Dict, Tuple

# 测试配置
BASE_URL = "http://localhost:8082"
TEST_QUERIES = [
    "人工智能技术应用",
    "5G网络建设方案",
    "供应商管理系统",
    "企业数字化转型",
    "云计算平台架构",
    "大数据分析工具",
    "网络安全防护",
    "项目管理系统",
    "招标采购流程",
    "质量管理体系"
]

@dataclass
class PerformanceMetric:
    """性能指标数据类"""
    name: str
    response_times: List[float]
    success_rate: float
    throughput: float  # requests per second
    memory_usage: List[float]
    cpu_usage: List[float]
    error_count: int

class PerformanceBenchmark:
    """性能基准测试器"""

    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.metrics = {}
        self.system_monitor = SystemMonitor()

    def run_single_request_test(self):
        """单请求性能测试"""
        print("🔧 运行单请求性能测试...")

        response_times = []
        errors = 0

        for query in TEST_QUERIES:
            start_time = time.time()
            try:
                response = self.session.post(
                    f"{self.base_url}/api/vector_search/search",
                    json={"query": query, "top_k": 5, "threshold": 0.3},
                    timeout=10
                )
                response_time = time.time() - start_time

                if response.status_code == 200:
                    response_times.append(response_time)
                else:
                    errors += 1

            except Exception:
                errors += 1

        if response_times:
            self.metrics['single_request'] = PerformanceMetric(
                name="单请求测试",
                response_times=response_times,
                success_rate=(len(response_times) / len(TEST_QUERIES)) * 100,
                throughput=len(response_times) / sum(response_times) if response_times else 0,
                memory_usage=[],
                cpu_usage=[],
                error_count=errors
            )

            print(f"  ✅ 平均响应时间: {statistics.mean(response_times):.3f}s")
            print(f"  ✅ 成功率: {(len(response_times) / len(TEST_QUERIES)) * 100:.1f}%")

    def run_concurrent_test(self, concurrency_levels=[1, 5, 10, 20]):
        """并发请求性能测试"""
        print("⚡ 运行并发请求性能测试...")

        for concurrency in concurrency_levels:
            print(f"  测试并发级别: {concurrency}")

            # 启动系统监控
            self.system_monitor.start_monitoring()

            response_times = []
            errors = 0
            start_time = time.time()

            def make_concurrent_request():
                query = TEST_QUERIES[0]  # 使用固定查询避免结果差异
                try:
                    req_start = time.time()
                    response = self.session.post(
                        f"{self.base_url}/api/vector_search/search",
                        json={"query": query, "top_k": 5, "threshold": 0.3},
                        timeout=10
                    )
                    req_time = time.time() - req_start
                    return req_time, response.status_code == 200
                except Exception:
                    return time.time() - req_start, False

            with ThreadPoolExecutor(max_workers=concurrency) as executor:
                futures = [executor.submit(make_concurrent_request) for _ in range(concurrency * 2)]

                for future in as_completed(futures):
                    response_time, success = future.result()
                    if success:
                        response_times.append(response_time)
                    else:
                        errors += 1

            total_time = time.time() - start_time

            # 停止系统监控
            memory_usage, cpu_usage = self.system_monitor.stop_monitoring()

            if response_times:
                self.metrics[f'concurrent_{concurrency}'] = PerformanceMetric(
                    name=f"并发测试(x{concurrency})",
                    response_times=response_times,
                    success_rate=(len(response_times) / (concurrency * 2)) * 100,
                    throughput=len(response_times) / total_time,
                    memory_usage=memory_usage,
                    cpu_usage=cpu_usage,
                    error_count=errors
                )

                print(f"    ✅ 平均响应时间: {statistics.mean(response_times):.3f}s")
                print(f"    ✅ 吞吐量: {len(response_times) / total_time:.2f} req/s")
                print(f"    ✅ 成功率: {(len(response_times) / (concurrency * 2)) * 100:.1f}%")

    def run_stress_test(self, duration_seconds=30):
        """压力测试"""
        print(f"🚀 运行压力测试 ({duration_seconds}秒)...")

        self.system_monitor.start_monitoring()

        response_times = []
        errors = 0
        request_count = 0
        start_time = time.time()

        def stress_worker():
            nonlocal response_times, errors, request_count
            while time.time() - start_time < duration_seconds:
                try:
                    query = TEST_QUERIES[request_count % len(TEST_QUERIES)]
                    req_start = time.time()

                    response = self.session.post(
                        f"{self.base_url}/api/vector_search/search",
                        json={"query": query, "top_k": 5, "threshold": 0.3},
                        timeout=5
                    )

                    req_time = time.time() - req_start
                    request_count += 1

                    if response.status_code == 200:
                        response_times.append(req_time)
                    else:
                        errors += 1

                except Exception:
                    errors += 1

                time.sleep(0.1)  # 避免过度压测

        # 启动多个工作线程
        threads = []
        for _ in range(5):  # 5个并发工作线程
            thread = threading.Thread(target=stress_worker)
            thread.start()
            threads.append(thread)

        # 等待完成
        for thread in threads:
            thread.join()

        total_time = time.time() - start_time
        memory_usage, cpu_usage = self.system_monitor.stop_monitoring()

        if response_times:
            self.metrics['stress_test'] = PerformanceMetric(
                name="压力测试",
                response_times=response_times,
                success_rate=(len(response_times) / request_count) * 100 if request_count > 0 else 0,
                throughput=len(response_times) / total_time,
                memory_usage=memory_usage,
                cpu_usage=cpu_usage,
                error_count=errors
            )

            print(f"  ✅ 总请求数: {request_count}")
            print(f"  ✅ 成功请求: {len(response_times)}")
            print(f"  ✅ 平均响应时间: {statistics.mean(response_times):.3f}s")
            print(f"  ✅ 平均吞吐量: {len(response_times) / total_time:.2f} req/s")

    def generate_performance_report(self):
        """生成性能报告"""
        print("\n" + "="*60)
        print("📊 性能测试报告")
        print("="*60)

        report_data = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'test_results': {},
            'summary': {}
        }

        total_tests = len(self.metrics)
        performance_score = 0

        for test_name, metric in self.metrics.items():
            if not metric.response_times:
                continue

            avg_response_time = statistics.mean(metric.response_times)
            min_response_time = min(metric.response_times)
            max_response_time = max(metric.response_times)
            p95_response_time = sorted(metric.response_times)[int(len(metric.response_times) * 0.95)]

            # 计算性能评分 (响应时间越短分数越高)
            response_score = max(0, 100 - (avg_response_time * 100))
            throughput_score = min(100, metric.throughput * 10)
            success_score = metric.success_rate

            test_score = (response_score + throughput_score + success_score) / 3
            performance_score += test_score

            print(f"\n{metric.name}:")
            print(f"  平均响应时间: {avg_response_time:.3f}s")
            print(f"  响应时间范围: {min_response_time:.3f}s - {max_response_time:.3f}s")
            print(f"  95%响应时间: {p95_response_time:.3f}s")
            print(f"  吞吐量: {metric.throughput:.2f} req/s")
            print(f"  成功率: {metric.success_rate:.1f}%")
            print(f"  性能评分: {test_score:.1f}/100")

            if metric.memory_usage:
                avg_memory = statistics.mean(metric.memory_usage)
                max_memory = max(metric.memory_usage)
                print(f"  平均内存使用: {avg_memory:.1f} MB")
                print(f"  峰值内存使用: {max_memory:.1f} MB")

            if metric.cpu_usage:
                avg_cpu = statistics.mean(metric.cpu_usage)
                max_cpu = max(metric.cpu_usage)
                print(f"  平均CPU使用: {avg_cpu:.1f}%")
                print(f"  峰值CPU使用: {max_cpu:.1f}%")

            # 保存到报告数据
            report_data['test_results'][test_name] = {
                'avg_response_time': avg_response_time,
                'min_response_time': min_response_time,
                'max_response_time': max_response_time,
                'p95_response_time': p95_response_time,
                'throughput': metric.throughput,
                'success_rate': metric.success_rate,
                'performance_score': test_score,
                'memory_usage': {
                    'avg': statistics.mean(metric.memory_usage) if metric.memory_usage else 0,
                    'max': max(metric.memory_usage) if metric.memory_usage else 0
                },
                'cpu_usage': {
                    'avg': statistics.mean(metric.cpu_usage) if metric.cpu_usage else 0,
                    'max': max(metric.cpu_usage) if metric.cpu_usage else 0
                }
            }

        # 总体评分
        overall_score = performance_score / total_tests if total_tests > 0 else 0

        print(f"\n总体性能评分: {overall_score:.1f}/100")

        # 性能等级
        if overall_score >= 80:
            grade = "优秀"
        elif overall_score >= 60:
            grade = "良好"
        elif overall_score >= 40:
            grade = "及格"
        else:
            grade = "需要优化"

        print(f"性能等级: {grade}")

        report_data['summary'] = {
            'overall_score': overall_score,
            'grade': grade,
            'total_tests': total_tests
        }

        # 保存详细报告
        report_file = Path("performance_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)

        print(f"\n📄 详细性能报告已保存到: {report_file}")

        return overall_score >= 60  # 60分及格

    def run_all_tests(self):
        """运行所有性能测试"""
        print("🚀 开始AI标书系统性能基准测试...")
        print(f"目标服务器: {self.base_url}")
        print("-" * 60)

        start_time = time.time()

        try:
            # 基础性能测试
            self.run_single_request_test()

            # 并发性能测试
            self.run_concurrent_test()

            # 压力测试
            self.run_stress_test(duration_seconds=30)

        except KeyboardInterrupt:
            print("\n⚠️  测试被用户中断")
        except Exception as e:
            print(f"\n❌ 测试过程中出现异常: {str(e)}")

        total_time = time.time() - start_time
        print(f"\n性能测试完成，总耗时: {total_time:.1f}s")

        # 生成报告
        performance_acceptable = self.generate_performance_report()

        return performance_acceptable


class SystemMonitor:
    """系统资源监控器"""

    def __init__(self):
        self.monitoring = False
        self.memory_usage = []
        self.cpu_usage = []
        self.monitor_thread = None

    def start_monitoring(self):
        """开始监控"""
        self.monitoring = True
        self.memory_usage = []
        self.cpu_usage = []
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.start()

    def stop_monitoring(self):
        """停止监控并返回数据"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        return self.memory_usage.copy(), self.cpu_usage.copy()

    def _monitor_loop(self):
        """监控循环"""
        while self.monitoring:
            try:
                # 获取当前进程的资源使用情况
                process = psutil.Process()

                # 内存使用 (MB)
                memory_mb = process.memory_info().rss / 1024 / 1024
                self.memory_usage.append(memory_mb)

                # CPU使用率
                cpu_percent = process.cpu_percent()
                self.cpu_usage.append(cpu_percent)

                time.sleep(0.5)  # 每0.5秒采样一次
            except:
                break


def main():
    """主函数"""
    benchmark = PerformanceBenchmark()
    performance_acceptable = benchmark.run_all_tests()

    if performance_acceptable:
        print("\n🎉 系统性能达标！")
        sys.exit(0)
    else:
        print("\n⚠️  系统性能需要优化。")
        sys.exit(1)


if __name__ == "__main__":
    main()