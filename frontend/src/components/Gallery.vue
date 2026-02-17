<template>
  <div class="gallery-layout">
    <aside class="sidebar">
      <div class="brand">SD Gallery</div>
      <div class="sidebar-controls">
        <button @click="goRoot">根目录</button>
        <button @click="toggleView">视图: {{ viewMode === 'grid' ? '网格' : '列表' }}</button>
      </div>

      <div class="folder-list">
        <div v-if="treeNodes.length === 0" class="empty-folders">没有可用的输出文件夹</div>
        <div v-for="(node, idx) in treeNodes" :key="node.fullPath + '_' + idx" class="folder-item" :class="{active: isActive(node)}" :style="{ paddingLeft: (12 + node.depth*12) + 'px' }">
          <div class="fi-left" @click.stop="node.type === 'dir' && toggleNode(node, idx)">
            <span v-if="node.type === 'dir'">{{ node.expanded ? '▾' : '▸' }}</span>
            <span v-else>🖼️</span>
          </div>
          <div class="fi-name" @click.stop="onNodeClick(node, idx)">
            {{ node.name }}
          </div>
        </div>
      </div>
    </aside>

    <main class="main">
      <div v-if="!selectedFolder" class="placeholder">
        <div class="placeholder-box">
          <div class="emoji">(๑>◡<๑)</div>
          <h2>请选择你要查看的一个输出文件哦</h2>
          <p>在左侧选择文件夹以查看图片预览 ✧</p>
        </div>
      </div>

      <div v-else class="content">
            <div class="content-header">
              <div class="crumbs">
                <!-- path display removed per user request -->
              </div>
              <div class="content-actions">
                <template v-if="!selectionMode && images.length > 0">
                  <button class="btn-primary" @click="selectionMode = true">批量选择</button>
                </template>
                <template v-else-if="selectionMode">
                  <button class="btn-primary" @click="downloadSelected" :disabled="selectedImages.length===0">下载所选 ({{ selectedImages.length }})</button>
                  <button class="btn-outline" @click="clearSelection">取消选择</button>
                </template>
              </div>
            </div>

            <div class="images" :class="viewMode">
              <div v-for="img in images" :key="img" class="image-card">
                <label v-if="selectionMode" class="select-checkbox">
                  <input type="checkbox" :value="img" v-model="selectedImages" />
                </label>
                <LazyImage :src="imageUrl(img)" :alt="img" @click="openImage(img)" />
                <div class="meta">
                  <div class="name">{{ img }}</div>
                  <div class="actions">
                    <a v-if="!selectionMode" :href="downloadUrl(img)" target="_blank" rel="noopener" class="btn-outline action-btn">下载</a>
                    <button v-if="!selectionMode" class="btn-primary action-btn" @click="openImage(img)">预览</button>
                  </div>
                </div>
              </div>
            </div>
      </div>

      <ImageViewer v-if="viewerImage" :src="viewerImageSrc" @close="viewerImage = null" />
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import ImageViewer from './ImageViewer.vue'
import LazyImage from './LazyImage.vue'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

const currentPath = ref('')
const folders = ref([])
const images = ref([])
const viewMode = ref('grid')
const viewerImage = ref(null)
const selectedFolder = ref(null) // stores full relative path

// tree structure for sidebar (flat list with depth)
const treeNodes = ref([])

const selectedName = computed(()=> selectedFolder.value ? selectedFolder.value.split('/').filter(Boolean).pop() : '')

const parts = computed(() => currentPath.value ? currentPath.value.split('/').filter(Boolean) : [])

function imageUrl(name){
  const rel = currentPath.value ? `${currentPath.value}/${name}` : name
  return `${API_BASE}/api/image?path=${encodeURIComponent(rel)}`
}

function downloadUrl(name){
  const rel = currentPath.value ? `${currentPath.value}/${name}` : name
  return `${API_BASE}/api/image?path=${encodeURIComponent(rel)}&download=true`
}

const viewerImageSrc = computed(()=> {
  if(!viewerImage.value) return ''
  return `${API_BASE}/api/image?path=${encodeURIComponent(viewerImage.value)}`
})

const downloadAllUrl = computed(()=> `${API_BASE}/api/folders?path=${encodeURIComponent(currentPath.value)}`)

const selectionMode = ref(false)
const selectedImages = ref([])

function clearSelection(){ selectedImages.value = []; selectionMode.value = false }

async function downloadSelected(){
  if(selectedImages.value.length === 0) return
  const params = new URLSearchParams()
  params.append('path', currentPath.value || '')
  selectedImages.value.forEach(f => params.append('files', f))
  const url = `${API_BASE}/api/zip?` + params.toString()
  const res = await fetch(url)
  if(!res.ok){ alert('下载失败') ; return }
  const blob = await res.blob()
  const a = document.createElement('a')
  const urlBlob = URL.createObjectURL(blob)
  a.href = urlBlob
  a.download = (selectedFolder.value || 'images') + '.zip'
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(urlBlob)
  clearSelection()
}

