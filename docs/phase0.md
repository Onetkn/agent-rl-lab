# Phase 0 源码核查（2026-10-15）

证据：`upstream.lock.json` 中的两个本地 checkout；以下均为源码观察，不是运行结果。

## 关键发现

准确入口：art-notebooks 的 `examples/mcp-rl/mcp-rl.ipynb`。README 称之为 NWS 示例，但 Notebook 本身是通用 Smithery MCP 训练流程，配置说明推荐 Exa，`SMITHERY_MCP_URL` 留空，不能称作已经可运行的 NWS 天气复现。

模型为 `Qwen/Qwen2.5-3B-Instruct`，后端为 `LocalBackend(in_process=True, path='./.art')`。不要用 Serverless 示例的模型或环境替换它后仍称原样复现。

Notebook 非 Colab 安装 ART backend 0.5.9；Colab 安装 0.4.11；T4 分支固定 vLLM 0.9.2 / Triton 3.2.0。Unsloth 经 backend 依赖引入，但此 Notebook 没有完整锁定它。art-notebooks 根 pyproject 则引用 ART commit `88d3df23285f56fbcbb4629768ba0fc17ebe2d27`，不是 Notebook 环境。审查时 ART main 声明 Python >=3.12、Unsloth 2026.3.3；也不能与旧 Notebook 依赖随意拼接。目前没有经过解析和验证的训练 requirements lock。

有效 MAX_TURNS 是后一次赋值的 3，不是前面的 10。组内采样数为 4，每步 2 组。`max_training_steps` 在配置中声明，但当前训练循环未用它截断；后续 smoke test 必须显式限制实际训练调用次数。

场景生成在 `random.seed(42)` 之前发生并 shuffle，所以当前 Notebook 的 train/val 划分不能仅凭该 seed 复现，需先保存固定题集。

`complete_task` 设置的是 task_completed；`success` 在 rollout 初始化后没有真正的正确性判定。不能把自报完成当作任务成功。轨迹初始 reward 为 0，训练前由 `ruler_score_group` 评分；说明文字声称只看最终输出，但调用没有显式的最终输出过滤，应继续检查选定 ART 版本的 RULER 实现。

## 网络、模型与许可证

该 Notebook 需要 Smithery MCP URL、OpenRouter 的场景生成及 RULER judge；W&B 日志可选。没有提供具体 NWS endpoint，因此未做 NWS 连通性测试。不能据此断言国内网络可用或不可用。

模型 ID 指向 Hugging Face；实际缓存路径取决于执行机 HF 配置，尚未下载。Checkpoint 的后端根目录配置为 `./.art`。

两个上游仓库主许可证都是 Apache-2.0；Notebook 的安装与上传片段包含 LGPL-3.0 的 Unsloth 改编代码，见 art-notebooks 的 THIRD-PARTY-NOTICES 和 licenses。保留上游独立 checkout，后续若复制代码需保留相应声明。模型许可证需在实际选定 revision 时另核对。

## 最短复现路线

1. 明确 GPU 执行机（优先 Linux GPU）及可用预算，选择兼容的固定 ART 版本。此阶段尚未安装依赖。
2. 先确定真实 NWS MCP 服务与冻结任务；若改为本地确定性天气工具，注明是迁移实验。
3. 从 Notebook 拆出只推理入口，先执行一条真实轨迹，再扩展到 20 条固定评测。API/GPU 费用和时长需在执行环境明确后估算。
4. 保存 JSONL、错误和指标，人工核查轨迹。此时才能产生真实 metrics.csv 和 failure_cases。
5. 可选 1–3 个实际训练 step，测速后再决定短训练规模；冻结测试集比较 Base / RL。

当前花费：未使用 GPU、未发起模型或 judge 调用；仅下载源码和审查。实验运行日志与指标尚不存在。
