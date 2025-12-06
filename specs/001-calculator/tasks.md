# Tasks: Simple Calculator

**Input**: Design documents from `/specs/001-calculator/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The calculator constitution (V. Test-Driven Development) mandates TDD, so tests will be included.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths shown below assume single project - adjust based on plan.md structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project directories: `src/`, `tests/`
- [ ] T002 Initialize Python project (e.g., `pyproject.toml` or `setup.py`)
- [ ] T003 [P] Configure basic linting and formatting (e.g., `flake8`, `black`)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure for expression parsing and evaluation that MUST be complete before ANY user story can be implemented.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 Create `calculator.py` in `src/` to house core logic
- [ ] T005 Create `test_calculator.py` in `tests/` for unit tests
- [ ] T006 Implement a basic expression tokenizer in `src/calculator.py`
- [ ] T007 Implement a basic expression parser (e.g., using shunting-yard algorithm or recursive descent) in `src/calculator.py`
- [ ] T008 Implement a safe expression evaluator (handling operator precedence and parentheses) in `src/calculator.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Perform Basic Arithmetic (Priority: P1) 🎯 MVP

**Goal**: Implement and verify the core functionality of evaluating basic arithmetic expressions.

**Independent Test**: Can be fully tested by providing various valid arithmetic expressions and asserting the correct numerical output.

### Tests for User Story 1 (Mandatory due to TDD principle)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T009 [US1] Write unit tests for addition in `tests/test_calculator.py`
- [ ] T010 [P] [US1] Write unit tests for subtraction in `tests/test_calculator.py`
- [ ] T011 [P] [US1] Write unit tests for multiplication in `tests/test_calculator.py`
- [ ] T012 [P] [US1] Write unit tests for division in `tests/test_calculator.py`
- [ ] T013 [P] [US1] Write unit tests for operator precedence and parentheses in `tests/test_calculator.py`

### Implementation for User Story 1

- [ ] T014 [US1] Refine tokenizer to handle integers and floats in `src/calculator.py`
- [ ] T015 [US1] Refine parser to handle operator precedence and parentheses in `src/calculator.py`
- [ ] T016 [US1] Refine evaluator to return correct numerical results for valid expressions in `src/calculator.py`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Handle Division by Zero (Priority: P2)

**Goal**: Implement robust error handling for division by zero scenarios.

**Independent Test**: Can be tested by providing expressions that include division by zero and verifying the appropriate error message is returned.

### Tests for User Story 2 (Mandatory due to TDD principle)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T017 [US2] Write unit tests for division by zero in `tests/test_calculator.py`

### Implementation for User Story 2

- [ ] T018 [US2] Modify evaluator to detect and raise a specific "Division by zero" error in `src/calculator.py`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Handle Invalid Input (Priority: P2)

**Goal**: Implement comprehensive input validation to catch invalid expressions and non-numeric input.

**Independent Test**: Can be tested by providing malformed expressions or non-numeric input and verifying the appropriate error message is returned.

### Tests for User Story 3 (Mandatory due to TDD principle)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T019 [US3] Write unit tests for invalid expression syntax (e.g., "2 + abc") in `tests/test_calculator.py`
- [ ] T020 [P] [US3] Write unit tests for incomplete expressions (e.g., "2 + ") in `tests/test_calculator.py`
- [ ] T021 [P] [US3] Write unit tests for empty or whitespace-only input in `tests/test_calculator.py`

### Implementation for User Story 3

- [ ] T022 [US3] Enhance tokenizer/parser to detect and raise a specific "Invalid expression" error for malformed input in `src/calculator.py`
- [ ] T023 [US3] Add checks for empty or whitespace-only input in `src/calculator.py`

**Checkpoint**: All user stories should now be independently functional

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T024 Code cleanup and refactoring in `src/calculator.py`
- [ ] T025 Ensure all tests pass and achieve good code coverage
- [ ] T026 Add a basic command-line interface (CLI) to `main.py` for interaction.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Depends on core evaluation from US1 but should be independently testable for its specific error handling.
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Depends on core parsing from US1 but should be independently testable for its specific error handling.

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services (N/A for this project as it's a single module)
- Services before endpoints (N/A for this project)
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows, with careful integration planning for US2 and US3).
- All tests for a user story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members (with careful coordination for US2 and US3).

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Write unit tests for addition in tests/test_calculator.py"
Task: "Write unit tests for subtraction in tests/test_calculator.py"
Task: "Write unit tests for multiplication in tests/test_calculator.py"
Task: "Write unit tests for division in tests/test_calculator.py"
Task: "Write unit tests for operator precedence and parentheses in tests/test_calculator.py"

# Implementation tasks are sequential after tests fail
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
