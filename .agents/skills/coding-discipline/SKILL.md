---
name: coding-discipline
description: Enforces Karpathy-inspired simplicity and Superpowers TDD methods to ensure clean, lean, and correct Python code. Use when writing, refactoring, or reviewing codebase files.
---

# Coding Discipline Guide

This skill enforces strict programming standards combining simplicity, surgical edits, and test-driven development.

## Core Rules

### 1. Simplicity First (YAGNI & DRY)
- Build ONLY what was explicitly requested. Do not add speculative "future proof" configurations or extra parameters.
- Do not build abstractions (classes, factories, inheritance) for code that is only used once. Prefer direct functions.
- If a script is unnecessarily long or overcomplicated, rewrite it. Keep logic compact and clean.

### 2. Surgical Edits
- Do not modify adjacent formatting, imports, or comments that are unrelated to your current task.
- Match the existing style and conventions of the file you are editing.
- Do not clean up unrelated dead code unless explicitly requested.

### 3. Test-Driven Development (TDD)
- Define verification criteria (tests) before finishing implementation.
- Run tests continuously. If tests fail, stop and fix the bug immediately.
- Use the checklist at `.agents/skills/coding-discipline/references/checklist.md` before finalizing edits.
