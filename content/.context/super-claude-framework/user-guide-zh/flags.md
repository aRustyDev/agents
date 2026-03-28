# SuperClaude 标志指南 🏁

**大多数标志会自动激活** - Claude Code 读取行为指令，根据您请求中的关键词和模式来调用适当的上下文。

## 基本自动激活标志（90% 的使用案例）

### 核心分析标志
| 标志 | 何时激活 | 作用 |
|------|---------------|--------------|
| `--think` | 5+ 个文件或复杂分析 | 标准结构化分析（约 4K 令牌）|
| `--think-hard` | 架构分析、系统依赖关系 | 深度分析（约 10K 令牌）配合增强工具 |
| `--ultrathink` | 关键系统重设计、遗留系统现代化 | 最大深度分析（约 32K 令牌）配合所有工具 |

### MCP 服务器标志
| 标志 | 服务器 | 目的 | 自动触发 |
|------|---------|---------|---------------|
| `--c7` / `--context7` | Context7 | 官方文档、框架模式 | 库导入、框架问题 |
| `--seq` / `--sequential` | Sequential | 多步推理、调试 | 复杂调试、系统设计 |
| `--magic` | Magic | UI 组件生成 | `/ui` 命令、前端关键词 |
| `--play` / `--playwright` | Playwright | 浏览器测试、E2E 验证 | 测试请求、视觉验证 |
| `--morph` / `--morphllm` | Morphllm | 批量转换、模式编辑 | 批量操作、样式强制执行 |
| `--serena` | Serena | 项目内存、符号操作 | 符号操作、大型代码库 |

### 行为模式标志
| 标志 | 何时激活 | 作用 |
|------|---------------|--------------|
| `--brainstorm` | 模糊请求、探索关键词 | 协作发现思维模式 |
| `--introspect` | 自我分析、错误恢复 | 透明地展现推理过程 |
| `--task-manage` | >3 步骤、复杂范围 | 通过委托进行协调 |
| `--orchestrate` | 多工具操作、性能需求 | 优化工具选择和并行执行 |
| `--token-efficient` / `--uc` | 上下文 >75%、效率需求 | 符号增强通信，减少 30-50% 令牌使用 |

### 执行控制标志
| 标志 | 何时激活 | 作用 |
|------|---------------|--------------|
| `--loop` | "improve"、"polish"、"refine" 关键词 | 迭代增强循环 |
| `--safe-mode` | 生产环境，>85% 资源使用 | 最大验证，保守执行 |
| `--validate` | 风险 >0.7，生产环境 | 执行前风险评估 |
| `--delegate` | >7 个目录或 >50 个文件 | 子智能体并行处理 |

## 特定命令标志

### 分析命令标志 (`/sc:analyze`)
| 标志 | 目的 | 值 |
|------|---------|--------|
| `--focus` | 针对特定领域 | `security`, `performance`, `quality`, `architecture` |
| `--depth` | 分析彻底程度 | `quick`, `deep` |
| `--format` | 输出格式 | `text`, `json`, `report` |

### 构建命令标志 (`/sc:build`)
| 标志 | 目的 | 值 |
|------|---------|--------|
| `--type` | 构建配置 | `dev`, `prod`, `test` |
| `--clean` | 构建前清理 | 布尔值 |
| `--optimize` | 启用优化 | 布尔值 |
| `--verbose` | 详细输出 | 布尔值 |

### 设计命令标志 (`/sc:design`)
| 标志 | 目的 | 值 |
|------|---------|--------|
| `--type` | 设计目标 | `architecture`, `api`, `component`, `database` |
| `--format` | 输出格式 | `diagram`, `spec`, `code` |

### 解释命令标志 (`/sc:explain`)
| 标志 | 目的 | 值 |
|------|---------|--------|
| `--level` | 复杂度级别 | `basic`, `intermediate`, `advanced` |
| `--format` | 解释风格 | `text`, `examples`, `interactive` |
| `--context` | 领域上下文 | 任何领域（如 `react`、`security`）|

