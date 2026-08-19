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
- [ ] Publish the bug-fix release and build a new Windows EXE/Setup
