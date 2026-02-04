<!-- 图片对比组件 -->
<template>
  <div class="image-comparison">
    <div class="comparison-container">
      <div class="image-panel">
        <h3>{{ leftTitle }}</h3>
        <div class="image-wrapper">
          <img v-if="leftImage" :src="leftImage" alt="左侧图片" />
          <div v-else class="no-image">暂无图片</div>
        </div>
      </div>

      <div class="divider"></div>

      <div class="image-panel">
        <h3>{{ rightTitle }}</h3>
        <div class="image-wrapper">
          <img v-if="rightImage" :src="rightImage" alt="右侧图片" />
          <div v-else class="no-image">暂无图片</div>
        </div>
      </div>
    </div>

    <!-- 相似度显示 -->
    <div v-if="similarity !== null" class="similarity-bar">
      <span class="similarity-label">相似度:</span>
      <el-progress
        :percentage="similarity"
        :color="getSimilarityColor(similarity)"
        :stroke-width="20"
      />
      <span class="similarity-value">{{ similarity }}%</span>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  leftImage: string
  rightImage: string
  leftTitle?: string
  rightTitle?: string
  similarity?: number | null
}

withDefaults(defineProps<Props>(), {
  leftTitle: '借出照片',
  rightTitle: '归还照片',
  similarity: null
})

const getSimilarityColor = (similarity: number) => {
  if (similarity >= 90) return '#67c23a' // 绿色
  if (similarity >= 70) return '#e6a23c' // 橙色
  return '#f56c6c' // 红色
}
</script>

<style scoped>
.image-comparison {
  width: 100%;
}

.comparison-container {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.image-panel {
  flex: 1;
  background: #fff;
  border-radius: 4px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.image-panel h3 {
  margin: 0 0 10px 0;
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  text-align: center;
}

.image-wrapper {
  width: 100%;
  aspect-ratio: 1;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
}

.image-wrapper img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.no-image {
  color: #909399;
  font-size: 14px;
}

.divider {
  width: 2px;
  background: #dcdfe6;
}

.similarity-bar {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.similarity-label {
  font-size: 14px;
  color: #606266;
  white-space: nowrap;
  min-width: 60px;
}

.similarity-value {
  font-size: 18px;
  font-weight: 500;
  min-width: 50px;
}

:deep(.el-progress) {
  flex: 1;
}
</style>
