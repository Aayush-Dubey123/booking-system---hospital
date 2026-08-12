"""
chat_cmd.py — Interactive chatbot REPL using /v1/chat (non-streaming) 
or /v1/chat/stream (SSE streaming with --stream flag).

Requires patient JWT. Identity from JWT — no user_id prompt.
"""
from __future__ import annotations

import uuid
from typing import Optional

import typer

import cli.auth as token_store
from cli.services import api_client as client
import cli.ui as ui

chat_app = typer.Typer(
    name="chat",
    help="Chat with the CityCare AI assistant (appointments & prescriptions).",
    no_args_is_help=False,
)


@chat_app.callback(invoke_without_command=True)
def chat(
    ctx: typer.Context,
    stream: bool = typer.Option(
        False,
        "--stream",
        "-s",
        help="Use SSE streaming for a word-by-word response.",
    ),
    conversation_id: Optional[str] = typer.Option(
        None,
        "--id",
        help="Resume an existing conversation by ID (auto-generated if omitted).",
    ),
):
    """
    Start an interactive chat session with the CityCare Patient Assistant.

    The assistant can:
      • Check available appointment slots
      • Book appointments on your behalf
      • Show your existing appointments
      • Answer questions about your prescriptions (RAG/AI powered)

    Type [bold]exit[/bold] or press Ctrl+C to quit.
    """
    if ctx.invoked_subcommand:
        return

    auth = token_store.require_auth()

    # Generate a fresh conversation ID for this session unless user specifies one
    conv_id = conversation_id or f"cli-{uuid.uuid4().hex[:12]}"

    ui.console.print(
        "\n[bold cyan]💬  CityCare Patient Assistant[/bold cyan]\n"
        f"[dim]Conversation ID: {conv_id}[/dim]\n"
        "[dim]Type [bold]exit[/bold] or press Ctrl+C to quit.[/dim]\n"
    )

    if stream:
        ui.info("Streaming mode active — responses will appear word-by-word.\n")

    try:
        while True:
            # Patient input
            try:
                user_input = ui.prompt("You")
            except (KeyboardInterrupt, EOFError):
                ui.console.print()
                ui.info("Chat session ended.")
                break

            if not user_input or user_input.strip().lower() in {"exit", "quit", "bye"}:
                ui.info("Chat session ended. Goodbye!")
                break

            payload = {
                "conversation_id": conv_id,
                "user_input": user_input.strip(),
            }

            if stream:
                # SSE streaming: print word-by-word
                ui.console.print("\n[bold cyan]🤖 Assistant:[/bold cyan] ", end="")
                client.stream_post("/v1/chat/stream", payload, auth=auth)
                ui.console.print()
            else:
                # Non-streaming: single request, show spinner, then display reply
                with ui.spinner("Thinking…"):
                    result = client.post("/v1/chat", payload, auth=auth)
                response_text = result.get("response", "")
                if response_text:
                    from rich.panel import Panel
                    from rich.markdown import Markdown
                    ui.console.print(
                        Panel(
                            Markdown(response_text),
                            title="[bold cyan]🤖 Assistant[/bold cyan]",
                            border_style="cyan",
                            padding=(1, 2),
                        )
                    )
                else:
                    ui.warning("No response from assistant.")

    except KeyboardInterrupt:
        ui.console.print()
        ui.info("Chat session ended.")
