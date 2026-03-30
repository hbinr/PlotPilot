<template>
  <div class="stats-top-bar">
    <div
      v-for="stat in stats"
      :key="stat.key"
      class="stat-item"
      role="group"
      :aria-label="stat.label"
    >
      <n-tooltip :show-arrow="false">
        <template #trigger>
          <div class="stat-content">
            <span class="stat-label">{{ stat.label }}</span>
            <span class="stat-value">{{ stat.value }}</span>
          </div>
        </template>
        <span>{{ stat.tooltip }}</span>
      </n-tooltip>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { NTooltip } from 'naive-ui'
import { useStatsStore } from '@/stores/statsStore'

const props = defineProps<{
  slug: string
}>()

const statsStore = useStatsStore()

const bookStats = computed(() => statsStore.getBookStats.value(props.slug))

const stats = computed(() => {
  if (!bookStats.value) return []

  const s = bookStats.value
  return [
    {
      key: 'words',
      label: '总字数',
      value: s.total_words.toLocaleString(),
      tooltip: `当前书籍共 ${s.total_words.toLocaleString()} 字`
    },
    {
      key: 'chapters',
      label: '完成章节',
      value: `${s.completed_chapters}/${s.total_chapters}`,
      tooltip: `已完成 ${s.completed_chapters} 章，共 ${s.total_chapters} 章`
    },
    {
      key: 'completion',
      label: '完成率',
      value: `${s.completion_rate.toFixed(1)}%`,
      tooltip: `项目完成度：${s.completion_rate.toFixed(1)}%`
    },
    {
      key: 'avg',
      label: '平均字数',
      value: s.avg_chapter_words.toLocaleString(),
      tooltip: `每章平均 ${s.avg_chapter_words.toLocaleString()} 字`
    },
    {
      key: 'updated',
      label: '最后更新',
      value: formatDate(s.last_updated),
      tooltip: `最后更新时间：${s.last_updated}`
    }
  ]
})

function formatDate(dateStr: string): string {
  try {
    const date = new Date(dateStr)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

    if (diffDays === 0) {
      return '今天'
    } else if (diffDays === 1) {
      return '昨天'
    } else if (diffDays < 7) {
      return `${diffDays}天前`
    } else {
      return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
    }
  } catch {
    return dateStr
  }
}

onMounted(async () => {
  await statsStore.loadBookStats(props.slug)
})
</script>

<style scoped>
.stats-top-bar {
  height: 80px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: space-around;
  padding: 0 24px;
  color: white;
}

.stat-item {
  flex: 1;
  text-align: center;
  cursor: help;
}

.stat-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-label {
  font-size: 12px;
  opacity: 0.9;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
}

.stat-item:hover .stat-value {
  transform: scale(1.05);
  transition: transform 0.2s;
}

/* Accessibility: Focus styles */
.stat-item:focus-within {
  outline: 2px solid rgba(255, 255, 255, 0.5);
  outline-offset: 4px;
  border-radius: 4px;
}

/* Responsive design */
@media (max-width: 768px) {
  .stats-top-bar {
    height: auto;
    flex-wrap: wrap;
    padding: 16px;
  }

  .stat-item {
    flex: 0 0 50%;
    margin-bottom: 12px;
  }

  .stat-value {
    font-size: 20px;
  }
}

@media (max-width: 480px) {
  .stat-item {
    flex: 0 0 100%;
  }
}
</style>