### 改进命令标志 (`/sc:improve`)
| 标志 | 目的 | 值 |
|------|---------|--------|
| `--type` | 改进焦点 | `quality`, `performance`, `maintainability`, `style`, `security` |
| `--safe` | 保守方法 | 布尔值 |
| `--interactive` | 用户指导 | 布尔值 |
| `--preview` | 显示但不执行 | 布尔值 |

### 任务命令标志 (`/sc:task`)
| 标志 | 目的 | 值 |
|------|---------|--------|
| `--strategy` | 任务方法 | `systematic`, `agile`, `enterprise` |
| `--parallel` | 并行执行 | 布尔值 |
| `--delegate` | 子智能体协调 | 布尔值 |

### 工作流命令标志 (`/sc:workflow`)
| 标志 | 目的 | 值 |
|------|---------|--------|
| `--strategy` | 工作流方法 | `systematic`, `agile`, `enterprise` |
| `--depth` | 分析深度 | `shallow`, `normal`, `deep` |
| `--parallel` | 并行协调 | 布尔值 |

### 故障排除命令标志 (`/sc:troubleshoot`)
| 标志 | 目的 | 值 |
|------|---------|--------|
| `--type` | 问题类别 | `bug`, `build`, `performance`, `deployment` |
| `--trace` | 包含跟踪分析 | 布尔值 |
| `--fix` | 执行修复 | 布尔值 |

### 清理命令标志 (`/sc:cleanup`)
| 标志 | 目的 | 值 |
|------|---------|--------|
| `--type` | 清理目标 | `code`, `imports`, `files`, `all` |
| `--safe` / `--aggressive` | 清理强度 | 布尔值 |
| `--interactive` | 用户指导 | 布尔值 |
| `--preview` | 显示但不执行 | 布尔值 |

### 估算命令标志 (`/sc:estimate`)
| 标志 | 目的 | 值 |
|------|---------|--------|
| `--type` | 估算焦点 | `time`, `effort`, `complexity` |
| `--unit` | 时间单位 | `hours`, `days`, `weeks` |
| `--breakdown` | 详细分解 | 布尔值 |

### 索引命令标志 (`/sc:index`)
| 标志 | 目的 | 值 |
|------|---------|--------|
| `--type` | 索引目标 | `docs`, `api`, `structure`, `readme` |
| `--format` | 输出格式 | `md`, `json`, `yaml` |

### 反思命令标志 (`/sc:reflect`)
| 标志 | 目的 | 值 |
|------|---------|--------|
| `--type` | 反思范围 | `task`, `session`, `completion` |
| `--analyze` | 包含分析 | 布尔值 |
| `--validate` | 验证完整性 | 布尔值 |

### 生成命令标志 (`/sc:spawn`)
| 标志 | 目的 | 值 |
|------|---------|--------|
| `--strategy` | 协调方法 | `sequential`, `parallel`, `adaptive` |
| `--depth` | 分析深度 | `normal`, `deep` |

### Git 命令标志 (`/sc:git`)
| 标志 | 目的 | 值 |
|------|---------|--------|
| `--smart-commit` | 生成提交消息 | 布尔值 |
| `--interactive` | 引导操作 | 布尔值 |

### 工具选择命令标志 (`/sc:select-tool`)
| 标志 | 目的 | 值 |
|------|---------|--------|
| `--analyze` | 工具分析 | 布尔值 |
| `--explain` | 解释选择 | 布尔值 |

### 测试命令标志 (`/sc:test`)
| 标志 | 目的 | 值 |
|------|---------|--------|
| `--coverage` | 包含覆盖率 | 布尔值 |
| `--type` | 测试类型 | `unit`, `integration`, `e2e` |
| `--watch` | 监视模式 | 布尔值 |

## 高级控制标志

### 范围和焦点
| 标志 | 目的 | 值 |
|------|---------|--------|
| `--scope` | 分析边界 | `file`, `module`, `project`, `system` |
| `--focus` | 领域定向 | `performance`, `security`, `quality`, `architecture`, `accessibility`, `testing` |

### 执行控制
| 标志 | 目的 | 值 |
|------|---------|--------|
| `--concurrency [n]` | 控制并行操作 | 1-15 |
| `--iterations [n]` | 改进循环 | 1-10 |
| `--all-mcp` | 启用所有 MCP 服务器 | 布尔值 |
| `--no-mcp` | 仅使用本地工具 | 布尔值 |

