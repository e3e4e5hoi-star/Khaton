# Khaton Studio Update TODO

- [x] Refresh the Studio visual design with a polished Khaton-branded dark interface
- [x] Add the public GitHub repository link inside Studio and README
- [x] Preserve Syntax Check, Run Selection, Cursor Status, and Find & Replace
- [x] Run Python tests and syntax validation
- [x] Push the update and build a new Windows EXE and Setup artifact
- [x] Attach the new EXE and Setup here with the GitHub link (artifact link supplied; local attachment download was network-limited)
- [x] Attach the GitHub artifact files directly in this chat after successful download

- [x] Rename the Khaton output command from print to printty across lexer, parser, runtime, bytecode, examples, Studio, README, and tests
- [x] Add a regression test proving printty executes and legacy print is rejected or handled according to the new language contract

- [x] Select and implement one useful Khaton language or Studio upgrade while preserving printty and existing behavior
- [x] Add regression tests and update README/examples for the new upgrade
- [x] Push the upgrade and produce a fresh Windows Studio build

- [x] Audit interpreter edge cases: malformed commands, divisions, loops, conditionals, exceptions, and input arity
- [x] Audit bytecode validation and round-trip behavior, including malformed JSON and unsupported instructions
- [x] Audit CLI error handling, file encoding, exit codes, and missing arguments
- [x] Audit Studio thread safety, dialogs, output saving, highlighting, and bundled paths
- [x] Add regression tests for every confirmed bug and update documentation
- [x] Publish the bug-fix release and build a new Windows EXE/Setup

- [x] Rename the Khaton conditional command from elif to Deli across lexer, runtime, bytecode, examples, Studio, README, and tests
- [x] Add regression coverage proving Deli works and legacy elif is rejected under the new language contract
- [x] Publish the Deli update and build a fresh Windows EXE/Setup

- [ ] Create an independent Khaton introduction and documentation website without modifying the Lila web project
- [ ] Showcase printty, Deli, bytecode, 17 libraries, Khaton Studio, and recent bug fixes
- [ ] Add install guide, code examples, navigation, GitHub link, and responsive documentation sections
- [ ] Verify responsive rendering and content accuracy before delivery

- [x] Profile interpreter execution on repeat, arithmetic, conditionals, and bytecode paths
- [x] Reduce avoidable repeated parsing/value resolution and fix confirmed small runtime bugs
- [x] Add performance guardrails and regression tests without using flaky hard time limits
- [x] Update README/changelog, publish the fix, and build a fresh Windows EXE/Setup

- [x] Re-audit remaining runtime edge cases in Deli/else, repeat nesting, try blocks, and mutable state
- [x] Re-audit bytecode malformed-input handling and CLI command behavior
- [x] Re-audit Studio run/save/output interactions and bundled asset paths
- [x] Add regression tests for confirmed issues and publish a new Windows build

- [x] Deep-audit expression parsing, block matching, try nesting, and runtime state reset between runs
- [x] Deep-audit bytecode schema validation, CLI exit/error behavior, and Studio packaging paths
- [x] Add regression tests for each newly confirmed bug and update changelog
- [x] Publish the second bug-fix pass and build a fresh Windows EXE/Setup
