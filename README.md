# Asterfire Skills

面向 Asterfire / Galileo / Adam Community 的技能集合，覆盖镜像构建、Kit 开发适配、Agent Toolbox、Workflow 发布调用与 Ent App 开发。当前提供五个入口，具体规则、脚本和模板按阶段读取。

## 安装

```bash
# 查看可用技能
npx skills add https://github.com/sidereus-ai/asterfire-skill.git --list

# 为 Codex 安装整套技能
npx skills add https://github.com/sidereus-ai/asterfire-skill.git -a codex -g -y
```

推荐整套安装，保持五个技能目录同级。Workflow 的 API 工具复用 DevOps 的公共客户端；DevOps 按任务需要读取 Kit、Workflow 或 Agent 的专业规则。

本地辅助工具使用 Python 3.10+；YAML 校验需要 PyYAML，可按 [Workflow requirements](asterfire-workflow-development/requirements.txt) 安装。平台 HTTP 客户端使用 Python 标准库。

## 五个技能的分工

| Skill | 职责 | 典型任务 |
| --- | --- | --- |
| [asterfire-platform-devops](asterfire-platform-devops/SKILL.md) | 唯一全链路编排入口；镜像开发、构建推送、SIF、发布与恢复 | 从项目到镜像、Kit，再到 Workflow；独立 Dockerfile、路径/权重检查、上传和调用调试 |
| [asterfire-kit-development](asterfire-kit-development/SKILL.md) | Kit 代码开发与原项目适配、审查和打包 | runner、最小表单、IO 端口、Demo、用户文案、报告、详情页、新版 ZIP 与六项验收 |
| [asterfire-workflow-development](asterfire-workflow-development/SKILL.md) | Workflow 专业开发、发布、调用和节点调试 | 多类节点、端口连接、节点级 scatter/gather、输入、相对路径产物和执行恢复 |
| [asterfire-agent-skill](asterfire-agent-skill/SKILL.md) | Agent Toolbox 与 ATP 工具开发 | 多 Tool、docstring、hooks、资源元数据、工具暴露和包结构 |
| [asterfire-ent-app-development](asterfire-ent-app-development/SKILL.md) | Ent 模块化 App 的开发、修改、验证与标准打包 | 复用 Kit/Workflow、可编辑表单、本地文件上传、示例填参、真实计算与结果交互 |

### 如何选择入口

- **完整交付**：使用 `$asterfire-platform-devops`。它按已有资产跳过完成阶段，推进镜像 → SIF → Kit 独立验证 → Workflow 验证。
- **仅开发或适配 Kit、交付 ZIP**：使用 `$asterfire-kit-development`。需要镜像或真实发布调试时由 DevOps 衔接。
- **已有 Kit 组装工作流**：使用 `$asterfire-workflow-development`。缺少 Kit/镜像时交回 DevOps 准备，上游可用后继续工作流。
- **Agent 工具开发**：使用 `$asterfire-agent-skill`；发布和外部调用由 DevOps 处理。
- **Ent 用户应用**：使用 `$asterfire-ent-app-development`，封装目标环境已有 Kit/Workflow；底层能力确有缺陷时再转交 Kit、Workflow 或 DevOps 技能。

每个入口遵循当前任务范围。只做本地代码、Dockerfile 或 YAML 时不会自动扩展为远程发布；端到端请求则继续完成约定的轻量调试。

## 镜像从平台实时查询

不再维护本地 SIF 名称注册表。使用支持 Open API v1 的 CLI 查询当前账号可见镜像，核对精确版本、依赖与目标集群 SIF 构建状态：

```bash
asterfire image list --json
asterfire image list --name <关键词> --json
asterfire image get <image_id> --json
asterfire image clusters --image-id <image_id> --json
```

原生 CLI 版本或路由不兼容时，DevOps 提供基于 `/api/open/v1` 的客户端及分页筛选工具。详情见 [平台镜像查询](asterfire-platform-devops/references/image-discovery.md)。开发者镜像列表受账号权限限制，不能当成所有公共/共享 SIF 的全集。项目仅记录本次选中镜像的 ID、版本和核验证据。

## 主要约定

- 镜像固化依赖、稳定第三方引擎、完整权重和运行资源；Kit ZIP 交付本项目的核心业务模块与入口。
- Kit 使用唯一 `runner(Tool)`，输入从 `kwargs['args']` 读取，表单字段与代码一致。输出端口包含实际类型和中文描述，与返回的字典实例 key 一致。
- 镜像路径、启动检查和权重验证统一在 DevOps 镜像阶段维护；平台入口依赖最终非交互环境中的 `bash`、`python` 与 `adam_community`。
- Workflow 节点不限于文件输入、Kit 和 Python 脚本；按目标部署契约使用其他类型与节点级 scatter。产物保存在当前节点目录，优先返回相对路径；跨节点通过输出端口或已核实的可读路径访问。
- 真实发布前核对环境、空间、版本、SIF 和权限。执行后按本次 execution/node/step 检查状态、日志和产物，不将“已提交”当成“已验证成功”。
- Token、密码和真实 `.env` 只放在本机受保护配置中，不提交到仓库、镜像或 ZIP。环境变量名称参考 [DevOps 示例](asterfire-platform-devops/.env.example)。

## Kit 用户文案与交付验收

