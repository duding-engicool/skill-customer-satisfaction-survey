#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
客户质量满意度调查生成与分析器
读入结构化调查 JSON，生成纯文字版 (.txt) + Markdown (.md) 双件文档。
同时产出"问卷卷首 + 量化分析报告"。

用法：
  python build_report.py --input survey.json --out-dir ./输出
  python build_report.py                                 # 内置小样本，直接产出示意双件

输入 JSON 结构：
{
  "project": "2026上半年客户质量满意度调查",
  "owner": "客户质量部",
  "objectives": ["目标1","目标2"],
  "survey": {
    "scale": "1-5",                      # CSAT 量表
    "dimensions": [{"name":"产品质量","items":["题目1","题目2"]}],
    "nps_question": "您有多大可能向同行推荐我们？(0-10)",
    "ces_question": "您解决问题平均花费的精力？",
    "open_questions": ["还有什么建议？"]
  },
  "analysis": {
    "respondents": 120,
    "nps": {"promoters":45,"passives":50,"detractors":25},
    "dimension_scores": [{"name":"产品质量","score":4.2,"outof":5}],
    "trend": "同比变化说明",
    "key_findings": ["发现1","发现2"],
    "actions": ["行动1","行动2"]
  },
  "pending": ["待企业补充项"]
}
"""

import argparse
import json
import os
import sys
from datetime import datetime


def load_survey(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def compute_nps(nps):
    p = nps.get("promoters", 0)
    pa = nps.get("passives", 0)
    d = nps.get("detractors", 0)
    total = p + pa + d
    if total <= 0:
        return 0, 0.0, 0.0
    prom_pct = p * 100.0 / total
    det_pct = d * 100.0 / total
    return round(prom_pct - det_pct, 1), round(prom_pct, 1), round(det_pct, 1)


def build_md(sv):
    an = sv.get("analysis", {})
    nps = an.get("nps", {})
    nps_val, prom_pct, det_pct = compute_nps(nps)
    L = []
    L.append(f"# {sv.get('project','客户质量满意度调查')}\n")
    L.append("## 第一部分：调查问卷\n")
    L.append(f"- 责任部门：{sv.get('owner','')}")
    L.append(f"- 调查目标：{('；'.join(sv.get('objectives',[])) or '（待企业补充）')}")
    L.append(f"- 量表：{sv.get('survey',{}).get('scale','1-5')}\n")
    L.append("### 一、满意度维度题（CSAT）\n")
    for dim in sv.get("survey", {}).get("dimensions", []) or []:
        L.append(f"**{dim.get('name','')}**")
        for it in dim.get("items", []) or []:
            L.append(f"- {it} 〔{sv.get('survey',{}).get('scale','1-5')}分制〕")
    L.append("")
    L.append(f"### 二、NPS 推荐意愿题\n- {sv.get('survey',{}).get('nps_question','推荐意愿(0-10)')}")
    L.append(f"### 三、CES 费力度题\n- {sv.get('survey',{}).get('ces_question','费力度')}")
    L.append("### 四、开放题")
    for oq in sv.get("survey", {}).get("open_questions", []) or []:
        L.append(f"- {oq}")
    L.append("")
    L.append("## 第二部分：分析报告\n")
    L.append(f"- 有效样本：{an.get('respondents','（待企业补充）')}")
    L.append(f"- **NPS（净推荐值）：{nps_val}**（推荐者 {prom_pct}% / 贬损者 {det_pct}%）\n")
    L.append("### 维度得分\n")
    L.append("| 维度 | 得分 | 量表上限 |")
    L.append("|------|------|----------|")
    for ds in an.get("dimension_scores", []) or []:
        L.append(f"| {ds.get('name','')} | {ds.get('score','')} | {ds.get('outof','')} |")
    L.append("")
    L.append(f"### 趋势\n{an.get('trend','（待企业补充）')}\n")
    L.append("### 关键发现\n")
    for k in an.get("key_findings", []) or []:
        L.append(f"- {k}")
    if not an.get("key_findings"):
        L.append("- （待企业补充）")
    L.append("\n### 行动建议\n")
    for a in an.get("actions", []) or []:
        L.append(f"- {a}")
    if not an.get("actions"):
        L.append("- （待企业补充）")
    pend = sv.get("pending", [])
    if pend:
        L.append("\n### 待企业补充项\n")
        for x in pend:
            L.append(f"- 〔待企业补充〕{x}")
    L.append(f"\n> 本报告由客户质量满意度调查技能生成 · {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    return "\n".join(L)


def build_txt(sv):
    an = sv.get("analysis", {})
    nps = an.get("nps", {})
    nps_val, prom_pct, det_pct = compute_nps(nps)
    sep = "=" * 48
    sub = "-" * 48
    L = []
    L.append(sep)
    L.append(sv.get("project", "客户质量满意度调查"))
    L.append(sep)
    L.append(f"责任部门：{sv.get('owner','')}")
    L.append(f"调查目标：{('；'.join(sv.get('objectives',[])) or '（待企业补充）')}")
    L.append(f"量表：{sv.get('survey',{}).get('scale','1-5')}")
    L.append("")
    L.append("第一部分：调查问卷")
    L.append(sub)
    L.append("一、满意度维度题（CSAT）")
    for dim in sv.get("survey", {}).get("dimensions", []) or []:
        L.append(f"【{dim.get('name','')}】")
        for it in dim.get("items", []) or []:
            L.append(f"  - {it} 〔{sv.get('survey',{}).get('scale','1-5')}分制〕")
    L.append("")
    L.append(f"二、NPS 推荐意愿题：{sv.get('survey',{}).get('nps_question','推荐意愿(0-10)')}")
    L.append(f"三、CES 费力度题：{sv.get('survey',{}).get('ces_question','费力度')}")
    L.append("四、开放题：")
    for oq in sv.get("survey", {}).get("open_questions", []) or []:
        L.append(f"  - {oq}")
    L.append("")
    L.append("第二部分：分析报告")
    L.append(sub)
    L.append(f"有效样本：{an.get('respondents','（待企业补充）')}")
    L.append(f"NPS（净推荐值）：{nps_val}（推荐者 {prom_pct}% / 贬损者 {det_pct}%）")
    L.append("")
    L.append("维度得分：")
    for ds in an.get("dimension_scores", []) or []:
        L.append(f"  - {ds.get('name','')}：{ds.get('score','')} / {ds.get('outof','')}")
    L.append("")
    L.append(f"趋势：{an.get('trend','（待企业补充）')}")
    L.append("")
    L.append("关键发现：")
    kfs = an.get("key_findings", []) or ["（待企业补充）"]
    for k in kfs:
        L.append(f"  - {k}")
    L.append("")
    L.append("行动建议：")
    acts = an.get("actions", []) or ["（待企业补充）"]
    for a in acts:
        L.append(f"  - {a}")
    pend = sv.get("pending", [])
    if pend:
        L.append("")
        L.append("待企业补充项：")
        for x in pend:
            L.append(f"  - 〔待企业补充〕{x}")
    L.append("")
    L.append(f"本报告由客户质量满意度调查技能生成 · {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    return "\n".join(L)


SAMPLE_SURVEY = {
    "project": "2026上半年客户质量满意度调查（示意）",
    "owner": "客户质量部",
    "objectives": ["量化客户对质量的整体满意度", "定位改进优先级"],
    "survey": {
        "scale": "1-5",
        "dimensions": [
            {"name": "产品质量", "items": ["交付产品符合规格要求", "产品一致性与稳定性"]},
            {"name": "交付表现", "items": ["订单准时交付率", "紧急需求响应速度"]},
            {"name": "问题解决", "items": ["客诉处理时效", "8D闭环质量与证据"]},
            {"name": "技术支持", "items": ["技术响应专业度", "改进配合度"]},
            {"name": "沟通与关系", "items": ["信息透明度", "接口顺畅度"]}
        ],
        "nps_question": "您有多大可能向同行推荐我们？(0-10)",
        "ces_question": "您解决问题平均花费的精力？(1=极易, 7=极难)",
        "open_questions": ["在质量方面，您最希望我们改进什么？"]
    },
    "analysis": {
        "respondents": 120,
        "nps": {"promoters": 45, "passives": 50, "detractors": 25},
        "dimension_scores": [
            {"name": "产品质量", "score": 4.2, "outof": 5},
            {"name": "交付表现", "score": 3.8, "outof": 5},
            {"name": "问题解决", "score": 3.5, "outof": 5},
            {"name": "技术支持", "score": 4.0, "outof": 5},
            {"name": "沟通与关系", "score": 4.1, "outof": 5}
        ],
        "trend": "总体满意度较去年同期(3.9)微升至3.92；NPS由12升至17，但仍低于行业基准（待企业补充）。",
        "key_findings": [
            "问题解决维度得分最低(3.5)，客诉闭环时效是主要短板",
            "交付表现(3.8)受紧急订单影响波动",
            "NPS 17 仍偏低，贬损者占比20.8%需重点转化"
        ],
        "actions": [
            "建立客诉48小时响应SLA，推行QRQC快速响应",
            "对贬损者客户开展专项回访与根因整改",
            "交付维度引入紧急订单专项保障通道"
        ]
    },
    "pending": [
        "真实回收样本量与各维度题项均值（替换示意数据）",
        "行业/NPS 基准分（用于对标）",
        "分客户分层的交叉分析结果"
    ]
}


def main():
    ap = argparse.ArgumentParser(description="客户质量满意度调查生成与分析器（txt+md）")
    ap.add_argument("--input", help="结构化调查 JSON 路径（缺省使用内置小样本）")
    ap.add_argument("--out-dir", default=os.getcwd(), help="输出目录（默认当前工作目录）")
    ap.add_argument("--format", choices=["txt", "md", "all"], default="all", help="输出格式，默认 all（txt+md）")
    args = ap.parse_args()

    try:
        sv = load_survey(args.input) if args.input else SAMPLE_SURVEY
    except Exception as e:
        sys.stderr.write(f"读取输入失败：{e}\n")
        sys.exit(1)

    os.makedirs(args.out_dir, exist_ok=True)
    date_tag = datetime.now().strftime("%Y%m%d")
    base = f"客户满意度调查_{date_tag}"

    if args.format in ("md", "all"):
        md_path = os.path.join(args.out_dir, base + ".md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(build_md(sv))
        sys.stderr.write(f"MD 已生成：{md_path}\n")
    if args.format in ("txt", "all"):
        txt_path = os.path.join(args.out_dir, base + ".txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(build_txt(sv))
        sys.stderr.write(f"TXT 已生成：{txt_path}\n")


if __name__ == "__main__":
    main()
