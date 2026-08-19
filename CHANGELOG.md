# Changelog

## 2026-08-14 — Khaton Studio 0.3.0

This release consolidates the Khaton Studio desktop update and the Windows distribution fixes. The editor now provides syntax-only checking, selected-code execution, live cursor line/column status, and Find & Replace with `Ctrl+F`. The repository-root launcher and PyInstaller spec explicitly collect the Khaton runtime so the packaged application does not depend on a source-tree import.

The Windows workflow now builds both the standalone `KhatonStudio.exe` and the Inno Setup installer. The installer script uses repository-relative paths, which prevents the previous missing-input failure during the Setup stage. Run the workflow named **Build Khaton Studio for Windows** from GitHub Actions or push a tag matching `studio-v*` to produce the downloadable artifact.

The core language remains educational and deterministic, with the existing interpreter, JSON bytecode path, standard libraries, structured exception handling, and regression tests preserved.


## Studio maintenance update

Khaton Studio now includes **Save Output** for exporting diagnostics and execution results to UTF-8 text, plus **Clear** for resetting the output panel without altering the source file. Existing `printty`, syntax checking, selection execution, cursor status, Find & Replace, and GitHub shortcut behavior remain intact.


## Bug-fix update

This maintenance update hardens runtime block handling so zero-count repeats skip their bodies and nested `if` blocks no longer consume a repeat terminator. It also adds clear validation for missing command arguments, rejects negative sleep durations, validates bytecode argument types and positive source lines, and reads CLI source files through context-managed UTF-8 helpers. Regression coverage now includes malformed bytecode, CLI compilation, nested control flow, zero-count repeats, and invalid command arguments.


## Deli conditional command

Khaton now uses `Deli` for else-if branches. It supports chained conditions with `if`, `Deli`, and `else`; the legacy `elif` spelling is intentionally rejected so the language contract remains unambiguous. The command count is now 40.
