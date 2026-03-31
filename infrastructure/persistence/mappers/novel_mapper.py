"""Novel 数据映射器"""
from typing import Dict, Any
from domain.novel.entities.novel import Novel, NovelStage
from domain.novel.entities.chapter import Chapter
from domain.novel.value_objects.novel_id import NovelId
from domain.novel.value_objects.chapter_id import ChapterId
from domain.novel.value_objects.word_count import WordCount
from domain.novel.value_objects.chapter_content import ChapterContent


class NovelMapper:
    """Novel 实体与字典数据之间的映射器

    负责将 Novel 领域对象转换为可持久化的字典格式，
    以及从字典数据重建 Novel 对象。
    """

    @staticmethod
    def to_dict(novel: Novel) -> Dict[str, Any]:
        """将 Novel 实体转换为字典

        Args:
            novel: Novel 实体

        Returns:
            字典表示
        """
        return {
            "id": novel.novel_id.value,
            "title": novel.title,
            "author": novel.author,
            "target_chapters": novel.target_chapters,
            "stage": novel.stage.value,
            "chapters": [
                {
                    "id": chapter.id,
                    "novel_id": chapter.novel_id.value,
                    "number": chapter.number,
                    "title": chapter.title,
                    "content": chapter.content,
                    "word_count": chapter.word_count.value
                }
                for chapter in novel.chapters
            ]
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> Novel:
        """从字典创建 Novel 实体

        Args:
            data: 字典数据

        Returns:
            Novel 实体
        """
        # 创建 Novel 实体
        novel = Novel(
            id=NovelId(data["id"]),
            title=data["title"],
            author=data["author"],
            target_chapters=data["target_chapters"],
            stage=NovelStage(data["stage"])
        )

        # 添加章节
        for chapter_data in data.get("chapters", []):
            chapter = Chapter(
                id=chapter_data["id"],
                novel_id=NovelId(chapter_data["novel_id"]),
                number=chapter_data["number"],
                title=chapter_data["title"],
                content=chapter_data["content"]
            )
            novel.add_chapter(chapter)

        return novel
