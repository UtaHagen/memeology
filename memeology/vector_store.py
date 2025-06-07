from typing import List, Dict, Any
import weaviate
from weaviate.classes.init import Auth
from weaviate.collections.classes.config import Configure, DataType, Property
from weaviate.collections.classes.config_vectorizers import Vectorizers
from memeology.configuration import settings


class WeaviateStore:
    def __init__(self):
        """初始化 Weaviate 客户端"""
        # 如果是本地 Weaviate，用 connect_to_local
        # self.client = weaviate.connect_to_local()
        # 如果是 Weaviate Cloud，用 connect_to_weaviate_cloud
        self.client = weaviate.connect_to_weaviate_cloud(
            cluster_url=settings.WEAVIATE_URL,
            auth_credentials=Auth.api_key(settings.WEAVIATE_API_KEY),
        )
        self._ensure_schema()

    def __del__(self):
        """析构函数，确保连接关闭"""
        self.close()

    def close(self):
        """关闭 Weaviate 连接"""
        if hasattr(self, "client"):
            self.client.close()

    def _ensure_schema(self):
        """确保数据库模式存在"""
        if not self.client.collections.exists("Meme"):
            # 创建集合配置
            self.client.collections.create(
                name="Meme",
                vectorizer_config={
                    "vectorizer": "multi2vec-clip",
                    "image_fields": ["image"],
                    "text_fields": [
                        "title",
                        "description",
                        "genre",
                        "emotion",
                        "character",
                    ],
                },
                properties=[
                    Property(name="title", data_type=DataType.TEXT),
                    Property(name="description", data_type=DataType.TEXT),
                    Property(name="image", data_type=DataType.BLOB),
                    Property(name="genre", data_type=DataType.TEXT),
                    Property(name="emotion", data_type=DataType.TEXT),
                    Property(name="character", data_type=DataType.TEXT),
                    Property(name="created_at", data_type=DataType.DATE),
                ],
            )

    def search(
        self, query: str, filters: Dict[str, Any] = None, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """搜索梗图"""
        # 构建查询
        query_builder = (
            self.client.query.get(
                "Meme",
                ["title", "description", "genre", "emotion", "character", "created_at"],
            )
            .with_near_text({"concepts": [query]})
            .with_limit(limit)
        )

        # 添加过滤条件
        if filters:
            if "genre" in filters and filters["genre"] != "All":
                query_builder = query_builder.with_where(
                    {
                        "path": ["genre"],
                        "operator": "Equal",
                        "valueText": filters["genre"],
                    }
                )

            if "emotion" in filters and filters["emotion"] != "All":
                query_builder = query_builder.with_where(
                    {
                        "path": ["emotion"],
                        "operator": "Equal",
                        "valueText": filters["emotion"],
                    }
                )

            if "character" in filters and filters["character"] != "All":
                query_builder = query_builder.with_where(
                    {
                        "path": ["character"],
                        "operator": "Equal",
                        "valueText": filters["character"],
                    }
                )

        # 执行查询
        result = query_builder.do()

        # 处理结果
        if "data" in result and "Get" in result["data"]:
            return result["data"]["Get"]["Meme"]
        return []

    def add_meme(
        self,
        title: str,
        description: str,
        image_path: str,
        genre: str,
        character: str,
        emotion: str,
    ) -> str:
        """添加新梗图"""
        # 读取图片
        with open(image_path, "rb") as f:
            image_data = f.read()

        # 创建对象
        data_object = {
            "title": title,
            "description": description,
            "genre": genre,
            "character": character,
            "emotion": emotion,
            "image": image_data,
        }

        # 添加到数据库
        result = self.client.data_object.create(data_object, "Meme")

        return result
