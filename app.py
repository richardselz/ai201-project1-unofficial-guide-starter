"""
Milestone 5 — Query interface for The Unofficial Guide.

A minimal Gradio web UI over the grounded generation pipeline. Enter a
question about an OMSCS course; the app retrieves relevant chunks, generates
a grounded answer with Groq, and shows which course pages were retrieved.

Run:  python app.py   then open http://localhost:7860
"""

import gradio as gr

from generate import answer


def handle_query(question):
    if not question or not question.strip():
        return "Please enter a question.", ""
    result = answer(question)
    sources = "\n".join(f"• {s}" for s in result["sources"])
    if not sources:
        sources = "(none — not enough information in the course documents)"
    return result["answer"], sources


with gr.Blocks(title="The Unofficial Guide — OMSCS") as demo:
    gr.Markdown(
        "# The Unofficial Guide — OMSCS Courses\n"
        "Ask about Georgia Tech OMSCS courses. Answers are grounded **only** "
        "in the official course pages; if the documents don't cover it, the "
        "system says so instead of guessing."
    )
    question = gr.Textbox(
        label="Your question",
        placeholder="e.g. What Apple hardware is not supported in CS 6210?",
    )
    ask_btn = gr.Button("Ask", variant="primary")
    answer_box = gr.Textbox(label="Answer", lines=8)
    sources_box = gr.Textbox(label="Retrieved from", lines=4)

    ask_btn.click(handle_query, inputs=question,
                  outputs=[answer_box, sources_box])
    question.submit(handle_query, inputs=question,
                    outputs=[answer_box, sources_box])


if __name__ == "__main__":
    demo.launch()
