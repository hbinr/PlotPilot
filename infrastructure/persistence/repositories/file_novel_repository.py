"""基于文件的 Novel 仓储实现"""
from typing import Optional, List
from domain.novel.entities.novel import Novel
from domain.novel.value_objects.novel_id import NovelId
from domain.novel.repositories.novel_repository import NovelRepository
from infrastructure.persistence.storage.backend import StorageBackend
from infrastructure.persistence.mappers.novel_mapper import NovelMapper


class FileNovelRepository(NovelRepository):
    """基于文件系统的 Novel 仓储实现

    使用 JSON 文件存储小说数据。
    """

    def __init__(self, storage: StorageBackend):
        """初始化仓储

        Args:
            storage: 存储后端
        """
        self.storage = storage

    def _get_path(self, novel_id: NovelId) -> str:
        """获取小说文件路径

        Args:
            novel_id: 小说 ID

        Returns:
            文件路径
        """
        return f"novels/{novel_id.value}.json"

    def save(self, novel: Novel) -> None:
        """保存小说"""
        path = self._get_path(novel.novel_id)
        data = NovelMapper.to_dict(novel)
        self.storage.write_json(path, data)

    def get_by_id(self, novel_id: NovelId) -> Optional[Novel]:
        """根据 ID 获取小说"""
        path = self._get_path(novel_id)

        if not self.storage.exists(path):
            return None

        data = self.storage.read_json(path)
        return NovelMapper.from_dict(data)

    def list_all(self) -> List[Novel]:
        """列出所有小说"""
        files = self.storage.list_files("novels/*.json")
        novels = []

        for file_path in files:
            data = self.storage.read_json(file_path)
            novel = NovelMapper.from_dict(data)
            novels.append(novel)

        return novels

    def delete(self, novel_id: NovelId) -> None:
        """删除小说"""
        path = self._get_path(novel_id)
        self.storage.delete(path)

    def exists(self, novel_id: NovelId) -> bool:
        """检查小说是否存在"""
        path = self._get_path(novel_id)
        return self.storage.exists(path)
