/**
 * Frontend API Type Definitions — 统一出口
 *
 * 各领域类型已拆分到独立模块：
 *   - common.ts   通用响应、Job、日志
 *   - novel.ts    小说 / Book
 *   - chapter.ts  章节
 *   - bible.ts    世界观设定
 *   - cast.ts     角色关系
 *   - knowledge.ts 知识图谱
 *   - stats.ts    统计
 *
 * 此文件保持向后兼容，统一 re-export 所有类型。
 * 新代码请直接从对应子模块导入（tree-shaking 更友好）。
 */

export * from './common'
export * from './novel'
export * from './chapter'
export * from './bible'
export * from './cast'
export * from './knowledge'
export * from './stats'

// ── 组合响应类型（跨模块） ─────────────────────────────────────

import type { BookDesk } from './novel'
import type { ChapterListItem } from './chapter'

export interface BookDeskResponse {
  book: BookDesk | null
  chapters: ChapterListItem[]
}
