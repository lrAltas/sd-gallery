<template>
  <div class="iv-backdrop" @click.self="close">
    <div class="iv-box">
      <div class="iv-header">
        <button @click="download">下载</button>
        <button @click="close">关闭</button>
      </div>
      <div class="iv-body">
        <img :src="src" :style="imgStyle" ref="imgRef" @load="onLoad" />
      </div>
      <div class="iv-footer">
        <label>缩放</label>
        <input type="range" min="0.2" max="3" step="0.05" v-model.number="scale" />
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

function close(){ emit('close') }

function onLoad(){ /* reserved for future */ }

function download(){
  if(!props.src) return
  const a = document.createElement('a')
  a.href = props.src + '&download=true'
  a.target = '_blank'
  a.click()
}

const imgStyle = computed(()=> ({ transform: `scale(${scale.value})`, transition: 'transform .08s' }))

watch(()=> props.src, ()=> { scale.value = 1 })
</script>

<style scoped>
.iv-backdrop{ position:fixed; inset:0; background:rgba(0,0,0,0.7); display:flex; align-items:center; justify-content:center; z-index:40 }
.iv-box{ width:90%; max-width:1100px; background: #0f1720; padding:12px; border-radius:10px }
.iv-header{ display:flex; justify-content:flex-end; gap:8px }
.iv-body{ display:flex; align-items:center; justify-content:center; overflow:auto; max-height:70vh }
.iv-body img{ max-width:100%; max-height:70vh; display:block }
.iv-footer{ margin-top:8px; display:flex; gap:8px; align-items:center }
</style>
