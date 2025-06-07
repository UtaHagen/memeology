import os
import argparse
from pathlib import Path
from memeology.vector_store import WeaviateStore

from memeology.configuration import settings


def upload_memes(
    meme_dir: str, genre: str, title_file: str = None, description_file: str = None
):
    """上传梗图到 Weaviate"""
    # 初始化 Weaviate 客户端
    store = WeaviateStore()

    # 获取所有图片文件
    meme_path = Path(meme_dir)
    image_files = list(meme_path.glob("*.{jpg,jpeg,png,gif}"))

    # 读取标题和描述（如果提供）
    titles = {}
    descriptions = {}
    if title_file:
        with open(title_file, "r", encoding="utf-8") as f:
            for line in f:
                filename, title = line.strip().split("|")
                titles[filename] = title

    if description_file:
        with open(description_file, "r", encoding="utf-8") as f:
            for line in f:
                filename, desc = line.strip().split("|")
                descriptions[filename] = desc

    # 上传每个梗图
    for image_file in image_files:
        filename = image_file.name
        title = titles.get(filename, filename)
        description = descriptions.get(filename, "")

        print(f"上传: {filename}")
        try:
            store.add_meme(
                title=title,
                description=description,
                image_path=str(image_file),
                genre=genre,
            )
            print(f"成功: {filename}")
        except Exception as e:
            print(f"失败: {filename} - {str(e)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="上传梗图到 Weaviate")
    parser.add_argument("meme_dir", help="梗图目录路径")
    parser.add_argument("genre", help="梗图类型")
    parser.add_argument("--title-file", help="标题文件路径（每行格式：文件名|标题）")
    parser.add_argument(
        "--description-file", help="描述文件路径（每行格式：文件名|描述）"
    )

    args = parser.parse_args()
    upload_memes(args.meme_dir, args.genre, args.title_file, args.description_file)
