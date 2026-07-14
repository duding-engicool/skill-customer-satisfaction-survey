# 客户质量满意度调查技能（customer-satisfaction-survey）

> 范式：交互引导式（纯文字版 .txt + Markdown .md）
> 面向客户质量经理与市场质量的客户满意度 / NPS 调查设计与分析工具。

## 一句话说明
产出专业问卷（CSAT/NPS/CES）与量化深度分析报告文档（txt+md）——这是"满意度度量"，区别于 VOC 的"痛点挖掘"。

## 适用角色
- 客户质量经理
- 市场质量

## 使用场景
- 年度/半年度客户质量满意度调查
- 新产品/新市场客户满意度摸底
- 重大客诉闭环后满意度回访
- 客户质量绩效（CQA）度量与汇报

## 与 VOC 的边界（重要）
| 维度 | VOC顾客声音分析 | 本技能 |
|------|----------------|--------|
| 目的 | 从客户原话挖掘痛点与需求（定性） | 结构化满意度度量（定量） |
| 产出 | CTQ、改善优先级 | CSAT/NPS/CES 得分、趋势、行动 |
| 关系 | 满意度低分维度的"下一步深挖" | 满意度量化"总览" |

## 标准度量
- **CSAT**：各维度 1–5 / 1–10 量表题
- **NPS**：0–10 推荐意愿，NPS = 推荐者% − 贬损者%
- **CES**：客户费力度，越低越好

## 文件清单
- `SKILL.md`：技能主文件
- `README.md`：本说明
- `scripts/build_report.py`：调查 JSON → 纯文字版 .txt + Markdown .md（问卷 + 分析一体）

## 使用方法
```bash
# 内置小样本直接跑通，产出示意 txt+md 双件
python scripts/build_report.py

# 用自有数据
python scripts/build_report.py --input survey.json --out-dir ./输出
```

## 联动技能
- supplier-assessment（满意度下滑逆向触发供应商专项评审）
- supplier-management-plan（纳入客户质量战略）
- VOC顾客声音分析 / voc-analysis（低分维度进一步定性深挖）

## 注意事项
- 所有分析数据须来自真实回收；示意数据标「待企业补充」；
- 不编造 NPS / 维度得分与行业基准；
- 本技能不替代真实调查发放与统计执行。
