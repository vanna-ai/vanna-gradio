import gradio as gr

from demo.calls import (
    get_followup_questions,
    get_plotly,
    get_records,
    get_sql,
    get_table,
)


def add_prompt_to_history(history, text):
    history += [(text, None)]
    return history, gr.Textbox(value="", interactive=False)


def event_handler(history):
    prompt = history[-1][0]
    # sql = "Select * FROM Genre"
    sql = get_sql(prompt)
    records = get_records(sql)
    table_figure = get_table(records)
    figure = get_plotly(prompt=prompt, sql=sql, df=records)
    follow_up_questions = get_followup_questions(prompt=prompt, records=records)

    history.append([None, sql])
    history.append([None, table_figure])
    history.append([None, figure])
    history.append([None, follow_up_questions])

    return history
