# Python程序设计课程学伴Agent — 角色B交付物清单

> **角色：张帅（部署与沙箱测试员）**
> 唯一需要完整运行系统的人，承担最多的实操任务。

---

## 交付进度总览

| 序 | 任务 | 交付物 | 状态 |
|:--:|:---|:---|:--:|
| 1 | 一键安装脚本 | [coding-mentor-agent/install.bat](coding-mentor-agent/install.bat) | ✅ 已完成 |
| 2 | 环境信息记录 | [coding-mentor-agent/环境信息.txt](coding-mentor-agent/环境信息.txt) | ✅ 已完成 |
| 3 | 部署录屏 | `screenshots/部署录屏.mp4` | ✅ 已完成 |
| 4 | 系统启动截图 | [screenshots/01-诊断首页-字典题目.png](screenshots/01-诊断首页-字典题目.png) | ✅ 已完成 |
| 5 | 学习闭环截图 | [screenshots/学习闭环/](screenshots/学习闭环/) | ✅ 已完成（10张） |
| 6 | 6类沙箱测试 | [screenshots/沙箱测试/](screenshots/沙箱测试/) | ✅ 已完成（15张：正常输出×2、语法错误×2、运行时错误、超时终止、写文件拦截、网络隔离、文件读取、pytest断言 + 过程记录5张） |
| 7 | 沙箱安全配置 | [docs/沙箱安全配置.md](docs/沙箱安全配置.md) | ✅ 已完成 |
| 8 | 单元测试日志 | [docs/单元测试记录.md](docs/单元测试记录.md) | ✅ 已完成 |
| 9 | 学生回路测试 | [docs/学生回路测试.md](docs/学生回路测试.md) | ✅ 已完成 |
| 10 | 5类风险验证 | [docs/风险验证记录.md](docs/风险验证记录.md) | ✅ 已完成 |
| 11 | 数据库表记录 | [docs/数据库表内容.md](docs/数据库表内容.md) | ✅ 已完成 |

---

## 详细清单

### 1. 一键安装脚本
- **文件**: [coding-mentor-agent/install.bat](coding-mentor-agent/install.bat)
- **说明**: Windows 一键安装脚本，自动检查环境 → 安装依赖 → 构建 Docker 镜像 → 启动服务

### 2. 环境信息
- **文件**: [coding-mentor-agent/环境信息.txt](coding-mentor-agent/环境信息.txt)
- **内容**: OS、Node.js、npm、Docker、Git、WSL 版本信息

### 3. 部署录屏
- **文件**: `screenshots/部署录屏.mp4`
- **内容**: 从运行 install.bat 到浏览器打开 http://127.0.0.1:3000 的完整过程

### 4. 系统启动截图
- **文件**: [screenshots/01-诊断首页-字典题目.png](screenshots/01-诊断首页-字典题目.png)
- **内容**: 浏览器打开后的初始诊断页面（Python字典选择题）

### 5. 学习闭环截图
- **目录**: [screenshots/学习闭环/](screenshots/学习闭环/)

| 序号 | 文件 | 内容 |
|:--:|:---|:---|
| 01 | 01-诊断-元组解包-已答10题.png | 诊断题：元组解包 `a, *b, (c,) = data` |
| 02 | 02-诊断-CSV文件处理-已答25题.png | 诊断题：CSV scores.csv 过滤排序 |
| 03 | 03-测评反馈-学习起点确定.png | 测评反馈：学习起点 = CSV数据处理 |
| 04 | 04-测评反馈-开始导师指导.png | 测评反馈详情 + "开始导师指导"按钮 |
| 05 | 05-导师指导-表达式概念入门.png | 导师开始讲解Python表达式与REPL |
| 06 | 06-导师指导-print函数讨论.png | 导师引导讨论print()函数与变量 |
| 07 | 07-系统错误-guided_question_missing.png | DeepSeek模型生成无效action_kind |
| 08 | 08-系统错误-多次结构校验失败.png | 多次动作验证失败 |
| 09 | 09-导师指导-数据类型表格讲解.png | 导师展示数据类型汇总表格 |
| 10 | 10-导师指导-动态类型问答.png | 动态类型讨论，学生正确回答 |

### 6. 6类沙箱边界测试
- **目录**: [screenshots/沙箱测试/](screenshots/沙箱测试/)