async function load(path=''){
  const url = `${API_BASE}/api/folders?path=${encodeURIComponent(path)}`
  const res = await fetch(url)
  if(!res.ok){
    folders.value = []
    images.value = []
    return
  }
  const data = await res.json()
  folders.value = data.folders
  images.value = data.images
  currentPath.value = data.path
}

async function fetchFolderData(path = ''){
  const url = `${API_BASE}/api/folders?path=${encodeURIComponent(path)}`
  const res = await fetch(url)
  if(!res.ok) return { folders: [], images: [], path: path }
  return await res.json()
}

function selectFolder(fullPath){
  selectedFolder.value = fullPath
  selectedImages.value = []
  selectionMode.value = false
  // load images for this folder into main view
  load(fullPath)
}

function selectFile(node){
  // node is file node
  const rel = node.fullPath
  // ensure currentPath corresponds to node's parent
  const parts = rel.split('/').filter(Boolean)
  const parent = parts.slice(0, -1).join('/')
  currentPath.value = parent
  selectedFolder.value = parent || null
  openImage(parts.pop())
}

async function onNodeClick(node, idx){
  if(node.type === 'dir'){
    await toggleNode(node, idx)
    selectFolder(node.fullPath)
  } else {
    selectFile(node)
  }
}

function isActive(node){
  if(!selectedFolder.value) return false
  return node.type === 'dir' ? node.fullPath === selectedFolder.value : (selectedFolder.value === (node.fullPath.split('/').slice(0,-1).join('/')))
}

function openImage(name){
  const rel = currentPath.value ? `${currentPath.value}/${name}` : name
  viewerImage.value = rel
}

function goRoot(){ selectedFolder.value = null; load('') }
function toggleView(){ viewMode.value = viewMode.value === 'grid' ? 'list' : 'grid' }

async function toggleNode(node, idx){
  if(node.expanded){
    // collapse: remove descendants
    collapseChildren(node, idx)
    node.expanded = false
    node.loaded = false
    // 如果折叠的节点包含当前选中的文件夹（包括子目录），则清除选中并恢复占位提示视图
    if(selectedFolder.value && (selectedFolder.value === node.fullPath || selectedFolder.value.startsWith(node.fullPath + '/'))){
      console.log('[gallery] collapsing parent of selected node, clearing selection and preview:', node.fullPath)
      selectedFolder.value = null
      images.value = []
      currentPath.value = ''
      // 使用空字符串确保 v-if 判定为 falsy，避免某些情况下仍然显示预览
      viewerImage.value = ''
    }
    return
  }
  // expand
  if(node.loaded){
    node.expanded = true
    // 通过箭头展开也要把该文件夹设为选中并加载内容
    console.log('[gallery] expanding folder via arrow:', node.fullPath)
    selectedFolder.value = node.fullPath
    selectionMode.value = false
    await load(node.fullPath)
    return
  }
  const data = await fetchFolderData(node.fullPath)
  const items = []
  // add folders first
  for(const d of data.folders){
    items.push({ name: d, fullPath: node.fullPath ? `${node.fullPath}/${d}` : d, type: 'dir', depth: node.depth + 1, expanded:false, loaded:false })
  }
  // then files
  for(const f of data.images){
    items.push({ name: f, fullPath: node.fullPath ? `${node.fullPath}/${f}` : f, type: 'file', depth: node.depth + 1 })
  }
  // insert into treeNodes after idx
  treeNodes.value.splice(idx+1, 0, ...items)
  node.expanded = true
  node.loaded = true
  // 将通过展开操作选中该文件夹并加载其内容
  console.log('[gallery] expanded folder and loaded:', node.fullPath)
  selectedFolder.value = node.fullPath
  selectionMode.value = false
  await load(node.fullPath)
}

function collapseChildren(node, idx){
  let i = idx + 1
  while(i < treeNodes.value.length && treeNodes.value[i].depth > node.depth){
    treeNodes.value.splice(i, 1)
  }
}

async function buildRootTree(){
  const data = await fetchFolderData('')
  const items = []
  for(const d of data.folders){
    items.push({ name: d, fullPath: d, type: 'dir', depth: 0, expanded:false, loaded:false })
  }
  for(const f of data.images){
    items.push({ name: f, fullPath: f, type: 'file', depth: 0 })
  }
  treeNodes.value = items
}

onMounted(()=> buildRootTree())
</script>

