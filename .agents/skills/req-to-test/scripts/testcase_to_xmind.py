#!/usr/bin/env python3
"""testcase_to_xmind.py — 测试用例 JSON → .xmind 脑图（或 Markdown 大纲）。

支持两种输入：
  1. 树形 JSON（推荐，完整控制脑图结构）: {"root": {"title": ..., "children": [...]}}
     节点字段: title(必填) / priority(P0-P3) / labels([]) / note / children([])
     详见 skill 的 references/output-templates.md 第 7 节；生成单 sheet
  2. 用例集 JSON（与 testcase_to_xlsx.py 同构）: {"meta": {...}, "cases": [...]}
     自动生成双 sheet：
       - 「按模块」视图：需求 → 模块 → 用例
       - 「维度覆盖」视图：12 个维度分支 + 每维度用例数，空维度挂「⚠ 未覆盖」警示，
         供第 5 步人工审核检查维度缺口
     用例维度取 dimension 字段（多维度用顿号/逗号分隔）；
     缺省时按 scene 自动映射：正常场景→正常功能流程、边界场景→边界值场景、异常场景→异常流程

用法:
    python testcase_to_xmind.py tree.json                      # 输出同名 .xmind
    python testcase_to_xmind.py tree.json -o 测试用例.xmind
    python testcase_to_xmind.py cases.json --format md -o 大纲.md

P0-P3 自动映射为 XMind 优先级图标（priority-1..4）并附加优先级标签。

用例详情展示方式（--detail-style）：
  - topics（默认）: 前置条件 / 操作步骤 / 预期结果（及接口请求信息）展开为子主题，
    脑图中直接可见，逐层展开即可审阅；多行文本自动拆成子节点。
  - note: 折叠进节点便签，脑图紧凑，点开便签查看。

退出码: 0 成功 / 1 输入错误
"""

import argparse
import itertools
import json
import re
import sys
import zipfile
from pathlib import Path

PRIORITY_MARKER = {
    "P0": "priority-1",
    "P1": "priority-2",
    "P2": "priority-3",
    "P3": "priority-4",
}

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


def fail(msg):
    print(f"错误: {msg}", file=sys.stderr)
    sys.exit(1)


