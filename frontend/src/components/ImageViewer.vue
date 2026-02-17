<template>
  <div class="iv-backdrop" @click.self="close">
    <div class="iv-box" role="dialog" aria-modal="true">
        <div class="iv-header">
          <div class="iv-title">{{ filename }}</div>
          <div class="iv-actions">
            <button class="iv-btn iv-btn-save" @click="download" title="保存图片">保存图片</button>
            <button class="iv-btn iv-btn-close" @click="close" aria-label="关闭">✕</button>
          </div>
        </div>

        <div class="iv-body">
          <img :src="src" :style="imgStyle" ref="imgRef" @load="onLoad" />
        </div>

        <div class="iv-footer">
          <div class="zoom-group">
            <label class="zoom-label">缩放</label>
            <input class="zoom-range" type="range" min="0.2" max="3" step="0.05" v-model.number="scale" />
            <div class="zoom-value">{{ Math.round(scale * 100) }}%</div>
            <button class="iv-btn iv-btn-reset" @click="resetScale" title="恢复默认">重置</button>
          </div>
        </div>
      </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
const props = defineProps({ src: String })
const emit = defineEmits(['close'])

const scale = ref(1)
const imgRef = ref(null)
const filename = ref('')

function close(){ emit('close') }

function onLoad(){ /* reserved for future */ }

function download(){
  if(!props.src) return
  // ensure download param present
  let url = props.src
  url += (url.includes('?') ? '&' : '?') + 'download=true'
  const a = document.createElement('a')
  a.href = url
  a.target = '_blank'
  a.rel = 'noopener'
  a.click()
}

function resetScale(){ scale.value = 1 }

const imgStyle = computed(()=> ({ transform: `scale(${scale.value})`, transition: 'transform .08s' }))

watch(()=> props.src, ()=> {
  scale.value = 1
  // derive filename from src (try query param 'path' first)
  if(!props.src){ filename.value = '' ; return }
  try{
    const u = new URL(props.src, window.location.href)
    const p = u.searchParams.get('path')
    if(p){ filename.value = p.split('/').filter(Boolean).pop() }
    else filename.value = u.pathname.split('/').filter(Boolean).pop() || ''
  }catch(e){
    // fallback: last segment after / or after =
    const s = props.src
    const m = s.match(/path=([^&]+)/)
    if(m) filename.value = decodeURIComponent(m[1]).split('/').filter(Boolean).pop()
    else filename.value = s.split('/').filter(Boolean).pop() || ''
  }
})
</script>

<style scoped>
.iv-backdrop{ position:fixed; inset:0; background:rgba(6,10,12,0.75); display:flex; align-items:center; justify-content:center; z-index:40 }
.iv-box{ width:92%; max-width:1200px; background: linear-gradient(180deg,#123a42,#0d2b2f); padding:14px; border-radius:12px; box-shadow: 0 12px 40px rgba(0,0,0,0.6) }
.iv-header{ display:flex; justify-content:space-between; align-items:center; gap:12px; margin-bottom:8px }
.iv-title{ color:#e6fff9; font-weight:700; font-size:1rem; padding-left:6px }
.iv-actions{ display:flex; gap:8px; align-items:center }
.iv-body{ display:flex; align-items:center; justify-content:center; overflow:auto; max-height:72vh; background: rgba(255,255,255,0.02); padding:10px; border-radius:8px }
.iv-body img{ max-width:100%; max-height:72vh; display:block; border-radius:6px }
.iv-footer{ margin-top:10px; display:flex; gap:8px; align-items:center; justify-content:flex-start }

/* small, unobtrusive buttons */
.iv-btn{ padding:6px 10px; border-radius:6px; font-size:0.95rem; cursor:pointer; border:1px solid transparent; background:transparent }
.iv-btn-save{ color:#0f6b65; background: linear-gradient(90deg,#bfeff6,#9eeff0); border:1px solid rgba(15,100,95,0.12) }
.iv-btn-close{ color:#dbeefb; background: rgba(0,0,0,0.12); border:1px solid rgba(255,255,255,0.04) }
.iv-btn-reset{ color:#dbeefb; background: rgba(0,0,0,0.12); border:1px solid rgba(255,255,255,0.04) }

.zoom-group{ display:flex; align-items:center; gap:10px }
.zoom-label{ font-weight:600; color:#dffcff; margin-right:6px }
.zoom-range{ width:300px }
.zoom-value{ min-width:48px; text-align:center; color:#e6fff9; font-weight:600 }

@media (max-width:900px){
  .iv-box{ width:96%; padding:10px }
  .zoom-range{ width:180px }
}
</style>
