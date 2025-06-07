import os
import gradio as gr
from dotenv import load_dotenv
from typing import List, Dict, Any
import modal
from memeology.agent import MemeologyAgent
from memeology.configuration import settings

# 加载环境变量
load_dotenv()

# 初始化 Modal app
app = modal.App("memeology")

# 创建 Memeology 代理实例
agent = MemeologyAgent()


def chat_interface(message: str, history: List[List[str]]) -> str:
    """处理聊天界面的消息"""
    response = agent.process_message(message, history)
    return response


def create_interface():
    """创建 Gradio 界面"""
    with gr.Blocks(title="Memeology - AI Meme Search Assistant") as demo:
        gr.Markdown("# 🎭 Memeology - AI Meme Search Assistant")

        with gr.Row():
            with gr.Column(scale=4):
                chatbot = gr.Chatbot(
                    height=600,
                    show_copy_button=True,
                    show_share_button=True,
                )
                with gr.Row():
                    msg = gr.Textbox(
                        placeholder="描述你想要的梗图...",
                        show_label=False,
                        container=False,
                    )
                    submit = gr.Button("发送", variant="primary")

            with gr.Column(scale=1):
                gr.Markdown("### 筛选条件")
                genre = gr.Dropdown(
                    choices=["全部", "搞笑", "动漫", "游戏", "电影", "其他"],
                    value="全部",
                    label="类型",
                )
                time_range = gr.Dropdown(
                    choices=["全部时间", "最近一周", "最近一月", "最近一年"],
                    value="全部时间",
                    label="时间范围",
                )

        submit.click(
            chat_interface,
            inputs=[msg, chatbot],
            outputs=[chatbot],
        ).then(lambda: "", None, [msg], queue=False)

        msg.submit(
            chat_interface,
            inputs=[msg, chatbot],
            outputs=[chatbot],
        ).then(lambda: "", None, [msg], queue=False)

    return demo


if __name__ == "__main__":
    demo = create_interface()
    demo.launch(share=True)
    # 关闭 Weaviate 连接
    agent.vector_store.close()
