# Third-Party Notices

Parts of this repository are adapted from the projects below. Each is distributed under the MIT License, reproduced below, unless its row names the Apache License 2.0, which is reproduced at the end of this file.

| File | Adapted from | Copyright |
|---|---|---|
| `plugins/daedalus-core/rules/testing.md` | [everything-claude-code](https://github.com/affaan-m/everything-claude-code), `rules/common/testing.md` (agent references removed) | Copyright (c) 2026 Affaan Mustafa |
| `plugins/daedalus-java/skills/java-coding-standards/SKILL.md`, `plugins/daedalus-springboot/skills/spring-coding-standards/SKILL.md` | everything-claude-code, `skills/java-coding-standards/SKILL.md` (split into framework-agnostic and Spring parts; Quarkus parts removed) | Copyright (c) 2026 Affaan Mustafa |
| `plugins/daedalus-springboot/skills/{springboot-patterns,springboot-security,springboot-verification,hexagonal-architecture,jpa-patterns}/SKILL.md`, `plugins/daedalus-core/skills/security-review/SKILL.md` | everything-claude-code, same skill names under `skills/` (unchanged) | Copyright (c) 2026 Affaan Mustafa |
| `plugins/daedalus-infra/skills/docker-patterns/SKILL.md` | everything-claude-code, `skills/docker-patterns/SKILL.md` (ECC installer-harness section removed) | Copyright (c) 2026 Affaan Mustafa |
| `plugins/daedalus-postgres/skills/postgres-patterns/SKILL.md` | everything-claude-code, `skills/postgres-patterns/SKILL.md` (references to absent agents and skills removed; restart note added for `max_connections`), itself based on Supabase Agent Skills (MIT) | Copyright (c) 2026 Affaan Mustafa |
| `plugins/daedalus-springboot/agents/java-build-resolver.md` | everything-claude-code, `agents/java-build-resolver.md` (skill references updated) | Copyright (c) 2026 Affaan Mustafa |
| `plugins/daedalus-python/skills/python-patterns/SKILL.md`, `plugins/daedalus-fastapi/skills/fastapi-patterns/SKILL.md`, `plugins/daedalus-frontend/skills/{e2e-testing,make-interfaces-feel-better}/SKILL.md`, `plugins/daedalus-react/skills/frontend-patterns/SKILL.md`, `plugins/daedalus-nextjs/skills/nextjs-turbopack/SKILL.md` | everything-claude-code, same skill names under `skills/` (unchanged) | Copyright (c) 2026 Affaan Mustafa |
| `plugins/daedalus-python/skills/python-testing/SKILL.md`, `plugins/daedalus-react/skills/react-testing/SKILL.md` | everything-claude-code, same skill names under `skills/` (TDD workflow sections removed in favor of `mattpocock-skills:tdd`; references to absent agents, rules, and commands removed) | Copyright (c) 2026 Affaan Mustafa |
| `plugins/daedalus-typescript/skills/typescript-patterns/SKILL.md`, `plugins/daedalus-frontend/skills/{accessibility,vite-patterns}/SKILL.md`, `plugins/daedalus-react/skills/{react-patterns,frontend-a11y}/SKILL.md` | everything-claude-code, same skill names under `skills/` (references to absent agents, rules, commands, and skills removed or renamed) | Copyright (c) 2026 Affaan Mustafa |
| `plugins/daedalus-react/skills/react-performance/SKILL.md` | everything-claude-code, `skills/react-performance/SKILL.md` (references to absent agents, rules, and commands removed), itself adapted from Vercel Labs [agent-skills](https://github.com/vercel-labs/agent-skills) `react-best-practices` (MIT) | Copyright (c) 2026 Affaan Mustafa |
| `plugins/daedalus-react/agents/react-build-resolver.md` | everything-claude-code, `agents/react-build-resolver.md` (references updated) | Copyright (c) 2026 Affaan Mustafa |
| `plugins/daedalus-core/rules/engineering.md`, sections 1–3 | [andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills), `skills/karpathy-guidelines/SKILL.md` (rewritten) | Copyright (c) forrestchang |
| `plugins/daedalus-core/skills/code-review/references/suppression.md`, `plugins/daedalus-core/skills/code-review/references/lenses/correctness.md` | [claude-plugins-official](https://github.com/anthropics/claude-plugins-official/tree/73c8cf3ea7e296057b467990f2f5d61b4c922260), `plugins/code-review/commands/code-review.md`, under the Apache License 2.0. Changes: the false-positive list and the high-signal bug criteria were reworded, grouped by category, extended, and split into two read strategies. Each adapted file starts with a notice of these changes. | Copyright Anthropic |
| `plugins/daedalus-writing/skills/vietnamizer/` | [finolabs/vietnamizer](https://github.com/finolabs/vietnamizer/tree/78ed5f7f0b40601ddbfb6a901203b79c45c9df11) | Copyright (c) 2026 Fioenix |
| `plugins/daedalus-writing/skills/clarity/` | [addyosmani/clarity](https://github.com/addyosmani/clarity/tree/e27ceeff60368cf6966b4ea00a5b9b36418ee9a0) | Copyright (c) 2026 Addy Osmani |
| `plugins/daedalus-writing/skills/natural-japanese/` | [coji/natural-japanese](https://github.com/coji/natural-japanese/tree/840bd400cbcb64c8b64d492a144da54fc05776c5) | Copyright (c) 2026 coji |
| `plugins/daedalus-writing/skills/slop-nuki/` | [chezou/slop-nuki](https://github.com/chezou/slop-nuki/tree/1bdf627b5991f4f806069619c9bde407960feac7) | Copyright (c) 2026 Aki Ariga |

The writing skills include their upstream licenses. `slop-nuki` adapts [stop-slop](https://github.com/hardikpandya/stop-slop) (MIT, Copyright (c) 2025 Hardik Pandya).

`daedalus-core` depends on [mattpocock-skills](https://github.com/mattpocock/skills) (MIT, Copyright (c) 2026 Matt Pocock), which is installed from its own marketplace and is not redistributed here.

The marketplace also lists [caveman](https://github.com/JuliusBrussee/caveman) (Apache-2.0 since 3.0.0, Copyright 2026 Julius Brussee) and [ponytail](https://github.com/DietrichGebert/ponytail) (MIT, Copyright (c) 2026 DietrichGebert) by pinned commit. Both are fetched from their upstream repositories at install time and are not redistributed here.

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

## Apache License 2.0

```text

                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS

   APPENDIX: How to apply the Apache License to your work.

      To apply the Apache License to your work, attach the following
      boilerplate notice, with the fields enclosed by brackets "[]"
      replaced with your own identifying information. (Don't include
      the brackets!)  The text should be enclosed in the appropriate
      comment syntax for the file format. We also recommend that a
      file or class name and description of purpose be included on the
      same "printed page" as the copyright notice for easier
      identification within third-party archives.

   Copyright [yyyy] [name of copyright owner]

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
```
