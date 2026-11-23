# daedalus-core evals

Eval suite for the `code-review` skill. Each case builds a synthetic git repository with its `fixture.sh`, runs the skill on it through `claude plugin eval`, and grades the report.

## Run

From `plugins/daedalus-core`:

```sh
./evals/run.sh --scaffold --trust-plugin --allow-tools "Bash(git *)" --runs 3 \
  --judge-model claude-haiku-5-5 --ablation none -j 8
```

- `run.sh` passes its arguments to `claude plugin eval`. It evaluates a temporary copy of the plugin without the `dependencies` field, because each eval run uses an isolated home where marketplace dependencies are not installed and the plugin would not load. Results go to `evals/results/`, which git ignores. It also copies `plugins/daedalus-python` into the `stack` case, because a case can load only plugins under the plugin being evaluated; run the suite through `run.sh`, not `claude plugin eval` directly.
- `--scaffold` runs the case fixtures. `--trust-plugin` confirms that you trust this repository's code.
- `--allow-tools "Bash(git *)"` lets the review run git and nothing else in the shell.
- Every case pins the model under test to `claude-sonnet-5-5`. Cases that reach the spec step and are not about the spec pass `--spec none`, so the review does not stop to ask for one. Every lens case also checks that its finding was verified (`Verifier: CONFIRMED`). `--judge-model` pins the judge for `llm` graders. The suite has none yet, so the judge model applies only if an `llm` grader is added.
- `--ablation none` skips the no-plugin baseline. Without the plugin the slash command does not exist, so the baseline measures nothing.
- One pass over the suite (17 cases, 1 run each) costs about $10 and takes about 3 minutes with `-j 8`.

To run one case, add `--case <name>`.

## Requirements

- Claude Code 2.1.269 or later, git 2.31 or later, and `python3`.
- A sandbox backend for the shell, because the suite grants Bash. See [sandboxing](https://code.claude.com/docs/en/sandboxing.md).
- On macOS, a git binary that is not the Xcode shim, placed before `/usr/bin` on `PATH`. For example, run `brew install git`. The shim `/usr/bin/git` calls `xcrun`, which keys its cache on `HOME`. Each eval run has a fresh `HOME`, and the sandbox blocks the cache write, so every git command fails with exit code 72.

## Cases

| Case | Fixture | Passes when |
| --- | --- | --- |
| `bad-ref` | A feature branch; the prompt names a base that does not exist | The run stops with `Review stopped: base ref ...` and starts no sub-agent |
| `empty-diff` | A clean checkout of `main` | The run stops with `Review stopped: no changes ...` and starts no sub-agent |
| `seeded-bug` | The diff adds `mean()`, which divides by `len - 1` | A C or H finding at `src/stats.py:13`, a blocking verdict, and at least 3 sub-agents (2 finders, 1 verifier) |
| `clean-change` | The diff adds a correct `mean()`; the prompt passes `--spec none` | The verdict is not blocking, every lens is available, the summary names the skipped `spec`, `tests`, `types`, and `stack` lenses with their reasons, and the spec section says `No spec available.` |
| `duplicate` | The diff adds `is_expired()` with an inverted comparison; the prompt names `main` as the base | Exactly one correctness finding at `src/tokens.py:9`, listing both correctness passes |
| `pre-existing` | `main` already has an inverted `percent_of()`; the diff adds a correct function to the same file | The finding at `src/money.py:11` is under "Pre-existing", not under "Introduced by this diff", and the verdict is not blocking |
| `uncommitted-flag` | A clean commit plus an unstaged `spread()` that subtracts in the wrong order | With `--uncommitted`: a C or H finding at `src/stats.py:18` and a blocking verdict |
| `uncommitted-no-flag` | The same fixture | Without the flag: no finding at `src/stats.py:18`, the gap `uncommitted changes not reviewed` in the summary, and a non-blocking verdict |
| `spec-ask` | A correct change with no spec file and no issue reference | The run asks `Where is the spec for this change?` and starts no sub-agent |
| `security` | The diff builds an SQL query from a request parameter | A C or H finding at `src/users.py:7` from the `security` lens, and a blocking verdict |
| `error-handling` | The diff adds `save_orders()`, which swallows `OSError` and returns `True` | A C or H finding at `src/orders.py:10-12` from the `error-handling` lens, and a blocking verdict |
| `standards` | `CODING_STANDARDS.md` forbids clock reads in `src/`; the diff calls `datetime.now()` and adds a Middle Man | An M finding at `src/invoices.py:7` from the `standards` lens that cites `CODING_STANDARDS.md`, the Middle Man smell at L, no smell graded above L, and a verdict that is not blocking |
| `spec` | `docs/specs/discount-codes.md` matches the branch; the diff ignores one requirement's `ValueError` and omits `describe_discount()` | A C or H finding at `src/discounts.py:8` from the `spec` lens that quotes the requirement, a coverage row `missing` for `describe_discount`, and a blocking verdict |
| `tests` | A pytest suite; the diff adds a test that asserts only `assert result` | An M finding at `tests/test_stats.py:8-10` from the `tests` lens, and a verdict that is not blocking |
| `types` | The diff adds a plain `@dataclass` documented as hashable and puts it in a set | A C or H finding at `src/grid.py:5-6` from the `types` lens, and a blocking verdict |
| `comments` | The diff adds a docstring that promises a `KeyError` the code never raises | An M finding at `src/directory.py:4-5` from the `comments` lens, and a verdict that is not blocking |
| `stack` | `daedalus-python` is loaded; the diff adds a mutable default argument | A C or H finding at `src/tags.py:4` from the `stack` lens that cites `python-patterns`, and a blocking verdict |

## Adding a case

Create `evals/<case>/case.yaml` and `evals/<case>/fixture.sh`. Copy an existing case. The fixture must build a git repository with synthetic code only; client code never enters this repository. Grade facts that a regex can match reliably: a `file:line`, a severity tag, a section heading, the verdict line, or a lens id in the summary.
