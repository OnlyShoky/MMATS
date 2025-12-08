You are an expert full-stack software architect and developer specialized in algorithmic trading platforms. Your task is to **implement the PRS for a Multi-Market Automated Trading System**, using the PRS located at `docs/PRS.md` and the already generated documentation in `docs/product_info/`.  

Objectives:

1. Read and fully understand the PRS at `docs/PRS.md`.
2. Use the existing documentation in `docs/product_info/ES/` and `docs/product_info/ENG/` as reference and update them as needed while implementing.
3. Implement the system **step by step**, stopping at each key milestone so I can:
    - Review
    - Test
    - Git commit
    - Provide credentials or environment variables if needed

4. For each step, provide:
    - **Description of the implementation step**
    - **Code or folder structure** (scaffold or minimal runnable example)
    - **Documentation updates** in Markdown if needed
    - **Testing instructions**: what to run, what to observe, expected output
    - **Notes for credentials or `.env` updates** if required

5. Implementation order:
    - Core engine and modular architecture
    - Data pipelines and adapters
    - Market adapters (start with Crypto or Forex)
    - Strategy interface and sample model
    - Backtesting and paper trading scaffolding
    - Risk management module
    - UI scaffolding
    - Optional AI/LLM news module (stub for now)

6. Step-by-step execution rules:
    - Each step must be **self-contained and testable**
    - Stop after each step for my confirmation/commit
    - Include brief explanations of what is happening and why
    - Clearly indicate if any action is required from me (API keys, credentials, environment updates)

7. Documentation rules:
    - Use Markdown compatible with Obsidian
    - Include headers, links, tables, and diagrams when helpful
    - Cross-reference PRS sections

Instructions:

- Begin by reading `docs/PRS.md` and confirming the main modules and architecture.
- Start implementing the **first step**: project scaffolding and folder structure, including:
    - `src/` (code)
    - `docs/` (documentation)
    - `.env.example` (placeholders for credentials)
    - `README.md` (project overview)
- Provide **minimal testing instructions** for this first step.
- Stop after this first step and wait for my confirmation before continuing.
