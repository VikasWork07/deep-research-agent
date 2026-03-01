import gradio as gr
from dotenv import load_dotenv
from research_manager import ResearchManager

load_dotenv(override=True)

manager = ResearchManager()

event_type = ['status', 'trace', 'report']

async def run(query:str, state):
    """
    Handles both:
    1) Initial research request
    2) Clarification responses
    """

    # If we were waiting for clarification, append user answers to original query
    if state.get("awaiting_clarification"):
        #full_query = state["original_query"] + "\n\nUser Clarifications:\n" + query
        state["clarifications"].append(query)
        state["awaiting_clarification"] = False
    else:
        #full_query = query
        state["original_query"] = query
        state["clarifications"] = []
    
    full_query = state["original_query"]

    if state["clarifications"]:
        full_query += "\n\nUser Clarifications:\n"
        full_query += "\n".join(state["clarifications"])
        
    report_content = ""

    async for output_chunk in manager.run(full_query):
        
         # Detect clarification request
        if isinstance(output_chunk, dict) and output_chunk["type"] == "clarification":
            state["awaiting_clarification"] = True
            questions = "\n".join(
                    [f"- {q}" for q in output_chunk["content"]]
                )
            report_content += "Query needs clarification...Please answer following questions to clarify your query:\n" + questions + "\n"
            yield report_content, state, gr.update(value="", placeholder="Provide clarification here...")
            return
        elif isinstance(output_chunk, dict) and output_chunk["type"] in event_type:
            report_content += f"{output_chunk['content']}\n" if isinstance(output_chunk, dict) else f"{output_chunk}\n"
        yield report_content, state, gr.update()
        

with gr.Blocks(theme=gr.themes.Default(primary_hue="sky")) as ui:
    gr.Markdown("# Your Deep Research Assistant")

    state = gr.State({
        "awaiting_clarification": False,
        "original_query": None,
        "clarifications": []
    })

    query_textbox = gr.Textbox(
        label="What topic would you like to research?",
        placeholder="Enter your research query here...")
    
    run_button = gr.Button("Run", variant="primary")
    report = gr.Markdown(label="Report")
    
    run_button.click(fn=run, inputs=[query_textbox, state], outputs=[report, state, query_textbox])
    query_textbox.submit(fn=run, inputs=[query_textbox, state], outputs=[report, state, query_textbox])

ui.launch(inbrowser=True)