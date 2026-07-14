#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
客户质量满意度调查生成与分析器
读入结构化调查 JSON，生成 Markdown + 网页版 HTML（主色 #C8102E）。
同时产出"问卷卷首 + 量化分析报告"双版文档。

用法：
  python build_report.py --input survey.json --md-out 客户满意度调查.md --html-out 客户满意度调查.html
  python build_report.py                                 # 内置小样本，直接产出示意双版

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
import sys
import html
from datetime import datetime

PRIMARY = "#C8102E"


def esc(s):
    return html.escape(str(s), quote=True)


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


CSS = f"""
:root{{--primary:{PRIMARY};--bg:#fafafa;--card:#ffffff;--ink:#1f2937;--muted:#6b7280;}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,"Segoe UI",Roboto,"PingFang SC","Microsoft YaHei",sans-serif;
  background:var(--bg);color:var(--ink);line-height:1.75;padding:32px}}
.wrap{{max-width:1000px;margin:0 auto}}
header{{text-align:center;padding:26px 0 16px;border-bottom:3px solid var(--primary);margin-bottom:26px}}
header h1{{font-size:27px}}
header .meta{{color:var(--muted);font-size:14px;margin-top:10px}}
.sec{{background:var(--card);border-radius:14px;padding:22px 26px;box-shadow:0 4px 16px rgba(0,0,0,.05);margin-bottom:20px}}
.sec h2{{font-size:20px;margin-bottom:12px;border-left:5px solid var(--primary);padding-left:12px}}
.sec h3{{font-size:16px;margin:12px 0 6px;color:var(--primary)}}
.sec p,.sec li{{font-size:15px;margin:4px 0}}
.nps{{display:flex;gap:16px;margin:12px 0}}
.nps .box{{flex:1;text-align:center;border-radius:12px;padding:14px;background:#f1f5f9}}
.nps .big{{font-size:30px;font-weight:800;color:var(--primary)}}
table{{width:100%;border-collapse:collapse;margin-top:10px;font-size:14px}}
th,td{{border:1px solid #e5e7eb;padding:9px 12px;text-align:left}}
th{{background:var(--primary);color:#fff}}
.pend{{background:#fff7f8;border:1px dashed var(--primary);border-radius:12px;padding:16px 22px}}
.pend h2{{color:var(--primary);border:none;padding:0;margin-bottom:8px}}
footer{{text-align:center;color:var(--muted);font-size:12px;margin-top:18px}}
"""


def build_html(sv):
    an = sv.get("analysis", {})
    nps = an.get("nps", {})
    nps_val, prom_pct, det_pct = compute_nps(nps)
    dims_html = ""
    for dim in (sv.get("survey", {}).get("dimensions", []) or []):
        items = "\n".join(f"<li>{esc(it)} 〔{esc(sv.get('survey',{}).get('scale','1-5'))}分制〕</li>" for it in (dim.get("items", []) or []))
        dims_html += f"<p><b>{esc(dim.get('name',''))}</b></p><ul>{items}</ul>"
    opens = "\n".join(f"<li>{esc(oq)}</li>" for oq in (sv.get("survey", {}).get("open_questions", []) or []))
    score_rows = "\n".join(
        f"<tr><td>{esc(ds.get('name',''))}</td><td>{esc(ds.get('score',''))}</td><td>{esc(ds.get('outof',''))}</td></tr>"
        for ds in (an.get("dimension_scores", []) or [])
    )
    findings = "\n".join(f"<li>{esc(k)}</li>" for k in (an.get("key_findings", []) or ["（待企业补充）"]))
    actions = "\n".join(f"<li>{esc(a)}</li>" for a in (an.get("actions", []) or ["（待企业补充）"]))
    pend = sv.get("pending", [])
    pend_html = ""
    if pend:
        items = "\n".join(f"<li>〔待企业补充〕{esc(x)}</li>" for x in pend)
        pend_html = f"<div class='pend'><h2>待企业补充项</h2><ul>{items}</ul></div>"
    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(sv.get('project','客户质量满意度调查'))}</title>
<style>{CSS}</style></head>
<body><div class="wrap">
<header>
  <h1>{esc(sv.get('project','客户质量满意度调查'))}</h1>
  <div class="meta">责任部门：{esc(sv.get('owner',''))} ｜ 生成：{datetime.now().strftime('%Y-%m-%d')}</div>
</header>
<section class="sec"><h2>第一部分：调查问卷</h2>
<h3>一、满意度维度题（CSAT）</h3>{dims_html}
<h3>二、NPS 推荐意愿题</h3><p>{esc(sv.get('survey',{}).get('nps_question','推荐意愿(0-10)'))}</p>
<h3>三、CES 费力度题</h3><p>{esc(sv.get('survey',{}).get('ces_question','费力度'))}</p>
<h3>四、开放题</h3><ul>{opens}</ul>
</section>
<section class="sec"><h2>第二部分：分析报告</h2>
<p>有效样本：{esc(an.get('respondents','（待企业补充）'))}</p>
<div class="nps">
  <div class="box"><div class="big">{nps_val}</div><div>NPS 净推荐值</div></div>
  <div class="box"><div class="big">{prom_pct}%</div><div>推荐者</div></div>
  <div class="box"><div class="big">{det_pct}%</div><div>贬损者</div></div>
</div>
<h3>维度得分</h3>
<table><thead><tr><th>维度</th><th>得分</th><th>量表上限</th></tr></thead><tbody>{score_rows}</tbody></table>
<h3>趋势</h3><p>{esc(an.get('trend','（待企业补充）'))}</p>
<h3>关键发现</h3><ul>{findings}</ul>
<h3>行动建议</h3><ul>{actions}</ul>
</section>
{pend_html}
<footer>本报告由客户质量满意度调查技能生成 · {datetime.now().strftime('%Y-%m-%d %H:%M')}</footer>
</div></body></html>"""


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
    ap = argparse.ArgumentParser(description="客户质量满意度调查生成与分析器")
    ap.add_argument("--input", help="结构化调查 JSON 路径（缺省使用内置小样本）")
    ap.add_argument("--md-out", default="客户满意度调查.md", help="输出 MD 路径")
    ap.add_argument("--html-out", default="客户满意度调查.html", help="输出 HTML 路径")
    args = ap.parse_args()

    try:
        sv = load_survey(args.input) if args.input else SAMPLE_SURVEY
    except Exception as e:
        sys.stderr.write(f"读取输入失败：{e}\n")
        sys.exit(1)

    with open(args.md_out, "w", encoding="utf-8") as f:
        f.write(build_md(sv))
    sys.stderr.write(f"MD 已生成：{args.md_out}\n")

    with open(args.html_out, "w", encoding="utf-8") as f:
        f.write(build_html(sv))
    sys.stderr.write(f"HTML 已生成：{args.html_out}\n")


if __name__ == "__main__":
    main()
