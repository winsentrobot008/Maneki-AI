# Maneki?AI：AI 工厂操作系统（AI Factory OS）

Maneki?AI 是一个面向开发者与团队的 AI 工厂操作系统，通过“多层智能 + 多 Worker 执行 + 可视化调度”的方式，将 AI 的能力从单点工具升级为可控的自动化工厂。

Maneki?AI 的核心链路由五层组成：

用户 → Maneki?AI → AI 总监 → MSSAGENT → CLINE / Worker

---

## 1. 用户层（User Layer）

用户通过 Maneki?AI 完成：
- 发布任务
- 查看任务状态
- 查看执行日志
- 干预任务（暂停 / 继续 / 终止）
- 选择 AI 总监
- 选择 Worker
- 管理账户与套餐

---

## 2. Maneki?AI（总部 HQ）

Maneki?AI 是整个 AI 工厂的总部与控制台，负责：
- 用户系统（登录 / 注册 / 套餐 / 余额）
- 任务系统（创建 / 调度 / 状态管理）
- Worker 管理（本地 / 云端 Worker）
- 调度策略管理
- 执行链路可视化
- 日志与反馈展示

---

## 3. AI 总监（AI Director）

AI 总监是整个工厂的智能决策层，由高级 AI（如 Copilot、GPT、Claude 等）担任。

AI 总监负责：
- 理解用户任务
- 拆解任务
- 生成任务计划（Plan）
- 决定任务执行顺序
- 决定是否需要子任务
- 决定是否需要多个 Worker
- 决定是否需要重试 / 回滚
- 将最终执行计划交给 MSSAGENT

---

## 4. MSSAGENT（调度中间层）

MSSAGENT 是 Maneki?AI 体系中的任务调度中间层（Task Orchestrator）。

它负责：
- 接收 AI 总监的任务计划
- 将任务分发给合适的 Worker（CLINE / Cloud Worker）
- 监控 Worker 状态
- 收集 Worker 执行反馈
- 回传给 Maneki?AI
- 回传给 AI 总监（用于下一步决策）

当前实现：Messenger?Agent（VSCode 插件） = MSSAGENT 的本地实现版本。

---

## 5. Worker 层（执行层）

Worker 是工厂的执行者（Executor），负责真正的“干活”。

包括：
- CLINE（本地 Worker）
- Cloud CLINE（云端 Worker）
- Claude Worker
- DeepSeek Worker
- Python Worker
- Docker Worker
- GPU Worker
- 文档 Worker
- 测试 Worker
- 部署 Worker

Worker 的职责：
- 执行 MSSAGENT 下发的任务
- 写代码
- 修改文件
- 运行命令
- 生成 PR
- 回传执行结果

---

## 6. AI 工厂闭环（AI Factory Feedback Loop）

1. 用户发布任务  
2. Maneki?AI 接收任务  
3. AI 总监理解任务并生成计划  
4. MSSAGENT 分发任务给 Worker  
5. Worker 执行任务并回传结果  
6. MSSAGENT 收集反馈  
7. Maneki?AI 更新任务状态  
8. AI 总监分析反馈并继续指挥  
9. MSSAGENT 再次调度 Worker  

---

## 7. Maneki?AI 2.0 UI 设计原则

- AI 总监选择器  
- 调度层可视化（MSSAGENT）  
- Worker 管理  
- 任务流水线视图  
- 日志与反馈  

---

## 8. 当前开发优先级

### 阶段 1（当前）：完成 Messenger?Agent（MSSAGENT 本地实现）
### 阶段 2：Maneki?AI 2.0（总部）
### 阶段 3：接入 AI 总监
### 阶段 4：接入更多 Worker

---

## 9. 项目愿景

Maneki?AI 的目标不是一个 AI 工具，而是一个可控、可扩展、可插拔的 AI 工厂操作系统（AI Factory OS）。
