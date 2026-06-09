"""
Python程序设计课程学伴Agent实验协作 Crew。

本 Crew 严格对应实验5小组5个分工职位：
- 架构分析师 (A)
- 部署与沙箱测试员 (B)
- 实验报告撰写员 (C)
- PPT制作员 (D)
- 汇报员 (E)
"""

from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task

from myflow.tools.custom_tool import (
    项目文件读取工具,
    知识库检索工具,
    部署命令生成工具,
)


@CrewBase
class 实验协作Crew:
    """Python程序设计课程学伴Agent实验协作 Crew。"""

    agents: list[BaseAgent]
    tasks: list[Task]

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def 架构分析师(self) -> Agent:
        return Agent(
            config=self.agents_config["架构分析师"],  # type: ignore[index]
            tools=[项目文件读取工具(), 知识库检索工具()],
            verbose=True,
        )

    @agent
    def 部署与沙箱测试员(self) -> Agent:
        return Agent(
            config=self.agents_config["部署与沙箱测试员"],  # type: ignore[index]
            tools=[项目文件读取工具(), 部署命令生成工具()],
            verbose=True,
        )

    @agent
    def 实验报告撰写员(self) -> Agent:
        return Agent(
            config=self.agents_config["实验报告撰写员"],  # type: ignore[index]
            verbose=True,
        )

    @agent
    def PPT制作员(self) -> Agent:
        return Agent(
            config=self.agents_config["PPT制作员"],  # type: ignore[index]
            verbose=True,
        )

    @agent
    def 汇报员(self) -> Agent:
        return Agent(
            config=self.agents_config["汇报员"],  # type: ignore[index]
            verbose=True,
        )

    @task
    def 架构分析任务(self) -> Task:
        return Task(
            config=self.tasks_config["架构分析任务"],  # type: ignore[index]
        )

    @task
    def 部署与沙箱测试任务(self) -> Task:
        return Task(
            config=self.tasks_config["部署与沙箱测试任务"],  # type: ignore[index]
        )

    @task
    def 实验报告撰写任务(self) -> Task:
        return Task(
            config=self.tasks_config["实验报告撰写任务"],  # type: ignore[index]
        )

    @task
    def PPT设计任务(self) -> Task:
        return Task(
            config=self.tasks_config["PPT设计任务"],  # type: ignore[index]
        )

    @task
    def 汇报稿撰写任务(self) -> Task:
        return Task(
            config=self.tasks_config["汇报稿撰写任务"],  # type: ignore[index]
        )

    @crew
    def crew(self) -> Crew:
        """创建实验协作 Crew（顺序执行）。"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
