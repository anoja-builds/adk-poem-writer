"""Exercise the real ADK runner without API calls or credentials."""

import unittest
from contextlib import ExitStack
from unittest.mock import patch

from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.models.base_llm import BaseLlm
from google.adk.models.llm_response import LlmResponse
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from poem_writer.agent import root_agent


class ScriptedModel(BaseLlm):
    model: str = "offline-test"
    response: str
    expected_instruction: tuple[str, ...] = ()

    async def generate_content_async(self, llm_request, stream=False):
        instruction = llm_request.config.system_instruction
        for expected in self.expected_instruction:
            assert expected in instruction, (expected, instruction)
        assert any(
            part.text == "Write about rain with no title."
            for content in llm_request.contents
            if content.role == "user"
            for part in content.parts or []
        ), "The original request must reach each stage"
        if stream:
            yield LlmResponse(
                content=types.Content(
                    role="model", parts=[types.Part(text=self.response[:5])]
                ),
                partial=True,
            )
        yield LlmResponse(
            content=types.Content(
                role="model", parts=[types.Part(text=self.response)]
            ),
            partial=False,
        )


class PipelineTests(unittest.IsolatedAsyncioTestCase):
    async def check_pipeline(self, streaming):
        draft = "Rain taps the window."
        feedback = "Make the imagery more vivid."
        final = "Silver rain taps the window."
        models = [
            ScriptedModel(response=draft),
            ScriptedModel(response=feedback, expected_instruction=(draft,)),
            ScriptedModel(
                response=final,
                expected_instruction=(draft, feedback, "without a title"),
            ),
        ]
        sessions = InMemorySessionService()
        session = await sessions.create_session(app_name="poem_writer", user_id="test")
        runner = Runner(
            agent=root_agent, app_name="poem_writer", session_service=sessions
        )
        with ExitStack() as stack:
            for agent, model in zip(root_agent.sub_agents, models):
                stack.enter_context(patch.object(agent, "model", model))
            events = [
                event
                async for event in runner.run_async(
                    user_id="test",
                    session_id=session.id,
                    new_message=types.Content(
                        role="user",
                        parts=[types.Part(text="Write about rain with no title.")],
                    ),
                    run_config=RunConfig(streaming_mode=streaming),
                )
            ]
        visible = [event for event in events if event.content]
        self.assertTrue(visible)
        self.assertTrue(all(e.author == "PoemRefinerAgent" for e in visible))
        self.assertEqual(visible[-1].content.parts[0].text, final)
        saved = await sessions.get_session(
            app_name="poem_writer", user_id="test", session_id=session.id
        )
        self.assertEqual(saved.state["draft_poem"], draft)
        self.assertEqual(saved.state["review_feedback"], feedback)
        self.assertEqual(saved.state["final_poem"], final)

    async def test_final_only_with_state_handoff(self):
        await self.check_pipeline(StreamingMode.NONE)

    async def test_streaming_does_not_leak_intermediate_text(self):
        await self.check_pipeline(StreamingMode.SSE)
