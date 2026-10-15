# OpenPipe ART 多轮 Agent 复现

当前阶段：源码审查完成初稿；尚未安装训练依赖、调用模型、采集轨迹或训练。

## 从这里开始

在 VS Code 中打开 `upstream/art-notebooks/examples/mcp-rl/mcp-rl.ipynb`，先阅读，不要 Run All。该 Notebook 把模型注册、rollout 定义和训练放在同一个单元，直接运行会启动训练。

运行零依赖的本地源码检查：

```powershell
python experiments/inspect_notebook.py
```

这只读取本地文件，不导入 ART，不执行 Notebook，不访问模型服务。

## 目录

- `experiments/inspect_notebook.py`：定位配置、rollout、评分和训练所在单元。
- `experiments/config.yaml`：拟定实验配置，未运行。
- `docs/phase0.md`：源码核查结果与后续路线。
- `upstream.lock.json`：审查使用的两个上游 commit。
- `upstream/`：本地上游源码，独立 Git 仓库，不上传到本项目。

## 恢复上游源码

```powershell
git clone https://github.com/OpenPipe/art-notebooks.git upstream/art-notebooks
git -C upstream/art-notebooks checkout 74c819447bd1e03318369d30fc0acb0f1106d5b6
git clone https://github.com/OpenPipe/ART.git upstream/ART
git -C upstream/ART checkout c7dda222015f728cf625fbb9719b2152dfd41d24
```

## 第一课：一条轨迹是什么

模型读取任务和工具 schema，输出工具名称及参数；MCP 执行工具，把 observation 加回消息历史；模型基于新历史继续行动，直至结束或达到轮数上限。这整个过程是一条 rollout，保存后的消息、动作、奖励等构成 trajectory。

同一道题采样多个 rollout 组成一个 group。示例用 RULER 对组内轨迹评分，再将带奖励的轨迹交给训练后端。模型宣布 `complete_task` 只代表它认为完成了，不能当作正确率。

阅读时思考：为什么工具返回结果必须加入消息历史？为什么调用了 `complete_task` 仍可能回答错误？

所有实验结论必须来自实际日志。当前没有实验指标。
