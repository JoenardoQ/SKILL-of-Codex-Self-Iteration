# Codex 自迭代 Skill

[English](README.md)

`self-iteration` 是一个面向大型项目交付的 Agent Skill，适用于需要协调工程契约，
或者执行由用户明确授权、顺序推进的多轮优化。它会明确管理范围、权限、证据和轮次
状态，但不会把调用 Skill 当成修改外部系统的授权。

## 适用范围

当项目需要先完成基线交付、再进行一轮或多轮审慎优化，或者实现与文档需要按已确认的
工程契约对齐时，使用本 Skill。

一次性建议、普通小改动、仓库级通用政策或工具连接缺失不适用。

## 安装

让 Codex 从 GitHub 下载 Skill：

```text
使用 $skill-installer 安装
https://github.com/JoenardoQ/SKILL-of-Codex-Self-Iteration/tree/main/self-iteration
```

安装后新建一个 Codex 任务。不要把已安装 Skill 链接到开发检出目录；需要更新时应从
GitHub 重新安装。

## 运行时行为

本 Skill 将基线交付与优化轮次分开：

1. 基线阶段定义结果、协调文档契约、实现已批准工作并验证结果。
2. 每轮优化审查已授权范围，提出有证据支持的方案，等待用户选择，只实现被选中的
   工作，然后协调文档并明确关闭轮次。
3. 同一时间只能有一轮处于活动状态。等待、失败或验证受阻都不会自动关闭轮次。
4. 最后一轮还会执行有边界的仓库清理和远期审视。未来工作仍需单独授权。

选择本 Skill 不会授予工具、凭据、发布权限，也不会授权破坏性操作或外部写入。

## 状态与隐私

默认使用宿主或任务状态恢复工作。只有在用户授权持久化项目内交接时，才会把运行时
模板 `self-iteration/assets/iteration-state.md` 复制到目标项目。生成的状态属于
目标项目，可能包含项目历史，因此目标项目的维护者必须自行决定保留与发布策略。

本源码仓库不发布自身的迭代台账、轮次报告、运行时清单、模型转录、评审决定或生成的
评测结果。这些内容由忽略规则限制在本地。

## 仓库内容

```text
SKILL-of-Codex-Self-Iteration/
├── .gitignore
├── README.md
├── README.zh-CN.md
├── LICENSE
├── evaluation/
│   └── eval-spec.json
├── release-policy.json
├── scripts/
│   ├── runtime_revision.py
│   ├── test_control_evidence_validator.py
│   ├── test_repo_validator.py
│   ├── test_runtime_revision.py
│   └── validate_repo.py
└── self-iteration/
    ├── SKILL.md
    ├── agents/openai.yaml
    ├── assets/iteration-state.md
    └── references/
        ├── final-round.md
        ├── review-matrix.md
        └── round-protocol.md
```

只有 `self-iteration/` 会被安装。评测规格、验证脚本、测试和发布策略是维护者资源。
评测规格包含计划中的合成案例和验收条件，不是评测运行结果。

## 维护者评测

生成的评测材料不得进入 Git。支持的本地路径包括
`evaluation/evidence/`、`evaluation/results/`、`evaluation/raw/` 和
`evaluation/runtime-manifest.json`。

公开检出目录不包含这些路径时，仓库验证器仍可通过。如果维护者生成了完整的本地清单
或证据语料，验证器会检查其内容，而不是静默忽略格式错误的数据。

## 验证与打包

运行公开仓库检查：

```bash
python3 -B scripts/validate_repo.py
python3 -B scripts/test_repo_validator.py
python3 -B scripts/test_runtime_revision.py
python3 -B scripts/test_control_evidence_validator.py
```

生成并检查仅保存在本地的运行时清单：

```bash
python3 -B scripts/runtime_revision.py write \
  --runtime-root self-iteration \
  --manifest evaluation/runtime-manifest.json
python3 -B scripts/runtime_revision.py check \
  --runtime-root self-iteration \
  --manifest evaluation/runtime-manifest.json
```

如果 Agent Skill Author 已安装在 `$CODEX_HOME` 下，可以验证并打包运行时目录：

```bash
python3 "$CODEX_HOME/skills/agent-skill-author/scripts/validate_skill.py" \
  self-iteration --policy release-policy.json
python3 "$CODEX_HOME/skills/agent-skill-author/scripts/validate_eval_spec.py" \
  evaluation/eval-spec.json
python3 "$CODEX_HOME/skills/agent-skill-author/scripts/package_skill.py" \
  self-iteration --output /tmp/self-iteration.zip \
  --receipt /tmp/self-iteration-receipt.json --policy release-policy.json
python3 "$CODEX_HOME/skills/agent-skill-author/scripts/verify_package.py" \
  --receipt /tmp/self-iteration-receipt.json \
  --archive /tmp/self-iteration.zip
```

## 限制

静态验证能够检查结构、引用、策略、Fixture 和仓库边界，但不能证明宿主发现、Skill
选择、行为改进、外部副作用或跨宿主可移植性。这些结论需要在每个目标宿主中重新运行
并接受独立审查。

## 许可证

[MIT](LICENSE)
