# skills

This repository stores reusable Codex skills tracked in git for review and sharing.

## Layout

- `skills/`: skill definitions copied into this repository.
- `skills/<skill-name>/SKILL.md`: the main instruction file for each skill.
- `AGENTS.md`: contributor guidance for updating this repository.

## Included Skills

- `changelog-release-notes`: guidance for drafting changelogs and release notes from repository evidence.
- `create-github-pull-request-from-specification`: guidance for creating a GitHub pull request from a written specification.
- `generate-implementation-design`: guidance for turning a PRD into a Chinese implementation design document using staged clarification, a fixed template, and C4-oriented HLD/LLD structure.
- `requirements-analysis`: end-to-end business analysis delivery for process-heavy, compliance-bound systems — baseline and unknowns, a BRD with same-source AS-IS/TO-BE swimlanes, feature-to-story slicing by process stage, story cards with six-category acceptance criteria, and low-fidelity wireframes.

## Updating Skills

To add or refresh a skill, copy it from your local Codex skill directory into `skills/` and commit the result. Example:

```sh
cp -R ~/.codex/skills/<skill-name> skills/
git add skills/<skill-name>
git commit -m "Add <skill-name> skill"
```

Keep each skill in its own directory and avoid mixing unrelated changes in the same commit.
