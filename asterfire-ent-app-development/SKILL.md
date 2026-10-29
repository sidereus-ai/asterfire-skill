---
name: asterfire-ent-app-development
description: "开发、修改、审查、调试、验证和标准打包 AsterFire Ent 模块化 App；按官方手册和应用仓库案例封装 tob.sidereus-ai.com 上的现有 Kit/Workflow，提供 indigo 主题、易懂表单、普通文件上传、后台自动归档、可见的一键示例填参、真实运行和结果交互。适用于 Ent App 页面、handler、Agent、结果回流及交付；单独的科学计算 Kit、DAG 或镜像开发交给对应平台技能。"
---

# AsterFire Ent 模块化 App 开发

把已有平台能力包装为用户看得懂、填得对、能运行并继续分析结果的 App。按当前请求选择开发、修复或交付环节；创建技能、做只读审查或改文案，不自动触发线上发布或计算。

## 用户明确的产品规则

1. **目标是 `https://tob.sidereus-ai.com`。** Kit、Workflow、文件传递和验收使用该环境的身份与资产。通过 Ent SDK / 服务端 `ctx` 调用，不把主 Go 环境的资产 ID 或登录状态混用进来。除非用户明确改目标，否则不回退到主 Go。
2. **主题沿用壳的 indigo。** 使用共享 Tailwind preset 与 `primary-*` 变量；用户后续指定新主题时按其要求调整。不要另造配色、渐变或自定义 CSS。
3. **用户不上传压缩包。** 即使计算入口要求 ZIP，也拆成普通文件选择和可编辑参数，由后端传输适配层按真实契约组装 ZIP。不得用 ZIP 上传框、手填云盘路径或浏览器偷偷打 ZIP 代替后端适配。云盘只作额外来源，本地文件必须可直接提交。
4. **参数对用户友好。** 中文任务含义、单位、必填性、合理默认值、有效示例和就地错误提示齐全；内部 JSON key、节点 ID、模板编号、归档目录不成为用户的任务。高级选项收起，必要参数仍可见。
5. **每个 App 都有完整可运行示例。** “载入示例”一次填入当前可见、可编辑的同一张表单和普通示例文件，并展开相关区块；不提交计算。用户看得见、改得动，再点“开始分析”提交当前值。禁止隐藏示例分支、仅展示摘要、跳过填表直接运行或用旧报告冒充新计算。
6. **App 只封装能力。** 科学计算与科学结论来自 Kit/Workflow；已由 Workflow 包含的 Kit 不再重复暴露或调用。不要扫描并展示别的 App 的流程来凑入口。

## 开工依据与范围