def load_json(path: Path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        fail(f"输入文件不存在: {path}")
    except json.JSONDecodeError as e:
        fail(f"JSON 解析失败: {e}")


def split_dimensions(value):
    if not value:
        return []
    parts = re.split(r"[、,，/;；]", str(value))
    return [p.strip() for p in parts if p.strip()]


def case_dimensions(case):
    """返回用例的覆盖维度列表；dimension 优先，scene 自动映射，均无则空列表。"""
    parts = split_dimensions(case.get("dimension"))
    if parts:
        return parts
    scene = str(case.get("scene") or "").strip()
    if scene in SCENE_TO_DIMENSION:
        return [SCENE_TO_DIMENSION[scene]]
    return [scene] if scene else []


def validate_tree(node, path="root"):
    if not isinstance(node, dict) or not str(node.get("title", "")).strip():
        fail(f"树形 JSON 校验失败: {path} 节点缺少非空 'title'")
    children = node.get("children", [])
    if not isinstance(children, list):
        fail(f"树形 JSON 校验失败: {path} 的 'children' 必须是数组")
    for i, child in enumerate(children):
        validate_tree(child, f"{path}.children[{i}]")


def to_text(value):
    """对象/字符串统一转为文本（对象 JSON 序列化，中文不转义）。"""
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def _field_topic(name, text):
    """单字段 → 子主题节点；单行直接「字段名: 内容」，多行拆为父节点+子节点。"""
    lines = [ln.strip() for ln in str(text).splitlines() if ln.strip()]
    if not lines:
        return None
    if len(lines) == 1:
        return {"title": f"{name}: {lines[0]}"}
    return {"title": name, "children": [{"title": ln} for ln in lines]}


def detail_topics(c):
    """用例详情 → 子主题节点列表（接口信息 / 前置条件 / 操作步骤 / 预期结果）。"""
    topics = []
    # 接口用例：请求方式+路径、请求头、请求参数、预期状态码、响应校验
    method = str(c.get("method") or "")
    path = str(c.get("path") or "")
    if method or path:
        topics.append({"title": f"请求: {method} {path}".strip()})
    if c.get("headers"):
        topics.append({"title": f"请求头: {to_text(c['headers'])}"})
    if c.get("body"):
        topics.append({"title": f"请求参数: {to_text(c['body'])}"})
    if c.get("expected_code") is not None:
        topics.append({"title": f"预期状态码: {c['expected_code']}"})
    if c.get("response_checks"):
        topics.append(_field_topic("响应校验", c["response_checks"]))
    if c.get("precondition"):
        topics.append(_field_topic("前置条件", c["precondition"]))
    steps = [str(s).strip() for s in (c.get("steps") or []) if str(s).strip()]
    if steps:
        if len(steps) == 1:
            topics.append({"title": f"操作步骤: {steps[0]}"})
        else:
            topics.append(
                {
                    "title": "操作步骤",
                    "children": [
                        {"title": f"{i}. {s}"} for i, s in enumerate(steps, 1)
                    ],
                }
            )
    if c.get("expected"):
        topics.append(_field_topic("预期结果", c["expected"]))
    return [t for t in topics if t]


def build_note_parts(c):
    """用例详情 → 便签段落列表（note 模式使用）。"""
    note_parts = []
    method = str(c.get("method") or "")
    path = str(c.get("path") or "")
    if method or path:
        note_parts.append(f"请求: {method} {path}".strip())
    if c.get("headers"):
        note_parts.append(f"请求头: {to_text(c['headers'])}")
    if c.get("body"):
        note_parts.append(f"请求参数: {to_text(c['body'])}")
    if c.get("expected_code") is not None:
        note_parts.append(f"预期状态码: {c['expected_code']}")
    if c.get("response_checks"):
        note_parts.append(f"响应校验: {c['response_checks']}")
    if c.get("precondition"):
        note_parts.append(f"前置条件: {c['precondition']}")
    steps = c.get("steps") or []
    if steps:
        numbered = "\n".join(f"{i}. {s}" for i, s in enumerate(steps, 1))
        note_parts.append(f"操作步骤:\n{numbered}")
    if c.get("expected"):
        note_parts.append(f"预期结果: {c['expected']}")
    return note_parts


def build_case_node(c, detail_style="topics"):
    """单条用例 → 脑图节点（labels 为覆盖维度）。
    detail_style="topics"：前置条件/步骤/预期结果等展开为子主题（默认）；
    detail_style="note"：  折叠进节点便签（紧凑模式）。
    """
    labels = case_dimensions(c)
    node = {
        "title": f"{c.get('id', '')} {c.get('title', '')}".strip(),
        "priority": c.get("priority"),
    }
    if labels:
        node["labels"] = labels
    if detail_style == "topics":
        children = detail_topics(c)
        if children:
            node["children"] = children
    else:
        note_parts = build_note_parts(c)
        if note_parts:
            node["note"] = "\n\n".join(note_parts)
    return node


def build_module_tree(meta, cases, detail_style="topics"):
    """用例集 → 需求 → 模块 → 用例 树。"""
    modules = {}
    order = []
    for c in cases:
        if not str(c.get("id", "")).strip():
            fail("用例缺少 'id' 字段")
        m = str(c.get("module", "未分组")) or "未分组"
        if m not in modules:
            modules[m] = []
            order.append(m)
        modules[m].append(build_case_node(c, detail_style))
    root_title = (
        str(meta.get("requirement") or meta.get("project") or "测试用例")
    )
    return {
        "title": root_title,
        "children": [
            {"title": m, "children": modules[m]} for m in order
        ],
    }


def build_dimension_tree(cases, detail_style="topics"):
    """用例集 → 12 维度覆盖检查树（空维度挂未覆盖警示）。"""
    buckets = {}
    extra_map = {}
    unassigned = []
    for c in cases:
        node = build_case_node(c, detail_style)
        dims = case_dimensions(c)
        if not dims:
            unassigned.append(node)
            continue
        for d in dims:
            if d in DIMENSIONS:
                buckets.setdefault(d, []).append(node)
            else:
                extra_map.setdefault(d, []).append(node)
    covered = sum(len(v) for v in buckets.values())
    root_title = f"维度覆盖检查（{covered} 条用例 / 12 维度）"
    children = []
    for i, d in enumerate(DIMENSIONS, 1):
        items = buckets.get(d, [])
        if items:
            dim_node = {"title": f"{i}. {d}（{len(items)} 条）", "children": items}
        else:
            dim_node = {
                "title": f"{i}. {d}（0 条）",
                "children": [{"title": "⚠ 未覆盖——审核时确认是否需要补充"}],
            }
        children.append(dim_node)
    for d, nodes in extra_map.items():
        children.append({"title": f"{d}（{len(nodes)} 条）", "children": nodes})
    if unassigned:
        children.append(
            {"title": f"未标注维度（{len(unassigned)} 条）", "children": unassigned}
        )
    return {
        "title": root_title,
        "note": "12 维度覆盖矩阵：空维度即覆盖缺口，审核时逐个确认「补充测试点」或「不适用（写明理由）」",
        "children": children,
    }


def normalize_sheets(data, detail_style="topics"):
    """两种输入统一为 sheet 列表 [(sheet_title, root_node), ...]。"""
    if isinstance(data, dict) and isinstance(data.get("root"), dict):
        validate_tree(data["root"])
        root = data["root"]
        return [(str(root.get("title") or "测试用例"), root)]
    if isinstance(data, dict) and isinstance(data.get("cases"), list):
        meta = data.get("meta") or {}
        module_root = build_module_tree(meta, data["cases"], detail_style)
        dim_root = build_dimension_tree(data["cases"], detail_style)
        return [
            (str(module_root.get("title") or "测试用例"), module_root),
            ("维度覆盖检查", dim_root),
        ]
    if isinstance(data, list):
        module_root = build_module_tree({}, data, detail_style)
        dim_root = build_dimension_tree(data, detail_style)
        return [
            (str(module_root.get("title") or "测试用例"), module_root),
            ("维度覆盖检查", dim_root),
        ]
    fail('无法识别输入结构：需要 {"root": ...} 树形 JSON 或 {"cases": [...]} 用例集 JSON')


def build_topic(node, counter):
    topic = {
        "id": f"t{next(counter)}",
        "class": "topic",
        "title": str(node["title"]),
    }
    priority = str(node.get("priority") or "")
    labels = [str(x) for x in (node.get("labels") or [])]
    if priority in PRIORITY_MARKER:
        topic["markers"] = [{"markerId": PRIORITY_MARKER[priority]}]
        if priority not in labels:
            labels = [priority] + labels
    if labels:
        topic["labels"] = labels
    if node.get("note"):
        topic["notes"] = {"plain": {"content": str(node["note"])}}
    children = node.get("children") or []
    if children:
        topic["children"] = {
            "attached": [build_topic(c, counter) for c in children]
        }
    return topic


def write_xmind(sheets, out_path: Path):
    counter = itertools.count(1)
    content = []
    for i, (sheet_title, root) in enumerate(sheets, 1):
        root_topic = build_topic(root, counter)
        root_topic["structureClass"] = "org.xmind.ui.logic.right"
        content.append(
            {
                "id": f"sheet-{i}",
                "class": "sheet",
                "title": str(sheet_title)[:60] or f"Sheet {i}",
                "rootTopic": root_topic,
            }
        )
    metadata = {"creator": {"name": "req-to-test skill", "version": "1.1"}}
    manifest = {"file-entries": {"content.json": {}, "metadata.json": {}}}
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("content.json", json.dumps(content, ensure_ascii=False))
        zf.writestr("metadata.json", json.dumps(metadata, ensure_ascii=False))
        zf.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False))
    n_nodes = next(counter) - 1
    print(
        f"已生成 XMind 脑图: {out_path}"
        f"（{len(sheets)} 个 sheet，共 {n_nodes} 个节点，可用 XMind 打开编辑）"
    )