### 系统标志（SuperClaude 安装）
| 标志 | 目的 | 值 |
|------|---------|--------|
| `--verbose` / `-v` | 详细日志 | 布尔值 |
| `--quiet` / `-q` | 静默输出 | 布尔值 |
| `--dry-run` | 模拟操作 | 布尔值 |
| `--force` | 跳过检查 | 布尔值 |
| `--yes` / `-y` | 自动确认 | 布尔值 |
| `--install-dir` | 目标目录 | 路径 |
| `--legacy` | 使用传统脚本 | 布尔值 |
| `--version` | 显示版本 | 布尔值 |
| `--help` | 显示帮助 | 布尔值 |

## 常用使用模式

### 前端开发
```bash
/sc:implement "responsive dashboard" --magic --c7
/sc:design component-library --type component --format code
/sc:test ui-components/ --magic --play
/sc:improve legacy-ui/ --magic --morph --validate
```

### 后端开发
```bash
/sc:analyze api/ --focus performance --seq --think
/sc:design payment-api --type api --format spec
/sc:troubleshoot "API timeout" --type performance --trace
/sc:improve auth-service --type security --validate
```

### 大型项目
```bash
/sc:analyze . --ultrathink --all-mcp --safe-mode
/sc:workflow enterprise-system --strategy enterprise --depth deep
/sc:cleanup . --type all --safe --interactive
/sc:estimate "migrate to microservices" --type complexity --breakdown
```

### 质量和维护
```bash
/sc:improve src/ --type quality --safe --interactive
/sc:cleanup imports --type imports --preview
/sc:reflect --type completion --validate
/sc:git commit --smart-commit
```

## 标志交互

### 兼容组合
- `--think` + `--c7`：带文档的分析
- `--magic` + `--play`：UI 生成带测试
- `--serena` + `--morph`：项目内存带转换
- `--safe-mode` + `--validate`：最大安全性
- `--loop` + `--validate`：带验证的迭代改进

### 冲突标志
- `--all-mcp` vs 单独的 MCP 标志（使用其中之一）
- `--no-mcp` vs 任何 MCP 标志（--no-mcp 获胜）
- `--safe` vs `--aggressive`（清理强度）
- `--quiet` vs `--verbose`（输出级别）

### 自动启用关系
- `--safe-mode` 自动启用 `--uc` 和 `--validate`
- `--ultrathink` 自动启用所有 MCP 服务器
- `--think-hard` 自动启用 `--seq` + `--c7`
- `--magic` 触发以 UI 为中心的智能体

## 标志故障排除

### 常见问题
- **工具过多**：使用 `--no-mcp` 仅用本地工具测试
- **操作太慢**：添加 `--uc` 压缩输出
- **验证阻塞**：在开发中使用 `--validate` 而不是 `--safe-mode`
- **上下文压力**：在 >75% 使用率时自动激活 `--token-efficient`

### 调试标志
```bash
/sc:analyze . --verbose                      # 显示决策逻辑和标志激活
/sc:select-tool "操作" --explain        # 解释工具选择过程
/sc:reflect --type session --analyze         # 审查当前会话决策
```

### 快速修复
```bash
/sc:analyze . --help                         # 显示命令的可用标志
/sc:analyze . --no-mcp                       # 仅本地执行
/sc:cleanup . --preview                      # 显示将被清理的内容
```

## 标志优先级规则

1. **安全第一**：`--safe-mode` > `--validate` > 优化标志
2. **显式覆盖**：用户标志 > 自动检测
3. **深度层次**：`--ultrathink` > `--think-hard` > `--think`
4. **MCP 控制**：`--no-mcp` 覆盖所有单独的 MCP 标志
5. **范围优先级**：system > project > module > file

## 相关资源
- [命令指南](commands.md) - 使用这些标志的命令
- [MCP 服务器指南](mcp-servers.md) - 理解 MCP 标志激活
- [会话管理](session-management.md) - 在持久会话中使用标志