| 序号 | 测试类型 | 文件 | 状态 |
|:--:|:---|:---|:--:|
| 1 | 正常输出 | 05-正常输出-passed-HelloPython.png | ✅ `print("Hello, Python!")` / `print(2+3)` → passed |
| 2 | 正常输出 | 08-正常输出-passed-HelloWorld.png | ✅ `print("Hello World!")` → passed |
| 3 | 语法错误 | 06-语法错误-括号未闭合.png | ✅ `print("hello")` → SyntaxError: '(' was never closed |
| 4 | 语法错误 | 07-语法错误-中文括号U+FF08.png | ✅ 中文全角括号 → SyntaxError: invalid character |
| 5 | 运行时错误 | 09-运行时错误-ZeroDivisionError.png | ✅ `x = 1/0` → ZeroDivisionError: division by zero |
| 6 | 超时终止 | 10-超时终止-whileTrue.png | ✅ `while True: pass` → status=timeout |
| 7 | 写文件拦截 | 12-写文件拦截-ReadOnly文件系统.png | ✅ `open('/test.txt','w')` → OSError: Read-only file system |
| 8 | 网络隔离 | 13-网络隔离拦截-urllib被阻止.png | ✅ `urllib.request.urlopen()` → 网络被拦截 |
| 9 | 文件读取 | 11-文件读取-etc-passwd-passed.png | ⚠️ `/etc/passwd`可读（世界可读文件） |
| 10 | pytest评测 | 15-pytest断言测试-AllTestsPassed.png | ✅ `def add(a,b)` + assert测试 → All tests passed! |

附加截图（沙箱访问过程记录）:

| 文件 | 内容 |
|:---|:---|
| 01-诊断错误-concepts_outside_frontier.png | 导师动作被拒：概念越界 |
| 02-导师对话-要求进入沙箱.png | 学生多次要求进入沙箱练习 |
| 03-导师对话-沙箱练习讨论.png | 讨论沙箱练习相关问题 |
| 04-练习界面-Using-Python-as-Calculator.png | 练习卡片出现：add(a,b)函数 |

### 7. 沙箱安全配置
- **文件**: [docs/沙箱安全配置.md](docs/沙箱安全配置.md)
- **内容**: 13项Docker安全参数（网络隔离、内存限制128MB、PID限制64、Linux capabilities丢弃、只读文件系统、非root用户、超时配置等），含完整docker run命令和状态推断逻辑
- **验证**: 所有安全机制已通过6类沙箱测试实际验证

### 8. 单元测试记录
- **文件**: [docs/单元测试记录.md](docs/单元测试记录.md)
- **内容**: Vitest v4.1.6 运行结果，29个测试文件、274个测试用例，265通过（96.7%），9个失败均为环境/文档缺失（非代码缺陷）
- **关键结果**: 安全测试、前端XSS测试、真实沙箱集成测试全部通过

### 9. 学生回路测试
- **文件**: [docs/学生回路测试.md](docs/学生回路测试.md)
- **内容**: 协议层16/20测试通过，含学生回路策略层次（local→strict→realistic→full-realistic→security→release）、16个学生Actor动作、7层Oracle、9个严格矩阵场景、5种Persona定义
- **注意**: Python E2E测试需playwright环境

### 10. 5类风险验证
- **文件**: [docs/风险验证记录.md](docs/风险验证记录.md)
- **内容**: 5类风险全部验证通过
  1. 提示注入防护 — 本地安全拒绝 + 安全事件审计
  2. 越权工具调用拦截 — 工具门禁 + 导师动作校验
  3. 不安全代码执行拦截 — Docker多层隔离 + 6项实际测试
  4. XSS 防护 — 前端纯文本渲染 + 输出脱敏
  5. 隐藏测试泄露防护 — 信封过滤 + 策略隔离 + 禁止词

### 11. 数据库表内容
- **文件**: [docs/数据库表内容.md](docs/数据库表内容.md)
- **内容**: 11张表的实际行数和内容记录，含agent_sessions(2)、session_messages(117)、tool_evidence(83)、tutor_agent_actions(89)、concept_mastery(21)等，证实系统学习状态持久化正常

---

## 目录结构

```
项目根目录/
├── coding-mentor-agent/     # 系统源码 + install.bat + 环境信息.txt
├── screenshots/             # 所有截图和录屏
│   ├── 部署录屏.mp4
│   ├── 01-诊断首页-字典题目.png
│   ├── 学习闭环/            # 学习闭环10张截图
│   └── 沙箱测试/            # 沙箱测试8张截图（含过程记录）
├── docs/                    # 所有文档类交付物（全部完成）
│   ├── 沙箱安全配置.md       ✅
│   ├── 单元测试记录.md       ✅
│   ├── 学生回路测试.md       ✅
│   ├── 风险验证记录.md       ✅
│   └── 数据库表内容.md       ✅
└── README.md                # 本文件
```

---

> 张帅加油！你是全组唯一真正把系统跑起来的人，你的每一个截图和记录都是全组的硬证据。