def write_md(sheets, out_path: Path):
    lines = []

    def walk(node, depth):
        title = str(node["title"])
        if depth <= 6:
            lines.append("#" * depth + " " + title)
        else:
            lines.append("  " * (depth - 7) + "- " + title)
        note = node.get("note")
        if note:
            for ln in str(note).splitlines():
                lines.append("> " + ln if ln.strip() else ">")
            lines.append("")
        for child in node.get("children") or []:
            walk(child, depth + 1)

    for i, (sheet_title, root) in enumerate(sheets):
        if i > 0:
            lines.append("")
            lines.append("---")
            lines.append("")
        walk(root, 1)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"已生成 Markdown 大纲: {out_path}（含 {len(sheets)} 个视图）")


def main():
    parser = argparse.ArgumentParser(description="测试用例 JSON 转 xmind 脑图 / Markdown 大纲")
    parser.add_argument("input", help="输入 JSON 文件路径")
    parser.add_argument("-o", "--output", help="输出文件路径（默认与输入同名，扩展名随格式）")
    parser.add_argument("--format", choices=["xmind", "md"], default="xmind", help="输出格式，默认 xmind")
    parser.add_argument(
        "--detail-style", choices=["topics", "note"], default="topics",
        help="用例详情展示方式: topics=前置条件/步骤/预期结果作为子主题（默认，展开即见）; "
             "note=折叠进节点便签（紧凑）",
    )
    args = parser.parse_args()

    in_path = Path(args.input)
    sheets = normalize_sheets(load_json(in_path), args.detail_style)

    ext = ".xmind" if args.format == "xmind" else ".md"
    out_path = Path(args.output) if args.output else in_path.with_suffix(ext)

    if args.format == "md":
        write_md(sheets, out_path)
    else:
        write_xmind(sheets, out_path)


if __name__ == "__main__":
    main()
