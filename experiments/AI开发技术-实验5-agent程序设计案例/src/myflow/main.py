#!/usr/bin/env python
"""
Python程序设计课程学伴Agent实验协作 Flow。

本 Flow 对应实验5的5个分工职位（架构分析/部署测试/报告撰写/PPT设计/汇报）
依次产出 5 份实验材料，并保存到 output/ 目录。
"""

from pathlib import Path

from pydantic import BaseModel

from crewai.flow import Flow, listen, start

from myflow.crews.content_crew.content_crew import 实验协作Crew


class 实验协作状态(BaseModel):
    """实验协作 Flow 的全局状态。"""

    项目路径: str = "../coding-mentor-agent"
    架构分析: str = ""
    部署与沙箱测试方案: str = ""
    实验报告: str = ""
    PPT设计: str = ""
    汇报稿: str = ""


class 实验协作Flow(Flow[实验协作状态]):

    @start()
    def 初始化实验上下文(self, crewai_trigger_payload: dict | None = None):
        """收集实验上下文（项目路径、分工信息等）。"""
        print("=" * 60)
        print("Python程序设计课程学伴Agent实验协作 Flow 启动")
        print("=" * 60)

        if crewai_trigger_payload:
            self.state.项目路径 = crewai_trigger_payload.get(
                "项目路径", self.state.项目路径
            )
            print(f"使用触发器传入的项目路径: {self.state.项目路径}")
        else:
            print(f"使用默认项目路径: {self.state.项目路径}")

        print("\n5 个分工职位：")
        print("  A 架构分析师")
        print("  B 部署与沙箱测试员")
        print("  C 实验报告撰写员")
        print("  D PPT制作员")
        print("  E 汇报员")

    @listen(初始化实验上下文)
    def 运行实验协作Crew(self):
        """按顺序执行 5 个 Agent 的协作任务。"""
        print("\n开始执行实验协作 Crew ...")
        result = (
            实验协作Crew()
            .crew()
            .kickoff(
                inputs={
                    "project_path": self.state.项目路径,
                }
            )
        )

        print("实验协作 Crew 执行完毕，开始落盘。")

        outputs = [
            ("架构分析", "01-架构分析.md"),
            ("部署与沙箱测试方案", "02-部署与沙箱测试方案.md"),
            ("实验报告", "03-实验报告.md"),
            ("PPT设计", "04-PPT设计.md"),
            ("汇报稿", "05-汇报稿.md"),
        ]

        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)

        task_outputs = result.tasks_output
        for idx, (field_name, file_name) in enumerate(outputs):
            if idx < len(task_outputs):
                content = task_outputs[idx].raw
                setattr(self.state, field_name, content)
                with open(output_dir / file_name, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"  ✓ 已保存: output/{file_name}")

    @listen(运行实验协作Crew)
    def 生成实验总结(self):
        """输出实验协作 Flow 的最终总结。"""
        print("\n" + "=" * 60)
        print("实验协作 Flow 全部完成")
        print("=" * 60)
        print("\n产出文件（位于 output/ 目录）：")
        print("  1) 01-架构分析.md        —— 架构分析师(A)")
        print("  2) 02-部署与沙箱测试方案.md —— 部署与沙箱测试员(B)")
        print("  3) 03-实验报告.md         —— 实验报告撰写员(C)")
        print("  4) 04-PPT设计.md          —— PPT制作员(D)")
        print("  5) 05-汇报稿.md           —— 汇报员(E)")
        print("\n请将以上材料作为实验报告与汇报的素材。")


def kickoff():
    """以默认配置启动 Flow。"""
    实验协作Flow().kickoff()


def plot():
    """生成 Flow 的可视化图表。"""
    实验协作Flow().plot()


def run_with_trigger():
    """通过 JSON 触发器参数启动 Flow。"""
    import json
    import sys

    if len(sys.argv) < 2:
        raise Exception(
            "未提供触发器参数。请以 JSON 字符串作为参数传入，例如："
            ' python main.py \'{"项目路径": "../coding-mentor-agent"}\''
        )

    try:
        trigger_payload = json.loads(sys.argv[1])
    except json.JSONDecodeError as exc:
        raise Exception(f"触发器参数不是合法 JSON: {exc}") from exc

    flow = 实验协作Flow()
    try:
        return flow.kickoff({"crewai_trigger_payload": trigger_payload})
    except Exception as exc:
        raise Exception(f"使用触发器运行 Flow 时发生错误: {exc}") from exc


if __name__ == "__main__":
    kickoff()
