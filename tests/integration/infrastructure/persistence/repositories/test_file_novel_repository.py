"""FileNovelRepository 集成测试"""
import pytest
import tempfile
import shutil
from pathlib import Path
from domain.novel.entities.novel import Novel, NovelStage
from domain.novel.entities.chapter import Chapter
from domain.novel.value_objects.novel_id import NovelId
from domain.novel.value_objects.chapter_id import ChapterId
from domain.novel.value_objects.word_count import WordCount
from domain.novel.value_objects.chapter_content import ChapterContent
from infrastructure.persistence.storage.file_storage import FileStorage
from infrastructure.persistence.repositories.file_novel_repository import FileNovelRepository


class TestFileNovelRepository:
    """FileNovelRepository 集成测试"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp_path = tempfile.mkdtemp()
        yield Path(temp_path)
        shutil.rmtree(temp_path)

    @pytest.fixture
    def storage(self, temp_dir):
        """创建 FileStorage 实例"""
        return FileStorage(temp_dir)

    @pytest.fixture
    def repository(self, storage):
        """创建 FileNovelRepository 实例"""
        return FileNovelRepository(storage)

    def test_save_and_get(self, repository):
        """测试保存和获取小说"""
        novel = Novel(
            id=NovelId("test-novel"),
            title="测试小说",
            author="测试作者",
            target_chapters=10
        )

        repository.save(novel)
        retrieved = repository.get_by_id(NovelId("test-novel"))

        assert retrieved is not None
        assert retrieved.novel_id.value == "test-novel"
        assert retrieved.title == "测试小说"
        assert retrieved.author == "测试作者"

    def test_get_nonexistent(self, repository):
        """测试获取不存在的小说"""
        result = repository.get_by_id(NovelId("nonexistent"))
        assert result is None

    def test_list_all(self, repository):
        """测试列出所有小说"""
        novel1 = Novel(
            id=NovelId("novel-1"),
            title="小说1",
            author="作者1",
            target_chapters=10
        )
        novel2 = Novel(
            id=NovelId("novel-2"),
            title="小说2",
            author="作者2",
            target_chapters=20
        )

        repository.save(novel1)
        repository.save(novel2)

        novels = repository.list_all()
        assert len(novels) == 2
        novel_ids = [n.novel_id.value for n in novels]
        assert "novel-1" in novel_ids
        assert "novel-2" in novel_ids

    def test_delete(self, repository):
        """测试删除小说"""
        novel = Novel(
            id=NovelId("test-novel"),
            title="测试小说",
            author="测试作者",
            target_chapters=10
        )

        repository.save(novel)
        assert repository.exists(NovelId("test-novel"))

        repository.delete(NovelId("test-novel"))
        assert not repository.exists(NovelId("test-novel"))

    def test_exists(self, repository):
        """测试检查小说是否存在"""
        novel_id = NovelId("test-novel")

        assert not repository.exists(novel_id)

        novel = Novel(
            id=novel_id,
            title="测试小说",
            author="测试作者",
            target_chapters=10
        )
        repository.save(novel)

        assert repository.exists(novel_id)

    def test_save_with_chapters(self, repository):
        """测试保存包含章节的小说"""
        novel = Novel(
            id=NovelId("test-novel"),
            title="测试小说",
            author="测试作者",
            target_chapters=10
        )

        chapter = Chapter(
            id="chapter-1",
            novel_id=NovelId("test-novel"),
            number=1,
            title="第一章",
            content="章节内容"
        )
        novel.add_chapter(chapter)

        repository.save(novel)
        retrieved = repository.get_by_id(NovelId("test-novel"))

        assert len(retrieved.chapters) == 1
        assert retrieved.chapters[0].title == "第一章"
