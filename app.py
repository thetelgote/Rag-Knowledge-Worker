import gradio as gr
from dotenv import load_dotenv
from implementation.answer import answer_question
from ingestion.ingest import run_ingest
import shutil
import os

load_dotenv(override=True)

UPLOAD_DIR = "knowledge-base/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def save_file(file):
    if file is None:
        return "❌ No file uploaded"

    file_path = os.path.join(UPLOAD_DIR, file.name)
    shutil.copy(file.name, file_path)

    # 🔥 Auto re-index after upload
    run_ingest()

    return f"✅ File uploaded & indexed: {file.name}"


def format_context(context):
    text = "### Retrieved Context\n\n"

    for doc in context:
        source = doc.metadata.get("source", "unknown")
        text += f"**Source:** {source}\n\n"
        text += doc.page_content + "\n\n---\n\n"

    return text


def chat(message, history):
    if history is None:
        history = []

    answer, context = answer_question(message, history)

    history.append((message, answer))

    return history, format_context(context)


def main():
    with gr.Blocks() as ui:

        gr.Markdown("# 🤖 RAG Knowledge Worker (Multi-file Support)")

        # 🔥 Upload section
        file_upload = gr.File(label="Upload PDF / DOCX / TXT / MD")
        upload_status = gr.Textbox(label="Upload Status")

        upload_btn = gr.Button("Upload & Index")

        upload_btn.click(
            save_file,
            inputs=file_upload,
            outputs=upload_status
        )

        chatbot = gr.Chatbot(height=400)
        context_box = gr.Markdown("Context will appear here")

        msg = gr.Textbox(
            placeholder="Ask a question from knowledge base",
            scale=7
        )

        msg.submit(
            chat,
            inputs=[msg, chatbot],
            outputs=[chatbot, context_box]
        ).then(
            lambda: "",
            None,
            msg,
            queue=False
        )

    ui.launch(share=True, inbrowser=True)


if __name__ == "__main__":
    main()