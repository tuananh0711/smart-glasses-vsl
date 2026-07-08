# Rule: External Codex Handoff

When a task involves implementation, coding, or writing documentation, follow this workflow for the final testing phase:

1. **Internal QC First**: Ensure the work has passed the internal `QC-1` subagent first.
2. **Generate agent_for_codex.md**: Once internal QC-1 is passed, ALWAYS write the handoff instructions to a file named `D:\do_an_tot_nghiep\agent_for_codex.md`.
3. **agent_for_codex.md Requirements**: The file MUST contain:
   - A list of the specific files that were just modified.
   - A brief summary of what was changed and the objective.
   - Explicit instructions for the external Codex IDE to:
     - Check the modified files for logical flaws, security vulnerabilities, edge cases, and formatting errors.
     - Evaluate independently without trusting QC-1's pass as the final proof.
     - Output its feedback to `qc_report.md`.
     - If FAIL: State clearly the file, error, reason, and fix.
     - If PASS: Simply write "PASS" in `qc_report.md`.
4. **Notify User**: Inform the user that `agent_for_codex.md` is ready, and they can trigger their Codex IDE to begin the final QC.
5. **Final Evaluation**: Upon the user returning with Codex's results, read `qc_report.md`. If it says "PASS", the task is successful. If FAIL, fix the errors and repeat.
