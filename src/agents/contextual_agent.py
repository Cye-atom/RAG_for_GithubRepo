from pydantic_ai import Agent, RunContext

system_prompt = """
Your function is to provide context for the text you will receive, based on the directory structure defined in the `directory_context` function. Each text fragment you receive will be one of the following cases:
- A concatenation of multiple files within a root folder, where transitions between files are marked in the text.
- A single file that has been split because it is too large. In this case, the beginning of the file will indicate which part it is: Part (m/n), where m ≤ n.
You should return, in under 200 characters, the context in which this document appears, as well as the main topics and technologies it covers. The goal is to clarify which files are included in each fragment, which subdirectories exist, and what is being addressed.
"""


contextual_agent = Agent(
    'openai:chatgpt-4o-latest',
    system_prompt=system_prompt,
    result_type=str,
    deps_type=str,
    retries=2,
)


@contextual_agent.system_prompt
def root_folder(ctx: RunContext[str]) -> str:
    return f'O texto pertence a pasta {ctx.deps}, situada na raiz'
