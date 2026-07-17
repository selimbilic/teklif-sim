# Coding Discipline Checklist

Use this checklist to self-review before committing any code changes:

- [ ] **No Speculative Code:** Have I added any features, parameters, or imports "just in case"? If yes, delete them.
- [ ] **Surgical Edits:** Did I modify lines of code that were unrelated to my ticket/task? If yes, revert them.
- [ ] **Simple Abstractions:** Did I introduce a class where a simple function would do? If yes, simplify.
- [ ] **Single Responsibility:** Does each function/module do exactly one thing?
- [ ] **Style Consistency:** Does the code match the existing style (variable names, docstrings, formatting)?
- [ ] **Test Coverage:** Are there tests verifying the new behavior? Have I run `pytest` to verify?
- [ ] **No Dead Code:** Have I removed any print statement debugging or commented-out code before requesting review?
