from collections.abc import AsyncGenerator

from google.adk.agents.invocation_context import InvocationContext
from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.events import Event


MODEL = "gemini-3.5-flash"


class FinalPoemPipeline(SequentialAgent):
    """Keep intermediate state updates without displaying draft/review text."""

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        async for event in super()._run_async_impl(ctx):
            if event.author in {"PoemWriterAgent", "PoemReviewerAgent"}:
                # The runner must still receive actions (including output_key
                # state updates) before the next agent reads its instruction.
                event = event.model_copy(update={"content": None})
            yield event


# 1. Poem Writer
poem_writer_agent = LlmAgent(
    name="PoemWriterAgent",
    model=MODEL,
    description="Creates an original poem based on the user's requirements.",
    instruction="""
You are a creative poem-writing agent.

Create an original poem based on the user's request.

Follow the user's requirements for:
- topic
- language
- mood
- poetic format
- length
- rhyme, when requested

Supported formats may include:
- free verse
- rhyming poem
- haiku
- sonnet
- acrostic poem
- custom line or stanza counts

Give the poem an appropriate title unless the user asks for no title.

Do not copy existing poems, song lyrics, famous verses, or published poetry.

Output only the title and poem.
""",
    output_key="draft_poem",
)


# 2. Poem Reviewer
poem_reviewer_agent = LlmAgent(
    name="PoemReviewerAgent",
    model=MODEL,
    description="Reviews the generated poem against the user's request.",
    instruction="""
You are a poetry reviewer.

Review the following draft poem:

{draft_poem}

Evaluate whether the poem:

1. Matches the user's requested topic.
2. Uses the requested language.
3. Matches the requested mood.
4. Follows the requested poem format.
5. Follows the requested length.
6. Uses rhyme correctly when requested.
7. Sounds natural and coherent.
8. Appears original.

Provide concise feedback describing only changes that are actually needed.

If the poem already satisfies the request well, respond with:

No major changes needed.
""",
    output_key="review_feedback",
)


# 3. Poem Refiner
poem_refiner_agent = LlmAgent(
    name="PoemRefinerAgent",
    model=MODEL,
    description="Produces the final poem using the draft and review feedback.",
    instruction="""
You are a poem refinement agent.

Original draft:

{draft_poem}

Reviewer feedback:

{review_feedback}

Create the final version of the poem.

Apply useful reviewer feedback while preserving the user's original request.

If the reviewer says "No major changes needed.", keep the original poem
unless a very small correction is necessary.

Output only the final poem and its title, unless the user asks for no title.
When the user asks for no title, output only the poem without a title.

Do not include review comments, explanations, or notes.
""",
    output_key="final_poem",
)


# Run the agents in order:
# Writer -> Reviewer -> Refiner
root_agent = FinalPoemPipeline(
    name="PoemWritingPipeline",
    sub_agents=[
        poem_writer_agent,
        poem_reviewer_agent,
        poem_refiner_agent,
    ],
    description=(
        "Creates, reviews, and refines poems based on user requirements."
    ),
)
