
"""Pipeline skeleton for FORGe

This file provides the high-level structure and TODOs for the end-to-end
pipeline that composes modules in ``src/core``.

Only imports and TODOs are present here — implementation belongs in the
individual core modules and a future orchestrator implementation.
"""

# Public imports from core components (skeleton only)
from core import speech_to_text as speech_to_text
from core import text_to_ticket as text_to_ticket
from core import natural_language_understanding as natural_language_understanding
from core import text_to_speech as text_to_speech
from core import post_to_n8n as post_to_n8n

def run_pipeline(input_source: str, config: dict) -> dict:
	"""
	Orchestrate the full pipeline.

	Raises:
	    NotImplementedError: This is a skeleton placeholder.
	"""

	# TODO: Implement orchestration logic here.
	raise NotImplementedError(
		"Pipeline orchestration not implemented — see TODOs in function docstring"
	)


__all__ = ["run_pipeline"]