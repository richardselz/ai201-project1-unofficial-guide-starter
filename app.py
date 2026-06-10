"""
Milestone 5 — Query interface for The Unofficial Guide.

A minimal Gradio web UI over the grounded generation pipeline. Enter a
question about an OMSCS course; the app retrieves relevant chunks, generates
a grounded answer with Groq, and shows which course pages were retrieved.

A toggle switches the free-text box for a dropdown of the planning.md
evaluation questions, which makes the demo / evaluation run easy to drive.

Run:  python app.py   then open http://localhost:7860
"""

import gradio as gr

from generate import answer

# The evaluation questions from planning.md (Q4 is the out-of-scope refusal).
EVAL_QUESTIONS = [
    "Who is the Head TA of CS 6035?",
    "What courses does Wenke Lee teach?",
    "What Apple hardware is not supported in CS 6210?",
    "How many of the courses are considered foundational?",
    "Which course recommends understanding the three-way handshake of TCP?",
    "Which course teaches the need for a trusted computing base (TCB)?",
]


def handle_query(use_dropdown, typed_question, picked_question):
    question = picked_question if use_dropdown else typed_question
    if not question or not question.strip():
        return "Please enter or select a question.", ""
    result = answer(question)
    sources = "\n".join(f"• {s}" for s in result["sources"])
    if not sources:
        sources = "(none — not enough information in the course documents)"
    return result["answer"], sources


def toggle_input(use_dropdown):
    # Show the dropdown when toggled on, the free-text box otherwise.
    return gr.update(visible=not use_dropdown), gr.update(visible=use_dropdown)


with gr.Blocks(title="The Unofficial Guide — OMSCS") as demo:
    gr.Markdown(
        "# The Unofficial Guide — OMSCS Courses\n"
        "Ask about Georgia Tech OMSCS courses. Answers are grounded **only** "
        "in the official course pages; if the documents don't cover it, the "
        "system says so instead of guessing."
    )

    use_dropdown = gr.Checkbox(
        label="Use a provided evaluation question", value=False
    )
    question = gr.Textbox(
        label="Your question",
        placeholder="e.g. What Apple hardware is not supported in CS 6210?",
        visible=True,
    )
    eval_dropdown = gr.Dropdown(
        label="Evaluation question",
        choices=EVAL_QUESTIONS,
        value=EVAL_QUESTIONS[0],
        visible=False,
    )

    ask_btn = gr.Button("Ask", variant="primary")
    answer_box = gr.Textbox(label="Answer", lines=8)
    sources_box = gr.Textbox(label="Retrieved from", lines=4)

    use_dropdown.change(
        toggle_input, inputs=use_dropdown, outputs=[question, eval_dropdown]
    )

    inputs = [use_dropdown, question, eval_dropdown]
    ask_btn.click(handle_query, inputs=inputs, outputs=[answer_box, sources_box])
    question.submit(handle_query, inputs=inputs, outputs=[answer_box, sources_box])


if __name__ == "__main__":
    demo.launch()
