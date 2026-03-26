---
name: self-improving-assistant
description: 当你在多个会话中处理项目，并且希望 AI 能够学习项目特定知识、用户偏好和问题解决模式时使用。
---

# 自我进化的 AI 助手

## 概述

这个技能使 AI 能够自动积累关于项目、用户偏好和问题解决经验的知识。它使用存储在项目 memory 目录中的基于文件的记忆系统。

## 使用场景

- 用户提及偏好、编码风格或工作习惯
- 项目有特定的约定或架构模式
- 用户对 AI 的工作方式提供反馈（正面或负面）
- 解决了一个可能在未来会话中重复出现的问题
- 用户提到"记住"或"别忘了"

## 记忆系统结构

记忆系统位于：`{项目根目录}/.claude/memory/`

```
memory/
├── MEMORY.md           # 索引文件 - 始终首先加载
├── user_*.md          # 用户档案和偏好
├── project_*.md       # 项目特定知识
├── feedback_*.md      # 用户反馈和纠正
└── reference_*.md     # 外部系统引用
```

## 核心模式

### 1. 自动知识捕获

当你遇到重要信息时，立即保存：

```markdown
---
name: user_preference_snake_case
description: 用户偏好使用 snake_case 命名变量
type: user
---

**偏好：** snake_case 变量命名

**原因：** 用户明确说明了这个偏好

**如何应用：** 在代码中对所有变量使用 snake_case
```

### 2. 记忆索引 (MEMORY.md)

保持 MEMORY.md 简洁 - 只包含记忆文件的引用：

```markdown
# 记忆索引

- [user_role.md](user_role.md) - 用户的角色和专业知识水平
- [feedback_testing.md](feedback_testing.md) - 测试偏好
- [project_mcp_arch.md](project_mcp_arch.md) - MCP 服务器架构
```

### 3. 记忆类型

| 类型 | 内容 | 保存时机 |
|------|------|----------|
| **user** | 角色、专业知识、偏好、工作风格 | 当你了解用户时 |
| **project** | 目标、计划、bug、当前工作 | 当你了解项目背景时 |
| **feedback** | 纠正、确认、工作方式偏好 | 当用户批准或纠正时 |
| **reference** | 外部系统位置（Linear、Grafana 等） | 当用户提及外部工具时 |

### 4. 读取记忆

在每个会话开始时（或相关时），检查记忆：

```python
# 记忆加载的伪代码
memory_dir = 项目根目录 + "/.claude/memory/"
if exists(memory_dir + "MEMORY.md"):
    read(memory_dir + "MEMORY.md")  # 首先加载索引
    for 索引中的每个链接:
        read(链接)  # 加载引用的记忆文件
```

### 5. 写入记忆

使用 Write 工具，参考以下模板：

```markdown
---
name: {唯一标识符}
description: {用于搜索的一行描述}
type: {user|project|feedback|reference}
---

{内容（使用中文）}

**原因：** 为什么这很重要

**如何应用：** 这应该如何影响未来的行为}
```

## 快速参考

| 操作 | 方法 |
|------|------|
| 保存用户偏好 | 写入 `memory/user_*.md` |
| 保存项目背景 | 写入 `memory/project_*.md` |
| 保存反馈 | 写入 `memory/feedback_*.md` |
| 保存引用 | 写入 `memory/reference_*.md` |
| 加载记忆 | 首先读取 `memory/MEMORY.md` |
| 更新记忆 | 编辑现有文件或创建新文件 |

## 常见错误

1. **忘记保存** - 了解重要信息时立即保存
2. **保存过多** - 只保存非显而易见、项目特定的知识
3. **不加载记忆** - 在会话开始时检查 MEMORY.md
4. **保存到错误位置** - 使用项目特定的记忆，不是全局的
5. **忘记更新** - 当信息变化时，更新记忆文件

## 何时不使用

- 通用编程知识（记录在其他地方）
- 已在 CLAUDE.md 或 git 历史中的信息
- 临时的会话上下文
- 一次性的调试会话