<template>
  <div class="lazy-image" role="img" :aria-label="alt" ref="rootRef">
    <div class="placeholder" v-if="!visible || !loaded"></div>
    <img
      v-if="visible"
      :src="currentSrc"
      :alt="alt"
      ref="imgRef"
      @click="$emit('click')"
      @load="onNativeLoad"
      @error="$emit('error')"
      loading="lazy"
      class="real-img"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps({ src: { type: String, required: true }, alt: { type: String, default: '' } })
const emit = defineEmits(['click','load','error'])

// simple shared queue to limit concurrent image decoding/fetching
const MAX_CONCURRENT = 6
let activeLoads = 0
const loadQueue = []

function runQueue(){
  if(activeLoads >= MAX_CONCURRENT) return
  const job = loadQueue.shift()
  if(!job) return
  activeLoads++
  job().finally(()=>{ activeLoads--; runQueue() })
}

const imgRef = ref(null)
const rootRef = ref(null)
const visible = ref(false)
const loaded = ref(false)
const currentSrc = ref('')

function onNativeLoad(e){ loaded.value = true; emit('load', e) }

let io = null

function scheduleLoad(){
  // queue a loader that sets the src on success (use Image to pre-decode)
  loadQueue.push(()=> new Promise((resolve,reject)=>{
    const loader = new Image()
    loader.onload = ()=>{
      currentSrc.value = props.src
      resolve()
    }
    loader.onerror = (e)=>{ emit('error', e); resolve() }
    loader.src = props.src
  }))
  runQueue()
}

onMounted(()=>{
  // use IntersectionObserver to detect visibility
  io = new IntersectionObserver((entries)=>{
    for(const ent of entries){
      if(ent.isIntersecting){
        visible.value = true
        // schedule actual network/decode work via queue
        scheduleLoad()
        io.unobserve(ent.target)
      }
    }
  }, { rootMargin: '200px', threshold: 0.01 })

  // observe the wrapper element (safer when img isn't yet in DOM)
  const target = rootRef.value || imgRef.value
  if(target) io.observe(target)
})

onBeforeUnmount(()=>{ if(io) io.disconnect() })
</script>

<style scoped>
.lazy-image{ position:relative; width:100%; height:100%; min-height:140px; display:block }
.placeholder{ position:absolute; inset:0; background:linear-gradient(90deg,#0f2b2f,#123a42); border-radius:6px; }
.real-img{ width:100%; height:180px; object-fit:cover; border-radius:6px; display:block; opacity:0; transition: opacity .28s ease, transform .12s ease; }
.real-img[src]{ opacity:1; }
</style>
