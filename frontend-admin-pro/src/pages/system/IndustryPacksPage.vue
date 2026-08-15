<template>
  <AdminPage title="行业包管理" subtitle="选择行业模板，自动初始化工序、质检模板、缺陷代码等配置">
    <div class="industry-packs-page">
      <!-- 当前已激活行业 -->
      <div v-if="currentIndustries.length > 0" class="current-industries">
        <div class="current-badge">
          <el-icon :size="20"><Check /></el-icon>
          <span>已激活行业：</span>
          <el-tag
            v-for="ind in currentIndustries"
            :key="ind.code"
            type="success"
            size="small"
            class="current-tag"
          >
            {{ ind.name }}
          </el-tag>
        </div>
      </div>

      <!-- 加载中 -->
      <div v-if="loading" class="loading-wrap">
        <el-skeleton :rows="3" animated />
      </div>

      <!-- 行业包卡片 -->
      <div v-else class="packs-grid">
        <div
          v-for="pack in industries"
          :key="pack.code"
          class="pack-card"
          :class="{ active: pack.is_active }"
        >
          <div class="pack-header">
            <div class="pack-icon" :style="{ background: getIconBg(pack.code) }">
              <el-icon :size="28" color="#fff"><component :is="getIcon(pack.code)" /></el-icon>
            </div>
            <div class="pack-title">
              <h3>{{ pack.name }}</h3>
              <span class="pack-name-en">{{ pack.name_en }}</span>
            </div>
            <el-tag v-if="pack.is_active" type="success" size="small" class="pack-active-tag">已激活</el-tag>
          </div>

          <p class="pack-desc">{{ pack.description }}</p>

          <div class="pack-features">
            <el-tag
              v-for="(feat, idx) in pack.features.slice(0, 6)"
              :key="idx"
              size="small"
              type="info"
              class="feature-tag"
            >
              {{ feat }}
            </el-tag>
            <el-tag v-if="pack.features.length > 6" size="small" type="info" class="feature-tag">
              +{{ pack.features.length - 6 }}
            </el-tag>
          </div>

          <div class="pack-footer">
            <span class="pack-version">v{{ pack.version }}</span>
            <div class="pack-actions">
              <el-button
                v-if="pack.is_active"
                type="warning"
                size="small"
                :loading="reseeding === pack.code"
                @click="handleReseed(pack)"
              >
                重新初始化
              </el-button>
              <el-button
                v-if="pack.is_active"
                type="danger"
                size="small"
                plain
                @click="handleDeactivate(pack)"
              >
                取消激活
              </el-button>
              <el-button
                v-else
                type="primary"
                size="small"
                :loading="activating === pack.code"
                @click="handleActivate(pack)"
              >
                激活
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AdminPage>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Tools, Box, Cpu, Scissor, Apple, Van, Check, Setting
} from '@element-plus/icons-vue'
import { productionApi } from '@/api/production'

interface IndustryInfo {
  code: string
  name: string
  name_en: string
  description: string
  version: string
  icon: string
  features: string[]
  is_active?: boolean
}

const industries = ref<IndustryInfo[]>([])
const currentCodes = ref<string[]>([])
const loading = ref(false)
const activating = ref('')
const reseeding = ref('')

const currentIndustries = computed(() => {
  return industries.value.filter(p => p.is_active)
})

// 图标映射
const iconMap: Record<string, any> = {
  machining: Tools,
  injection_molding: Box,
  electronics: Cpu,
  garment: Scissor,
  food: Apple,
  auto_parts: Van,
}

const iconBgMap: Record<string, string> = {
  machining: '#409EFF',
  injection_molding: '#67C23A',
  electronics: '#E6A23C',
  garment: '#F56C6C',
  food: '#FF6B35',
  auto_parts: '#909399',
}

function getIcon(code: string) {
  return iconMap[code] || Setting
}

function getIconBg(code: string) {
  return iconBgMap[code] || '#409EFF'
}

async function loadData() {
  loading.value = true
  try {
    const [listRes, curRes] = await Promise.all([
      productionApi.listIndustries(),
      productionApi.getCurrentIndustry(),
    ])
    industries.value = listRes.items || []
    currentCodes.value = Array.isArray(listRes.current) ? listRes.current : []
  } catch (e: any) {
    console.error('加载行业包失败:', e)
  } finally {
    loading.value = false
  }
}

async function handleActivate(pack: IndustryInfo) {
  try {
    await ElMessageBox.confirm(
      `确定激活「${pack.name}」行业包？\n将自动初始化该行业的工序模板、质检模板、缺陷代码和字典数据。`,
      '激活行业包',
      { confirmButtonText: '确定激活', cancelButtonText: '取消', type: 'warning' }
    )
    activating.value = pack.code
    await productionApi.activateIndustry({ industry_code: pack.code })
    ElMessage.success(`「${pack.name}」行业包激活成功`)
    await loadData()
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error(e?.message || '激活失败')
    }
  } finally {
    activating.value = ''
  }
}

async function handleDeactivate(pack: IndustryInfo) {
  try {
    await ElMessageBox.confirm(
      `确定取消激活「${pack.name}」行业包？\n已有数据不会删除，仅移除行业标识。`,
      '取消激活',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
    await productionApi.deactivateIndustry({ industry_code: pack.code })
    ElMessage.success(`「${pack.name}」行业包已取消激活`)
    await loadData()
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error(e?.message || '取消激活失败')
    }
  }
}

async function handleReseed(pack: IndustryInfo) {
  try {
    await ElMessageBox.confirm(
      '确定重新初始化当前行业的种子数据？\n已有数据不会重复插入（幂等操作）。',
      '重新初始化',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
    reseeding.value = pack.code
    await productionApi.reseedIndustry({ industry_code: pack.code })
    ElMessage.success('种子数据重新初始化成功')
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error(e?.message || '初始化失败')
    }
  } finally {
    reseeding.value = ''
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.industry-packs-page {
  padding: 0;
}

.current-industries {
  margin-bottom: 20px;
}

.current-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: #f0f9eb;
  border: 1px solid #e1f3d8;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 500;
  color: #67c23a;
  flex-wrap: wrap;
}

.current-tag {
  margin-left: 4px;
}

.loading-wrap {
  padding: 40px 0;
}

.packs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 20px;
}

.pack-card {
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  padding: 20px;
  transition: all 0.3s;
  display: flex;
  flex-direction: column;
}

.pack-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.pack-card.active {
  border-color: #67c23a;
  box-shadow: 0 0 0 1px #67c23a;
}

.pack-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.pack-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.pack-title {
  flex: 1;
}

.pack-title h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.pack-name-en {
  font-size: 12px;
  color: #909399;
}

.pack-active-tag {
  flex-shrink: 0;
}

.pack-desc {
  font-size: 13px;
  color: #606266;
  line-height: 1.6;
  margin: 0 0 12px 0;
  min-height: 42px;
}

.pack-features {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 16px;
  flex: 1;
}

.feature-tag {
  font-size: 11px;
}

.pack-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-top: 1px solid #f0f0f0;
  padding-top: 12px;
}

.pack-version {
  font-size: 12px;
  color: #c0c4cc;
}

.pack-actions {
  display: flex;
  gap: 8px;
}
</style>