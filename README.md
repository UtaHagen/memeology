# 🎭 Memeology

Memeology 是一个智能梗图搜索助手，它使用先进的 AI 技术来帮助用户找到最相关的梗图。

## ✨ 特性

- 🤖 基于 LLaMA 3 的智能对话
- 🔍 多模态搜索（文本 + 图像）
- 🎯 精确的过滤和分类
- 💬 自然语言交互
- 🎨 美观的 Gradio 界面

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Modal 账号
- Weaviate Cloud 账号
- Hugging Face 账号（用于访问 LLaMA 模型）

### 安装

1. 克隆仓库：
```bash
git clone https://github.com/yourusername/memeology.git
cd memeology
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置环境变量：
创建 `.env` 文件并添加以下配置：
```env
WEAVIATE_URL=your_weaviate_url
WEAVIATE_API_KEY=your_weaviate_api_key
HUGGINGFACE_TOKEN=your_huggingface_token
MODAL_TOKEN_ID=your_modal_token_id
MODAL_TOKEN_SECRET=your_modal_token_secret
```

### 运行

1. 启动应用：
```bash
python app.py
```

2. 上传梗图：
```bash
python scripts/upload_memes.py /path/to/memes "搞笑" --title-file titles.txt --description-file descriptions.txt
```

## 🏗️ 项目结构

```
memeology/
├── app.py              # 主应用入口
├── requirements.txt    # 项目依赖
├── memeology/         # 核心模块
│   ├── agent.py       # AI 代理实现
│   ├── llm.py         # LLM 引擎
│   ├── vector_store.py # Weaviate 存储
│   └── config.py      # 配置管理
└── scripts/           # 工具脚本
    └── upload_memes.py # 梗图上传工具
```

