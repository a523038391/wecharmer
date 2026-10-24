#!/usr/bin/env python3
"""testcase_to_xlsx.py — 结构化测试用例 JSON 转 xlsx/csv。

用法:
    python testcase_to_xlsx.py cases.json
    python testcase_to_xlsx.py cases.json -o 测试用例.xlsx
    python testcase_to_xlsx.py cases.json --format csv -o cases.csv

输入 JSON 结构见 skill 的 references/output-templates.md 第 5 节。
用例的 dimension 字段（12 覆盖维度）写入「覆盖维度」列，概要 sheet 含维度覆盖统计；
dimension 缺省时按 scene（正常/边界/异常场景）自动映射为对应维度。
xlsx 输出依赖 openpyxl；缺失时按报错提示安装，或改用 --format csv（纯标准库）。

退出码: 0 成功 / 1 输入或参数错误 / 2 依赖缺失
"""

import argparse
import csv
import json
import re
import sys
from pathlib import Path

COLUMNS = [
    ("用例编号", 14),
    ("所属模块", 12),
    ("用例标题", 32),
    ("优先级", 8),
    ("覆盖维度", 12),
    ("测试类型", 10),
    ("前置条件", 24),
    ("操作步骤", 40),
    ("预期结果", 32),
    ("关联测试点", 14),
    ("关联需求", 12),
    ("备注", 16),
]

# 接口用例列：用例含 method/path/expected_code 任一字段时追加到「测试用例」sheet
API_COLUMNS = [
    ("请求方式", 8),
    ("请求路径", 28),
    ("请求头", 24),
    ("请求参数", 32),
    ("预期状态码", 10),
    ("响应校验", 28),
]

PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}

DIMENSIONS = [
    "正常功能流程",
    "异常流程",
    "边界值场景",
    "权限控制",
    "数据校验",
    "状态流转",
    "前后端交互",
    "数据库一致性",
    "兼容性",
    "性能风险",
    "安全风险",
    "历史缺陷可能复发点",
]

SCENE_TO_DIMENSION = {
    "正常场景": "正常功能流程",
    "边界场景": "边界值场景",
    "异常场景": "异常流程",
}


def case_dimensions(case):
    """返回用例的覆盖维度列表；dimension 优先，scene 自动映射，均无则空列表。"""
    value = case.get("dimension")
    if value:
        parts = [p.strip() for p in re.split(r"[、,，/;；]", str(value)) if p.strip()]
        if parts:
            return parts
    scene = str(case.get("scene") or "").strip()
    if scene in SCENE_TO_DIMENSION:
        return [SCENE_TO_DIMENSION[scene]]
    return [scene] if scene else []


def to_text(value):
    """对象/字符串统一转为单行文本（对象 JSON 序列化，中文不转义）。"""
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def has_api_cases(cases):
    """用例集中是否存在接口用例（含 method/path/expected_code 任一字段）。"""
    return any(
        c.get("method") or c.get("path") or c.get("expected_code") is not None
        for c in cases
    )


