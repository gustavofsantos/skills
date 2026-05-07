# Session: 010-sync-readme-with-plugin-skills-7b2f367

**Date:** 2026-05-07
**Issue:** 010 — Sync README with plugin skills
**Commits:** 7b2f367

## Objective
Update README.md so every skill in `skills/` has a matching row in the correct table, and every row accurately reflects its `description` frontmatter.

## Key decisions
- Confirmed all four missing skills (session-close, survey, provenance, project-setup) are user-invocable with no exclusion flags in frontmatter
- Placed session-close in Orchestration table, survey and provenance in Knowledge Management, and project-setup in Integrations, based on their purpose
- Verified existing 18 rows all matched their frontmatter descriptions exactly before adding new entries

## Context used
(none)

## Tasks
- [x] Read `description` and `user-invocable` frontmatter for the four missing skills
- [x] Add rows for user-invocable missing skills to the correct README tables 7b2f367
- [x] Verify all existing rows match their skill's `description` frontmatter first sentence
- [x] Fix any stale descriptions found

## Outcome
Completed