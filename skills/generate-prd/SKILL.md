---
name: generate-prd
description: Generate complete Chinese PRD documents from rough product requests. Use when the user asks to create, refine, or standardize a PRD, turn ambiguous requirements into an Agile-friendly product requirements document, or fill a PRD template by first asking focused clarification questions and then saving the final markdown file.
---

# Generate PRD

## Overview

Turn incomplete product ideas into a complete Chinese PRD that a delivery team can discuss and implement.
Use the bundled template at `./assets/prd-template.md` as the required output structure and do not change its section order unless the user explicitly asks for a different format.

## Workflow

Follow these phases in order.
Do not skip a phase unless the user explicitly asks for a partial result.

### Phase 1: Clarify Missing Information

1. Read the user's request and propose a concise requirement name.
2. Read `./assets/prd-template.md` before asking questions.
3. Compare the request against every template section and identify missing or weak information.
4. Ask focused clarification questions one by one or in very small batches.
5. Prioritize gaps that block later sections:
   - business background and problem evidence
   - target users and scenarios
   - scope boundaries
   - functional details and business rules
   - success metrics, release constraints, and dependencies
6. Stop asking questions when the remaining unknowns can be filled with reasonable, explicit assumptions.
7. If assumptions are necessary, label them clearly in the final PRD as `待确认` rather than pretending they were provided.

### Phase 2: Generate The PRD

1. Use the exact structure from `./assets/prd-template.md`.
2. Replace every placeholder with real content derived from the user's request, follow-up answers, or explicit assumptions.
3. Write the entire document in Chinese.
4. Use professional product language and active voice.
5. **路径约束**：文档输出目录必须固定为 `<当前项目根目录>/docs/requirements/`。
   - "当前项目根目录"指调用本 skill 时所在的工程根目录（即用户当前操作的代码仓库根），不是 skill 自身所在的位置。
   - 默认情况下不接受其他保存位置；仅当用户在本次调用中明确指定了其他目录时，才覆盖此约束，并在文档说明中注明实际使用的路径。
6. **自动建目录**：若 `<当前项目根目录>/docs/requirements/` 不存在，则必须按需递归创建（包括 `docs/` 等所有缺失的父级目录），确认创建成功后再写入文档。
7. 将文档统一保存为 `<当前项目根目录>/docs/requirements/<需求名称>-prd.md`。
8. Keep the requirement name short, specific, and file-system safe. Replace illegal path characters with `-` when needed.

### Phase 3: Validate And Improve

1. Review the PRD section by section.
2. Remove placeholder text such as `【功能名称】`, `[待补充]`, `[例如：]`, `[功能1]`, or `[不包含1]`.
3. Verify that goals are SMART and measurable.
4. Verify that functional requirements are actionable enough for design and engineering discussion.
5. Verify that the tone supports collaboration rather than issuing commands.
6. Tighten ambiguous wording. Replace weak terms such as `大约`, `可能`, `尽量`, or similarly vague phrasing.
7. Save the improved version to the same file path.

## Questioning Rules

- Ask only for information that materially improves the PRD.
- Ask concrete questions tied to missing template fields.
- Prefer questions that elicit measurable answers, constraints, examples, or rules.
- When the user gives a broad goal, drill into baseline, target value, and deadline.
- When the user gives a feature idea without boundaries, ask what is explicitly out of scope.
- When the user cannot provide data, ask for the best available proxy such as current process time, error rate, ticket volume, or conversion rate.

## Writing Rules

- Keep the template headings and numbering format intact.
- Preserve markdown readability and concise phrasing.
- Use bullet lists for scope, rules, risks, and acceptance criteria when that improves clarity.
- Express objectives with metrics, thresholds, owners, or time bounds whenever possible.
- Write user stories in the form `作为……，我希望……，从而……`.
- For `需求范围`, clearly separate `In Scope` and `Out of Scope`.
- For each functional requirement, include description, user value, interaction flow, business rules, boundary conditions, and exception handling.
- For `验收标准`, write testable Given-When-Then statements.

## Quality Bar

Enforce these principles in every output:

- Data-driven: ground the problem statement in observed behavior, user research, or operational data.
- SMART goals: make every core objective specific, measurable, achievable, relevant, and time-bound.
- Concise and clear: prefer precise statements over long explanations.
- Executable: provide enough detail for implementation and cross-functional review.
- Collaborative: phrase open questions, dependencies, and assumptions in a way that invites discussion.

## Template Handling

- Always load `./assets/prd-template.md` before drafting.
- Treat the template as mandatory output scaffolding.
- Update dates to the current working date when the user does not provide one.
- Fill unknown owner names or status with explicit values such as `待确认` only when the user did not specify them.
- Do not leave example text or placeholder markers in the final file.

## Output Pattern

When responding after writing the file:

1. State the saved file path. The path must be reported in the form `<当前项目根目录>/docs/requirements/<需求名称>-prd.md`. If the user explicitly overrode the directory in this call, restate the actual absolute path that was used.
2. Summarize the requirement name and any major assumptions.
3. Call out unresolved items that still need stakeholder confirmation.
