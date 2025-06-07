import os
from typing import List, Dict, Any

USE_MODAL = os.environ.get("USE_MODAL", "0") == "1"

if USE_MODAL:
    import modal
    from memeology.configuration import settings

    app = modal.App("memeology-llm")

    @app.cls(
        gpu="A100",
        image=modal.Image.debian_slim().pip_install(
            "transformers", "torch", "accelerate"
        ),
    )
    class LLMEngine:
        def __enter__(self):
            from transformers import AutoTokenizer, AutoModelForCausalLM

            self.model_name = "meta-llama/Llama-2-70b-chat-hf"
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name, token=settings.HUGGINGFACE_TOKEN
            )
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                token=settings.HUGGINGFACE_TOKEN,
                device_map="auto",
                torch_dtype="auto",
            )
            return self

        @modal.method()
        def analyze_intent(self, query: str) -> Dict[str, Any]:
            prompt = f"""分析以下查询的意图，并提取相关过滤条件：\n查询：{query}\n\n请以 JSON 格式返回，包含以下字段：\n- intent: 查询的主要意图\n- filters: 相关的过滤条件（如类型、时间范围等）\n"""
            response = self._generate(prompt)
            # TODO: 解析响应为 JSON
            return {"intent": "search", "filters": {}}

        @modal.method()
        def generate_response(
            self,
            query: str,
            results: List[Dict[str, Any]],
            history: List[Dict[str, str]],
        ) -> str:
            context = "\n".join(
                [f"{msg['role']}: {msg['content']}" for msg in history[-5:]]
            )
            results_text = "\n".join(
                [
                    f"- {result.get('title', 'Untitled')}: {result.get('description', 'No description')}"
                    for result in results[:3]
                ]
            )
            prompt = f"""基于以下对话历史和搜索结果，生成一个自然的响应：\n\n对话历史：\n{context}\n\n用户查询：{query}\n\n搜索结果：\n{results_text}\n\n请生成一个友好、自然的响应，包含对搜索结果的总结和建议。\n"""
            return self._generate(prompt)

        @modal.method()
        def generate_clarification(self, query: str) -> str:
            prompt = f"""用户查询：{query}\n\n这个查询可能需要更多信息才能准确理解。请生成一个友好的问题来请求用户澄清。\n"""
            return self._generate(prompt)

        def _generate(self, prompt: str) -> str:
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
            outputs = self.model.generate(
                **inputs, max_new_tokens=512, temperature=0.7, top_p=0.9, do_sample=True
            )
            return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
else:
    import requests

    class LLMEngine:
        def __init__(self, model="llama3"):
            self.model = model
            self.api_url = "http://localhost:11434/api/generate"

        def _generate(self, prompt: str) -> str:
            response = requests.post(
                self.api_url,
                json={"model": self.model, "prompt": prompt, "stream": False},
            )
            response.raise_for_status()
            return response.json()["response"]

        def analyze_intent(self, query: str) -> Dict[str, Any]:
            prompt = f"""分析以下查询的意图，并提取相关过滤条件：\n查询：{query}\n\n请以 JSON 格式返回，包含以下字段：\n- intent: 查询的主要意图\n- filters: 相关的过滤条件（如类型、时间范围等）\n"""
            response = self._generate(prompt)
            return {"intent": "search", "filters": {}}

        def generate_response(
            self,
            query: str,
            results: List[Dict[str, Any]],
            history: List[Dict[str, str]],
        ) -> str:
            context = "\n".join(
                [f"{msg['role']}: {msg['content']}" for msg in history[-5:]]
            )
            results_text = "\n".join(
                [
                    f"- {result.get('title', 'Untitled')}: {result.get('description', 'No description')}"
                    for result in results[:3]
                ]
            )
            prompt = f"""基于以下对话历史和搜索结果，生成一个自然的响应：\n\n对话历史：\n{context}\n\n用户查询：{query}\n\n搜索结果：\n{results_text}\n\n请生成一个友好、自然的响应，包含对搜索结果的总结和建议。\n"""
            return self._generate(prompt)

        def generate_clarification(self, query: str) -> str:
            prompt = f"""用户查询：{query}\n\n这个查询可能需要更多信息才能准确理解。请生成一个友好的问题来请求用户澄清。\n"""
            return self._generate(prompt)
