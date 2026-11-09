# Third-Party Notices

Parts of this repository are adapted from the projects below. Each is distributed under the MIT License, reproduced at the end of this file.

| File | Adapted from | Copyright |
|---|---|---|
| `plugins/daedalus-core/rules/testing.md` | [everything-claude-code](https://github.com/affaan-m/everything-claude-code), `rules/common/testing.md` (agent references removed) | Copyright (c) 2026 Affaan Mustafa |
| `plugins/daedalus-java/skills/java-coding-standards/SKILL.md`, `plugins/daedalus-springboot/skills/spring-coding-standards/SKILL.md` | everything-claude-code, `skills/java-coding-standards/SKILL.md` (split into framework-agnostic and Spring parts; Quarkus parts removed) | Copyright (c) 2026 Affaan Mustafa |
| `plugins/daedalus-springboot/skills/{springboot-patterns,springboot-security,springboot-verification,hexagonal-architecture,jpa-patterns}/SKILL.md`, `plugins/daedalus-core/skills/security-review/SKILL.md` | everything-claude-code, same skill names under `skills/` (unchanged) | Copyright (c) 2026 Affaan Mustafa |
| `plugins/daedalus-infra/skills/docker-patterns/SKILL.md` | everything-claude-code, `skills/docker-patterns/SKILL.md` (ECC installer-harness section removed) | Copyright (c) 2026 Affaan Mustafa |
| `plugins/daedalus-springboot/skills/postgres-patterns/SKILL.md` | everything-claude-code, `skills/postgres-patterns/SKILL.md` (references to absent agents and skills removed), itself based on Supabase Agent Skills (MIT) | Copyright (c) 2026 Affaan Mustafa |
| `plugins/daedalus-springboot/agents/java-build-resolver.md` | everything-claude-code, `agents/java-build-resolver.md` (skill references updated) | Copyright (c) 2026 Affaan Mustafa |
| `plugins/daedalus-core/rules/engineering.md`, sections 1–3 | [andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills), `skills/karpathy-guidelines/SKILL.md` (rewritten) | Copyright (c) forrestchang |

`daedalus-core` depends on [mattpocock-skills](https://github.com/mattpocock/skills) (MIT, Copyright (c) 2026 Matt Pocock), which is installed from its own marketplace and is not redistributed here.

The marketplace also lists [caveman](https://github.com/JuliusBrussee/caveman) (MIT, Copyright (c) 2026 Julius Brussee) and [ponytail](https://github.com/DietrichGebert/ponytail) (MIT, Copyright (c) 2026 DietrichGebert) by pinned commit. Both are fetched from their upstream repositories at install time and are not redistributed here.

## MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
