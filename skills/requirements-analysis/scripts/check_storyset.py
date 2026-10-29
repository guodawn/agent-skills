#!/usr/bin/env python3
"""
check_storyset.py — 故事集结构与一致性校验

用法:
    python3 check_storyset.py 故事集.md
    python3 check_storyset.py 故事集.md --expect-cards 47 --expect-ac 542
    python3 check_storyset.py 故事集.md --prefix US --json

校验项:
    1. 卡片数量与编号唯一
    2. 同一编号族内序号连续（US-101..US-104 不断号）
    3. 每卡必备字段齐全
    4. 每卡 AC 编号从 1 连续
    5. Description 含 As a / so that
    6. Design 无 TBD 残留
    7. Conversation 至少一条"决定/未定/风险"
    8. 波次与规模分布
    9. 与 --expect-* 给定的基准值比对（用于批量改动后的回归）

退出码: 0 全部通过；1 有失败项；2 参数或读取错误
"""

import argparse
import json
import re
import sys
from collections import Counter, OrderedDict

REQUIRED_FIELDS = [
    ("Title", r"\*\*Title\*\*[：:]"),
    ("Description", r"\*\*Description\*\*[：:]"),
    ("Design", r"\*\*Design\*\*[：:]"),
    ("Conversation", r"\*\*Conversation\*\*"),
    ("Acceptance Criteria", r"\*\*Acceptance Criteria\*\*"),
    ("元信息", r"\*\*元信息\*\*[：:]"),
]

CARD_RE = re.compile(r"^##\s+(?P<id>(?P<prefix>[A-Za-z]+)-(?P<family>\d)(?P<seq>\d+))\b", re.M)
AC_ITEM_RE = re.compile(r"^(\d+)\.\s+\S", re.M)
TBD_RE = re.compile(r"\bTBD\b|待定\s*$|\[TODO", re.M)


def split_cards(text):
    """按卡片标题切块，返回 [(id, prefix, family, seq, body)]"""
    matches = list(CARD_RE.finditer(text))
    cards = []
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        cards.append(
            (
                m.group("id"),
                m.group("prefix"),
                m.group("family"),
                int(m.group("seq")),
                text[start:end],
            )
        )
    return cards


def check(path, prefix_filter=None, expect_cards=None, expect_ac=None):
    try:
        text = open(path, encoding="utf-8").read()
    except OSError as e:
        print(f"读取失败: {e}", file=sys.stderr)
        sys.exit(2)

    cards = split_cards(text)
    if prefix_filter:
        cards = [c for c in cards if c[1].upper() == prefix_filter.upper()]

    errors, warnings = [], []

    if not cards:
        errors.append("未找到任何卡片（标题需形如 `## US-101 标题`）")
        return summarize(path, cards, {}, {}, errors, warnings, expect_cards, expect_ac)

    # 1. 唯一性
    ids = [c[0] for c in cards]
    dup = [k for k, v in Counter(ids).items() if v > 1]
    if dup:
        errors.append(f"编号重复: {', '.join(sorted(dup))}")

    # 2. 族内序号连续
    families = OrderedDict()
    for cid, _p, fam, seq, _b in cards:
        families.setdefault(fam, []).append(seq)
    for fam, seqs in families.items():
        seqs_sorted = sorted(seqs)
        expect = list(range(1, len(seqs_sorted) + 1))
        if seqs_sorted != expect:
            missing = sorted(set(expect) - set(seqs_sorted))
            errors.append(f"编号族 *{fam} 断号，缺: {missing}")

    # 3-7. 逐卡
    ac_total = 0
    wave, size = Counter(), Counter()
    for cid, _p, _f, _s, body in cards:
        # 3. 字段
        for name, pat in REQUIRED_FIELDS:
            if not re.search(pat, body):
                errors.append(f"{cid} 缺字段 {name}")

        # 4. AC 编号连续
        ac_block = body.split("**元信息**")[0]
        nums = [int(n) for n in AC_ITEM_RE.findall(ac_block)]
        if nums:
            ac_total += len(nums)
            if nums != list(range(1, len(nums) + 1)):
                errors.append(f"{cid} AC 编号不连续: {nums}")
        else:
            errors.append(f"{cid} 无 AC")

        # 5. Description 形态
        desc = re.search(r"\*\*Description\*\*[：:](.*?)(?:\n\n|\*\*Design)", body, re.S)
        if desc:
            d = desc.group(1)
            if "As a" not in d and "作为" not in d:
                warnings.append(f"{cid} Description 未用 As a / 作为 句式")
            if "so that" not in d and "以便" not in d:
                warnings.append(f"{cid} Description 缺 so that / 以便")
        else:
            errors.append(f"{cid} Description 为空")

        # 6. Design 残留 TBD
        dm = re.search(r"\*\*Design\*\*[：:](.+)", body)
        if dm and TBD_RE.search(dm.group(1)):
            errors.append(f"{cid} Design 仍为 TBD")

        # 7. Conversation 有实质内容
        cm = re.search(r"\*\*Conversation\*\*(.*?)\*\*Acceptance Criteria\*\*", body, re.S)
        if cm:
            c = cm.group(1)
            if not re.search(r"决定|未定|风险|Decision|Open|Risk", c):
                warnings.append(f"{cid} Conversation 无「决定/未定/风险」条目")

        # 8. 分布
        mm = re.search(r"\*\*元信息\*\*[：:](.+)", body)
        if mm:
            meta = mm.group(1)
            w = re.search(r"波次\s*(\d)", meta)
            s = re.search(r"规模\s*\*{0,2}\s*([SML])", meta)
            if w:
                wave[w.group(1)] += 1
            else:
                warnings.append(f"{cid} 元信息缺「波次」")
            if s:
                size[s.group(1)] += 1
            else:
                warnings.append(f"{cid} 元信息缺「规模」")

    return summarize(
        path, cards, wave, size, errors, warnings, expect_cards, expect_ac, ac_total
    )