def load_cases(path: Path):
    """读取并校验 JSON，返回 (meta, cases)。校验失败时打印错误并退出。"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        fail(f"输入文件不存在: {path}")
    except json.JSONDecodeError as e:
        fail(f"JSON 解析失败: {e}")

    if isinstance(data, list):
        meta, cases = {}, data
    elif isinstance(data, dict):
        meta = data.get("meta") or {}
        cases = data.get("cases")
        if not isinstance(cases, list):
            fail("JSON 根对象缺少 'cases' 数组")
    else:
        fail("JSON 根节点必须是对象或数组")

    errors = []
    seen_ids = set()
    for i, c in enumerate(cases, 1):
        if not isinstance(c, dict):
            errors.append(f"第 {i} 条用例不是对象")
            continue
        for field in ("id", "module", "title", "priority"):
            if not str(c.get(field, "")).strip():
                errors.append(f"第 {i} 条用例缺少必填字段 '{field}'")
        if c.get("id") in seen_ids:
            errors.append(f"用例编号重复: {c.get('id')}")
        seen_ids.add(c.get("id"))
        steps = c.get("steps")
        if not isinstance(steps, list) or not steps:
            errors.append(f"用例 {c.get('id', '?')} 的 'steps' 必须是非空数组")
        if not str(c.get("expected", "")).strip():
            errors.append(f"用例 {c.get('id', '?')} 缺少 'expected' 预期结果")

    if errors:
        print("用例数据校验失败:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)

    cases.sort(key=lambda c: (PRIORITY_ORDER.get(str(c.get("priority")), 9),))
    return meta, cases


def row_of(case, with_api=False):
    steps = case.get("steps") or []
    numbered = "\n".join(f"{i}. {s}" for i, s in enumerate(steps, 1))
    join = lambda v: "、".join(v) if isinstance(v, list) else (v or "")
    row = [
        str(case.get("id", "")),
        str(case.get("module", "")),
        str(case.get("title", "")),
        str(case.get("priority", "")),
        "、".join(case_dimensions(case)),
        str(case.get("type") or "功能测试"),
        str(case.get("precondition", "")),
        numbered,
        str(case.get("expected", "")),
        join(case.get("test_points")),
        join(case.get("requirements")),
        str(case.get("remark", "")),
    ]
    if with_api:
        row += [
            str(case.get("method") or ""),
            str(case.get("path") or ""),
            to_text(case.get("headers")),
            to_text(case.get("body")),
            str(case.get("expected_code", "") if case.get("expected_code") is not None else ""),
            str(case.get("response_checks") or ""),
        ]
    return row


def fail(msg):
    print(f"错误: {msg}", file=sys.stderr)
    sys.exit(1)


def write_csv(cases, out_path: Path, with_api=False):
    columns = COLUMNS + API_COLUMNS if with_api else COLUMNS
    with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow([c[0] for c in columns])
        for case in cases:
            w.writerow(row_of(case, with_api))
    print(f"已生成 CSV: {out_path}（共 {len(cases)} 条用例）")


def write_xlsx(meta, cases, out_path: Path, with_api=False):
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Alignment, Font, PatternFill
        from openpyxl.utils import get_column_letter
    except ImportError:
        print(
            "缺少依赖 openpyxl。两种解决方式：\n"
            "  1) 安装: pip install openpyxl（或在 WorkBuddy 管理的 venv 中安装）\n"
            "  2) 改用 CSV: 追加参数 --format csv",
            file=sys.stderr,
        )
        sys.exit(2)

    wb = Workbook()
    columns = COLUMNS + API_COLUMNS if with_api else COLUMNS

    # ---- Sheet 1: 测试用例 ----
    ws = wb.active
    ws.title = "测试用例"
    header_font = Font(bold=True, color="FFFFFF", name="微软雅黑", size=10)
    header_fill = PatternFill("solid", fgColor="4472C4")
    body_font = Font(name="微软雅黑", size=10)
    top_wrap = Alignment(vertical="top", wrap_text=True)

    for col, (name, width) in enumerate(columns, 1):
        cell = ws.cell(row=1, column=col, value=name)
        cell.font = header_font
        cell.fill = header_fill
        ws.column_dimensions[get_column_letter(col)].width = width

    priority_font = {
        "P0": Font(name="微软雅黑", size=10, bold=True, color="C00000"),
        "P1": Font(name="微软雅黑", size=10, bold=True, color="BF6000"),
    }

    for r, case in enumerate(cases, 2):
        values = row_of(case, with_api)
        for c, value in enumerate(values, 1):
            cell = ws.cell(row=r, column=c, value=value)
            cell.alignment = top_wrap
            if c == 4 and values[3] in priority_font:
                cell.font = priority_font[values[3]]
            else:
                cell.font = body_font

    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:{get_column_letter(len(columns))}{len(cases) + 1}"

    # ---- Sheet 2: 概要 ----
    if meta or cases:
        ws2 = wb.create_sheet("概要")
        label_font = Font(bold=True, name="微软雅黑", size=10)
        meta_map = [
            ("项目", meta.get("project", "")),
            ("需求", meta.get("requirement", "")),
            ("版本", meta.get("version", "")),
            ("编写人", meta.get("author", "")),
            ("日期", meta.get("date", "")),
        ]
        row = 1
        for k, v in meta_map:
            ws2.cell(row=row, column=1, value=k).font = label_font
            ws2.cell(row=row, column=2, value=v).font = body_font
            row += 1
        row += 1
        ws2.cell(row=row, column=1, value="统计").font = Font(
            bold=True, size=11, name="微软雅黑"
        )
        row += 1
        stats = [
            ("用例总数", len(cases)),
            *[
                (f"{p} 用例数", sum(1 for c in cases if c.get("priority") == p))
                for p in ("P0", "P1", "P2", "P3")
            ],
        ]
        modules = {}
        for c in cases:
            modules[c.get("module", "")] = modules.get(c.get("module", ""), 0) + 1
        stats += [(f"模块: {m}", n) for m, n in sorted(modules.items())]
        for k, v in stats:
            ws2.cell(row=row, column=1, value=k).font = body_font
            ws2.cell(row=row, column=2, value=v).font = body_font
            row += 1

        # ---- 维度覆盖统计（12 维度，0 显示为红色「未覆盖」）----
        row += 1
        ws2.cell(row=row, column=1, value="维度覆盖").font = Font(
            bold=True, size=11, name="微软雅黑"
        )
        row += 1
        dim_counts = {}
        for c in cases:
            dims = case_dimensions(c)
            for d in dims or ["(未标注)"]:
                dim_counts[d] = dim_counts.get(d, 0) + 1
        warn_font = Font(name="微软雅黑", size=10, bold=True, color="C00000")
        ordered = DIMENSIONS + [k for k in dim_counts if k not in DIMENSIONS]
        for d in ordered:
            n = dim_counts.get(d, 0)
            ws2.cell(row=row, column=1, value=d).font = body_font
            cell = ws2.cell(row=row, column=2, value=n if n else "未覆盖")
            cell.font = body_font if n else warn_font
            row += 1
        ws2.column_dimensions["A"].width = 20
        ws2.column_dimensions["B"].width = 30

    wb.save(out_path)
    print(f"已生成 XLSX: {out_path}（共 {len(cases)} 条用例）")


def main():
    parser = argparse.ArgumentParser(description="结构化测试用例 JSON 转 xlsx/csv")
    parser.add_argument("input", help="输入 JSON 文件路径")
    parser.add_argument("-o", "--output", help="输出文件路径（默认与输入同名，扩展名随格式）")
    parser.add_argument(
        "--format", choices=["xlsx", "csv"], default="xlsx", help="输出格式，默认 xlsx"
    )
    args = parser.parse_args()

    in_path = Path(args.input)
    meta, cases = load_cases(in_path)
    with_api = has_api_cases(cases)

    if args.output:
        out_path = Path(args.output)
    else:
        out_path = in_path.with_suffix("." + args.format)

    if args.format == "csv":
        write_csv(cases, out_path, with_api)
    else:
        write_xlsx(meta, cases, out_path, with_api)


if __name__ == "__main__":
    main()
