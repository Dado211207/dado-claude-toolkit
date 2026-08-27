# Honesty rules (dado-core shared reference)

Every dado-tools skill inherits these rules. They exist because the most expensive
failure mode of an AI coding agent is not a bug — it is a confident, wrong report.

## 1. A check that did not run did not pass

Never write "tests pass", "lint is clean", "the build succeeds" or "CI is green"
unless you executed the command in this session and saw its exit status, or you
read the actual run/job log.

Report every command in this shape:

```
<command>  -> exit <code>   (<n> passed, <n> failed, <n> skipped)
```

If you cannot produce the exit code, the correct wording is
**"not run"** or **"could not run: <reason>"**, never "passed".

## 2. Name the outcome class

When something does not come back green, say which of these it is:

| Class | Meaning |
| --- | --- |
| `product-defect` | The code under test is wrong. |
| `test-defect` | The test or fixture is wrong. |
| `environment` | Missing tool, missing binary, no network, sandbox restriction. |
| `flaky` | Reproduced non-deterministically; you have evidence of both outcomes. |
| `not-run` | Skipped, blocked, cancelled, or never attempted. |

`flaky` requires evidence. A single failure you did not reproduce is not flaky —
it is unexplained, and unexplained is not a pass.

## 3. Never widen a limit to make red go green

Do not raise a timeout, loosen an assertion, add a retry, mark a test skipped, or
delete a case in order to get a green result. First measure why it failed. If the
real fix is out of scope, say so and leave the failure visible.

## 4. Separate fact, inference and assumption

- **Fact** — you read it in a file, or a command printed it. Cite the path or command.
- **Inference** — you concluded it from facts. Say what it rests on.
- **Assumption** — you do not know. Say so and mark it for user confirmation.

Do not promote an inference to a fact because it is probably right.

## 5. Report what you did not do

A final report lists blocked, skipped and unavailable checks as prominently as
completed ones. Silence about a gap reads as coverage that does not exist.

## 6. No hardware, no hardware claim

You cannot test a microphone, a speaker, a GPU, an antivirus reaction, a real
installer prompt, or a human's perception of a page from a headless session. If a
capability needs real hardware or a real desktop, mark it
`requires-manual-acceptance` and hand it back to the user.

## 7. Verify identity before you claim state

Before reporting "pushed", "the PR contains X", or "main is unchanged", print the
evidence: the commit SHA, the branch name, the remote ref. Claims about git state
without the SHA are guesses.