def summarize(
    path,
    cards,
    wave,
    size,
    errors,
    warnings,
    expect_cards,
    expect_ac,
    ac_total=0,
):
    lines = []
    ok = True
    lines.append(f"文件: {path}")
    lines.append(f"卡片: {len(cards)} ｜ AC: {ac_total} ｜ 平均 {ac_total / max(len(cards), 1):.1f} 条/卡")

    if wave:
        lines.append(
            "波次: " + " / ".join(f"{k}:{v}" for k, v in sorted(wave.items()))
        )
    if size:
        lines.append(
            "规模: " + " / ".join(f"{k}:{v}" for k, v in sorted(size.items()))
        )
        if size.get("L"):
            lines.append(f"提示: {size['L']} 张 L 卡，进迭代前需再拆")

    if expect_cards is not None:
        if len(cards) != expect_cards:
            errors.append(f"卡片数 {len(cards)} ≠ 基准 {expect_cards}")
    if expect_ac is not None:
        if ac_total != expect_ac:
            errors.append(f"AC 数 {ac_total} ≠ 基准 {expect_ac}")

    lines.append("")
    if errors:
        ok = False
        lines.append(f"✗ 失败 {len(errors)} 项")
        for e in errors:
            lines.append(f"  - {e}")
    else:
        lines.append("✓ 结构校验全部通过")

    if warnings:
        lines.append(f"⚠ 提示 {len(warnings)} 项")
        for w in warnings[:40]:
            lines.append(f"  - {w}")
        if len(warnings) > 40:
            lines.append(f"  … 其余 {len(warnings) - 40} 项省略")

    print("\n".join(lines))
    return ok


def main():
    ap = argparse.ArgumentParser(description="故事集结构与一致性校验")
    ap.add_argument("path")
    ap.add_argument("--prefix", help="只校验某个编号前缀，如 US")
    ap.add_argument("--expect-cards", type=int, help="期望卡片数（回归基准）")
    ap.add_argument("--expect-ac", type=int, help="期望 AC 总数（回归基准）")
    ap.add_argument("--json", action="store_true", help="以 JSON 输出")
    args = ap.parse_args()

    if args.json:
        import io
        from contextlib import redirect_stdout

        buf = io.StringIO()
        with redirect_stdout(buf):
            ok = check(
                args.path, args.prefix, args.expect_cards, args.expect_ac
            )
        print(json.dumps({"ok": ok, "report": buf.getvalue()}, ensure_ascii=False, indent=2))
    else:
        ok = check(args.path, args.prefix, args.expect_cards, args.expect_ac)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