- 统一源码仓库：[asterfire-ent-apps](https://codeup.aliyun.com/sidereus-ai/galileo/asterfire-ent-apps)，工作区检出位置 `work/asterfire-ent-apps`，应用在 `apps/<app_id>/`。优先在现有应用目录修改；历史构建目录和交付源码仅供参考。
- 开发前读取当前仓库 README、适用 AGENTS.md，以及 `demo.workflow`、`demo.kit`、`intel.research` 的相关代码。接口与开发规范以[官方开发者手册](https://sidereus-ai.feishuapp.com/app/app_17fw9154cxp)为准，入口别名及离线资料见 [platform-contracts.md](references/platform-contracts.md)。
- 使用当前可读的最新手册与 SDK 源码核对接口；手册无法访问时说明所用快照日期与验证范围，不把“待发布”功能当成已上线。旧示例与本技能的明确用户要求冲突时，遵循用户要求。
- 先识别当前请求是 App 包装、底层能力缺陷，还是环境问题。不要为了包装现有 Workflow 重建镜像、复制算法或迁移资产。

## 工作流程

### 1. 查实当前 toB 契约

通过当前 SDK / `ctx`、CLI 和已授权身份，核对目标环境、Kit toolbox 名、Workflow 完整名称/别名、发布版本、输入节点及输出端口。环境清单只用于识别本 App 精确绑定的入口；运行时按名称/版本及输入契约识别并取得真实 ID，不让用户手填编号，不跨环境硬编码 ID。

模板不可见时依次核对发布、授权、调用身份、名称和版本匹配。不要仅凭空清单断言要迁移。模板可见也不能证明文件传输、镜像或真实运行可用。

把实际输入契约映射为“用户字段 → 校验 → 后端归档/输入节点 → 输出展示”，具体按 [input-and-demo.md](references/input-and-demo.md) 执行。先验证普通本地文件能经过后端传给计算入口，再围绕这个契约做页面。

### 2. 实现表单与传输适配

- 优先采用“左侧输入，右侧进度与结果”；先呈现完成任务所需的最少字段。文件类型、用途、格式样例和可选性说清楚；不要让用户制作机器配置或猜路径。
- 文件选择统一使用当前宿主支持的 SDK `FileSourceButton`，选择普通文件；可额外提供云盘来源。按真实支持能力实现上传、服务端归档、校验和平台提交，不臆造 SDK 方法或 `ctx` 扩展。同步 handler 超出平台限额时改走已支持的文件服务/异步传输适配，不能把负担退给用户。
- `App.tsx` 只装配；同一页面在组合层只创建一份 `useRun`、`useAgent`，向子组件传递。`PageProvider` 注册表单和表格；多表单使用唯一 ID。持久化及 URL 状态带 App id 前缀。
- 控件使用 antd / SDK，图标使用 lucide-react，`manifest.icon` 遵守壳白名单。`primary-*` 不加透明度后缀，边框显式 `border-solid`。不打包 SDK 副本，先核对宿主的组件兼容性。
- 页面通过 SDK hooks / client，handler 通过 `ctx` 访问平台；不裸写 fetch/axios、不直连数据库、不读取 Ent 私密配置。实现模式见 [platform-contracts.md](references/platform-contracts.md)。

### 3. 示例、Agent 与结果形成同一条路径

完整示例包含真实合法参数、全部必要普通文件及来源/合成数据标识；与用户输入共用校验、后端归档和提交函数。“载入示例”替换旧文件引用并清除过期派生状态，文件名与可读预览可见；编辑后的值必须进入实际提交。已有用户输入需覆盖时提供合适的提示，不能悄悄混入旧文件。

Agent 用字段说明解释参数、提出填写建议，用户接受后才更新表单。`@expose(agent=True)` 提供输入 schema；占算力或不可撤销的工具标 `confirm=True`，AGENT.md 写明需有用户授权。明确的运行按钮或本轮“提交测试”请求构成相应授权，不重复索要相同确认；仅要求创建技能或审查代码不构成运行授权。

提交后展示真实 run、节点进度、终态和产物。运行失败就停止“整理报告”等成功路径提示；用户可理解的原因优先，技术细节可展开。通过结果钩子持久化 run_id、实际参数快照及产物引用，支持报告、表格/结构、下载、历史和基于证据的追问；未生成的结果、缺失证据和模型意见明确区分。LLM 使用平台已配置连接，缺配置时如实提示；不把 API key 放进前端或安装包。

### 4. 做到可验证，而非只让按钮可点

按改动风险执行类型检查、构建和必要测试，重点覆盖输入转换、后台归档、示例装载/编辑/重置、提交一致性、终态错误及结果回流。别为简单文案写镜像式测试。

交付界面前在本地 Vite/Ent 预览实际查看布局、主题、可读性和交互；依据当前授权在 toB 用示例真实提交，确认计算完成、产物可读、结构化记录入库与追问可引用，检查其他 App 状态隔离。完整验收项见 [input-and-demo.md](references/input-and-demo.md)。不要把 fixture、缓存报告、模板可见或本地构建称作线上验收。

浏览器/账号/算力受阻时完成可做工作，准确区分已验证和未验证。遵守权限拦截，不用其他通道绕过；需要候选包例外时依据当前用户指令处理，不能把历史一次豁免当作以后永久免验。

### 5. 升版本并标准交付

先构建再用当前官方打包器打包（仓库示例 `asterbench pack --app <app目录> --out <安装包>`）。已发布的 `(app_id, version)` 不可覆盖，任何发布内容更新均升版本。安装 ZIP 只包含 `manifest.json`、`dist/`、`handlers/`、`agent/`、`schemas/`，路径用 `/`；这是给管理员安装的交付包，与禁止用户上传输入 ZIP 是两回事。

可运行本技能的只读检查器：

```text
python <本技能目录>/scripts/check_bundle.py <安装包.zip> --source <app源码目录> --app-id <app_id> --version <version>
```

检查器验证包结构、CRC、入口、manifest/schema 引用和源码目录运行文件一致性；不证明浏览器加载、科学结果或线上运行成功。另查 `remoteEntry.js` 及所有静态依赖存在、Module Federation 配置与宿主兼容、无凭据和运行状态泄漏。发布及重试规则见 [platform-contracts.md](references/platform-contracts.md)。

源码按仓库约定管理，不提交 `.env`、凭据、`.asterfire`、node_modules、dist 或安装 ZIP。交付安装包、源码位置/版本、简洁使用说明和实际验证证据；源码交接包与可安装 ZIP 分开标明。发布/安装/计算按当前授权执行，未知提交结果先查现有任务/版本再决定重试，避免重复消耗。

## 何时转交其他技能

- 真实 DAG、输入适配节点或科学依赖需改动：使用 [asterfire-workflow-development](../asterfire-workflow-development/SKILL.md)。
- Kit 的 runner、表单/输出契约或算法实现有缺陷：使用 [asterfire-kit-development](../asterfire-kit-development/SKILL.md)。
- 需要平台资产上传发布、镜像或完整生命周期：使用 [asterfire-platform-devops](../asterfire-platform-devops/SKILL.md)。明确传递目标 `tob.sidereus-ai.com`，不要沿用其他技能的主 Go 默认环境。

仅在确有底层工作时使用这些技能；不要因开发 App 自动扩大为重做全链路。