<style scoped>
.gallery-layout{
  display:flex;
  /* 固定为基于视口的响应式背板：宽度自适应浏览器，居中，有边距，且高度基于视口而非内容 */
  width: calc(100% - 32px);
  max-width: none;
  margin: 16px auto;
  height: calc(100vh - 40px);
  min-height: 60vh;
  border-radius:10px;
  overflow:hidden;
  box-shadow: 0 6px 18px rgba(2,6,23,0.6);
}
.sidebar{ width:340px; min-width:240px; background: linear-gradient(180deg,#10242e 0%, #16383f 100%); color:#d7fbff; padding:20px; box-sizing:border-box; height:100% }
.brand{ font-weight:700; font-size:1.2rem; margin-bottom:8px }
.sidebar-controls{ display:flex; gap:8px; margin-bottom:12px }
.sidebar-controls button{ background:transparent; border:1px solid rgba(155,231,255,0.08); color:#9be7ff; padding:6px 8px; border-radius:6px }
.folder-list{ overflow:auto; max-height:50vh }
.folder-item{ display:flex; align-items:center; gap:8px; padding:8px; border-radius:6px; cursor:pointer; margin-bottom:6px }
.info-panel{ margin-top:12px; padding:8px; background: rgba(255,255,255,0.02); border-radius:6px }
.thumbs{ display:flex; gap:6px; flex-wrap:wrap; margin-top:8px }
.thumbs img{ width:46px; height:46px; object-fit:cover; border-radius:4px }
.folder-item:hover{ background:rgba(155,231,255,0.04) }
.folder-item.active{ background:linear-gradient(90deg, rgba(155,231,255,0.06), rgba(155,231,255,0.02)); border-left:3px solid #7fe7ff }
.fi-left{ width:30px; text-align:center }
.fi-name{ flex:1; text-align:left }

.main{ flex:1; background:linear-gradient(180deg,#123a42 0%, #0c2830 100%); padding:28px; box-sizing:border-box; height:100% }
.placeholder{ display:flex; align-items:center; justify-content:center; height:100% }
.placeholder-box{ text-align:center; color:#9be7ff; max-width:720px }
.placeholder .emoji{ font-size:3rem; margin-bottom:8px }
.content{ }
.content{ height:calc(100% - 64px); overflow:auto }
.images{ max-height:100%; overflow:auto }
.image-card{
  background: linear-gradient(180deg, rgba(28,38,44,0.92), rgba(18,28,34,0.88));
  border: 1px solid rgba(255,255,255,0.06);
  padding:10px;
  border-radius:12px;
  position:relative;
  overflow:hidden;
}
.select-checkbox{ position:absolute; left:8px; top:8px; background:rgba(0,0,0,0.35); padding:4px; border-radius:4px }
.image-card img{ width:100%; height:160px; object-fit:cover; border-radius:6px; cursor:pointer; display:block }
.content-header{ display:flex; justify-content:space-between; align-items:center; margin-bottom:12px }
.crumbs .crumb.clickable{ cursor:pointer; color:#9be7ff }
.images.grid{ display:grid; grid-template-columns: repeat(auto-fill,minmax(200px,1fr)); gap:16px }
.images.list{ display:block }
.image-card{ background:rgba(255,255,255,0.02); padding:8px; border-radius:8px }
.image-card img{ width:100%; height:180px; object-fit:cover; border-radius:6px; cursor:pointer }

/* meta area separated from main dark background */
.meta{
  display:flex;
  justify-content:space-between;
  align-items:center;
  margin-top:10px;
  padding:10px 12px;
  /* 更浅的 meta 背景以增强可读性 */
  background: rgba(255,255,255,0.02);
  border-radius:8px;
  border: 1px solid rgba(255,255,255,0.04);
  color: #e6fff9;
}
.name{
  font-weight:600;
  color:#e6fff9;
  overflow:hidden;
  text-overflow:ellipsis;
  white-space:nowrap;
  max-width:66%;
}
.actions{ display:flex; gap:8px; align-items:center }
.actions a, .actions button{ margin:0 }

/* button visuals inside cards */
.action-btn{
  padding:6px 10px;
  font-size:0.92rem;
  border-radius:6px;
  line-height:1;
}
.btn-outline.action-btn{
  border:1px solid rgba(110,210,220,0.26);
  color:#66e0e8;
  background:transparent;
}
.btn-primary.action-btn{
  background: linear-gradient(90deg,#11807f,#0c6b68);
  color:#e6fff9;
  border:none;
  box-shadow: 0 6px 14px rgba(10,60,60,0.28);
}

/* smaller, consistent action buttons inside each image card */
.action-btn{
  padding:6px 10px;
  font-size:0.92rem;
  border-radius:6px;
  line-height:1;
}
.actions a{ text-decoration:none; display:inline-block }

.btn-primary{
  background: linear-gradient(90deg,#0f3a45,#08323a);
  color:#bfeff6;
  border:none;
  padding:8px 12px;
  border-radius:8px;
  box-shadow: 0 6px 14px rgba(3,30,36,0.6);
  cursor:pointer;
  transition: transform .08s ease, box-shadow .12s ease;
}
.btn-primary:hover{ transform: translateY(-1px); box-shadow: 0 10px 20px rgba(3,30,36,0.6) }
.btn-primary:disabled{ opacity:0.45; cursor:not-allowed }
.btn-outline{
  background: transparent;
  color: #9be7ff;
  border: 1px solid rgba(155,231,255,0.08);
  padding:8px 12px;
  border-radius:8px;
}

/* responsive */
@media (max-width:900px){
  .gallery-layout{ flex-direction:column; /* 保持基于视口的高度，避免随内容塌缩 */ }
  .sidebar{ width:100%; display:flex; gap:12px; overflow:auto }
  .main{ height:auto }
}
</style>