Kit 概述、描述、中英文详情、输入说明、Demo 文案和 `report.md` 都会展示给用户，应说明能完成什么任务、如何提供输入、如何查看和理解结果。镜像复用、SIF 标签、接口声明、调试与测试通过记录放开发文档或日志；方法来源、关键参数、置信度和影响使用的限制仍须准确说明。具体边界与改写示例见 [用户文案与六项验收](asterfire-kit-development/references/user-content-and-acceptance.md)。

基于开源工具的 Kit，展示名称须保留上游工具的可识别名称并搭配中文用途。例如使用“AlphaFold 3 生物分子结构预测（CPU）”，不能仅写“生物分子结构预测（CPU）”。短描述和方法仍准确注明开放实现与实际权重来源；同步表单、详情页和报告中的工具身份，并在发布后核对平台实际名称。详见[开源工具的展示命名](asterfire-kit-development/references/user-content-and-acceptance.md#开源工具的展示命名)。

每次 Kit 新建、适配或修改完成后，开发者须执行测试与审查，并在交付说明中提交以下六项单选总结，每项附实际运行或审查证据：

| 序号 | 验收问题 | 单选选项 |
| --- | --- | --- |
| 1 | Demo 配置是否完整（GitHub 项目须核对上游官方案例）？ | 完整 / 不完整 |
| 2 | 交付的 Demo 配置是否能够正常使用？ | 是 / 否 |
| 3 | Kit 描述以及 input 描述是否用户友好？ | 是 / 否 |
| 4 | `report.md` 是否面向用户，且不含仅供开发者查看的内容？ | 是 / 否 |
| 5 | 主要结果是否真实、完整且可查看？ | 是 / 否 |
| 6 | 异常输入或运行失败时，是否有清楚提示且不会误报成功？ | 是 / 否 |

第 1 项选“完整”、第 2–6 项选“是”才通过。Demo 配置完整性检查不能替代实际运行，未完成验证须按未通过记录并说明原因。端到端任务还须验证平台运行、结果回流与展示。六项总结属于开发交付说明，不写入用户的运行报告；验收不扩大原任务的发布或计算范围。

## Ent App 的开发与交付

[Ent App 开发技能](asterfire-ent-app-development/SKILL.md) 使用当前官方 SDK 与服务端上下文封装平台能力，优先复用已有计算资产。当前默认目标环境为 `https://tob.sidereus-ai.com`；与主 Go 环境的身份和资产分开核对，名称和版本按实时清单识别，不跨环境硬编码编号。

- 统一源码仓库为 [asterfire-ent-apps](https://codeup.aliyun.com/sidereus-ai/galileo/asterfire-ent-apps)，应用放在 `apps/<app_id>/`；先读该仓库 README、AGENTS.md 和官方案例。
- 表单使用中文任务含义、单位与必要默认值，提供普通本地文件上传；计算所需归档由后台组装，云盘作为额外来源。
- “载入示例”填入同一张可见、可编辑表单及真实示例文件，不启动计算；用户检查或修改后再点击运行。
- 应用只封装 Kit/Workflow，展示真实进度、结果、历史及基于证据的追问；计算逻辑保留在平台能力中。
- 交付前检查页面、构建与安装包，并按当前授权完成目标环境的示例运行和结果回流。安装包内容变更升版本，具体包结构和检查器见技能正文。

以[官方开发者手册](https://sidereus-ai.feishuapp.com/app/app_17fw9154cxp)、当前 SDK 和仓库案例为接口依据；授权范围仅为文档或代码时，不自动启动线上发布与计算。

## 从旧版升级

当前仓库统一为上面的五个入口；旧镜像、路径检查和项目适配目录已合并，历史版本仍可从 Git 记录查看。对应关系如下：

| 旧入口/旧文档名称 | 新入口 |
| --- | --- |
| `Asterfire-kit-adapter` / `asterfire-kit-adapter` / `asterfire-project-to-kit-adapter` | `asterfire-kit-development` |
| `asterfire-dockerfile-builder` | `asterfire-platform-devops` 的镜像阶段 |
| `asterfire-image-rules` / `asterfire-image-path-calibrator` | `asterfire-platform-devops` 的路径与权重检查 |

更新安装后，若本机仍有旧的 `Asterfire-kit-adapter`、`Asterfire-dockerfile-builder` 或 `Asterfire-image-rules` 目录，先备份，再移出技能发现目录，避免新旧规则同时生效。旧镜像注册表不再迁入新技能；需要镜像时查询目标平台。

## 本地验证

平台和工作流测试均采用本地样例、临时目录或模拟请求，不调用生产计算：

```bash
cd asterfire-platform-devops
python -m unittest discover -s tests

cd ../asterfire-workflow-development
python -m unittest discover -s tests
```

Ent 安装包的只读检查命令见 [Ent Skill](asterfire-ent-app-development/SKILL.md)，仅验证技能或包结构时不会触发线上计算。

Kit 的表单、Demo 校验与项目分析命令见 [Kit Skill](asterfire-kit-development/SKILL.md)，镜像工具见 [镜像阶段](asterfire-platform-devops/references/image-lifecycle.md)。静态校验通过仍需在实际发布任务中检查构建结果、权限和最小真实案例。

## License

[MIT](LICENSE)。
