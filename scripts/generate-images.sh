#!/bin/bash
# Kie AI Image Generation Script for Proctologos.mx
# Models: Flux-2 Pro, Nano Banana 2, Seedream 5.0 Lite

API_KEY="5f79f80ec3b15c78db437ee493e260e4"
BASE_URL="https://api.kie.ai/api/v1/jobs/createTask"
POLL_URL="https://api.kie.ai/api/v1/jobs/recordInfo"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OUTPUT_DIR="$SCRIPT_DIR/../images/generated"

mkdir -p "$OUTPUT_DIR"
> "$OUTPUT_DIR/pending_tasks.txt"

# --- Create task for Flux-2 or Nano Banana (resolution-based) ---
create_task_resolution() {
  local model="$1"
  local prompt="$2"
  local aspect="$3"
  local name="$4"
  local resolution="${5:-1K}"

  echo "🚀 [$name] model=$model"

  local response=$(curl -s -X POST "$BASE_URL" \
    -H "Authorization: Bearer $API_KEY" \
    -H "Content-Type: application/json" \
    -d "$(python3 -c "
import json
print(json.dumps({
  'model': '$model',
  'input': {
    'prompt': '''$prompt''',
    'aspect_ratio': '$aspect',
    'resolution': '$resolution',
    'nsfw_checker': False
  }
}))
")")

  local task_id=$(echo "$response" | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['taskId'])" 2>/dev/null)

  if [ -z "$task_id" ]; then
    echo "❌ Failed: $name — $response"
    return 1
  fi

  echo "✅ taskId=$task_id"
  echo "$task_id|$name" >> "$OUTPUT_DIR/pending_tasks.txt"
}

# --- Create task for Seedream (quality-based) ---
create_task_seedream() {
  local prompt="$1"
  local aspect="$2"
  local name="$3"
  local quality="${4:-basic}"

  echo "🚀 [$name] model=seedream/5-lite-text-to-image"

  local response=$(curl -s -X POST "$BASE_URL" \
    -H "Authorization: Bearer $API_KEY" \
    -H "Content-Type: application/json" \
    -d "$(python3 -c "
import json
print(json.dumps({
  'model': 'seedream/5-lite-text-to-image',
  'input': {
    'prompt': '''$prompt''',
    'aspect_ratio': '$aspect',
    'quality': '$quality',
    'nsfw_checker': False
  }
}))
")")

  local task_id=$(echo "$response" | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['taskId'])" 2>/dev/null)

  if [ -z "$task_id" ]; then
    echo "❌ Failed: $name — $response"
    return 1
  fi

  echo "✅ taskId=$task_id"
  echo "$task_id|$name" >> "$OUTPUT_DIR/pending_tasks.txt"
}

# --- Poll and download ---
poll_and_download() {
  local task_id="$1"
  local name="$2"
  local max_attempts=40
  local attempt=0

  while [ $attempt -lt $max_attempts ]; do
    sleep 8
    attempt=$((attempt + 1))

    local result=$(curl -s -H "Authorization: Bearer $API_KEY" "$POLL_URL?taskId=$task_id")
    local state=$(echo "$result" | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['state'])" 2>/dev/null)

    if [ "$state" = "success" ]; then
      local url=$(echo "$result" | python3 -c "
import sys,json
d=json.load(sys.stdin)['data']
r=json.loads(d['resultJson'])
print(r['resultUrls'][0])
" 2>/dev/null)
      curl -s -o "$OUTPUT_DIR/${name}.png" "$url"
      local size=$(ls -la "$OUTPUT_DIR/${name}.png" | awk '{print $5}')
      echo "✅ $name — downloaded (${size} bytes)"
      return 0
    elif [ "$state" = "fail" ]; then
      local msg=$(echo "$result" | python3 -c "import sys,json; print(json.load(sys.stdin)['data'].get('failMsg','unknown'))" 2>/dev/null)
      echo "❌ $name failed: $msg"
      return 1
    else
      echo "⏳ $name: $state ($attempt/$max_attempts)"
    fi
  done

  echo "⏰ $name timed out after $max_attempts attempts"
  return 1
}

echo "========================================"
echo "  Proctologos.mx — Image Generation"
echo "========================================"
echo "Output: $OUTPUT_DIR"
echo ""

# ========== PROCEDIMIENTOS ==========

# 1. Laser — Flux-2 Pro (best photorealism)
create_task_resolution "flux-2/pro-text-to-image" \
  "Professional medical editorial photograph. Close-up of modern minimally invasive laser surgical equipment in a pristine clinical setting. Subtle blue and amber LED indicators on the device. Clean white surfaces, soft diffused lighting. Shallow depth of field, 85mm macro lens. Premium healthcare technology advertising. No text, no watermarks, no people." \
  "3:4" "proc-laser" "1K"

# 2. Ligadura — Seedream (photorealistic 2K)
create_task_seedream \
  "Professional medical editorial photograph. A sterile modern operating room prepared for a minimally invasive procedure. Clean stainless steel instruments arranged precisely on a surgical tray. Soft overhead surgical lighting creating clean shadows. Desaturated color palette with warm amber accents. Shot on medium format camera, 50mm lens. Premium healthcare advertising aesthetic. No text, no watermarks, no people." \
  "3:4" "proc-ligadura" "basic"

# 3. THD — Nano Banana 2
create_task_resolution "nano-banana-2" \
  "Professional medical editorial photograph. Modern digital diagnostic display showing medical imaging on a sleek monitor in a dark consultation room. Soft ambient lighting from the screen casting subtle blue and amber tones. Clean minimalist medical office environment. Shallow depth of field. Premium healthcare technology aesthetic. No text, no watermarks, no people." \
  "3:4" "proc-thd" "1K"

# 4. LIFT-VAAFT — Seedream
create_task_seedream \
  "Professional medical editorial photograph. An advanced minimally invasive surgical setup in a modern operating room. Fiber optic equipment with subtle blue light glow. Ultra-clean environment with white and chrome surfaces. Soft natural light from frosted windows. Shallow depth of field, 85mm lens. Desaturated color palette with warm amber tones. Premium healthcare advertising. No text, no watermarks, no people." \
  "3:4" "proc-lift-vaaft" "basic"

# 5. SILAC — Flux-2 Pro
create_task_resolution "flux-2/pro-text-to-image" \
  "Professional medical editorial photograph. A modern medical consultation room with a doctor reviewing patient charts on a tablet. Clean minimalist interior with warm wood accents and soft natural light through large windows. Desaturated palette with amber highlights. Shot on medium format camera, 50mm lens. Premium healthcare advertising. No text, no watermarks." \
  "3:4" "proc-silac" "1K"

# 6. Diagnostico — Nano Banana 2
create_task_resolution "nano-banana-2" \
  "Professional medical editorial photograph. Advanced proctological diagnostic equipment in a pristine examination room. Modern medical technology with subtle LED indicators. Clean white surfaces, professional medical environment. Soft diffused overhead lighting. Desaturated color palette. Premium healthcare technology advertising aesthetic. No text, no watermarks, no people." \
  "3:4" "proc-diagnostico" "1K"

# ========== RETRATOS / SECCIONES ==========

# 7. Doctor portrait — Seedream (excels at portraits)
create_task_seedream \
  "Professional medical portrait photograph. A confident male Latin American doctor in his 40s wearing a pristine white lab coat, standing in a modern medical office. Warm natural light from large window. Clean background with subtle medical office elements. Desaturated color palette with warm amber tones. Shot on medium format camera, 85mm portrait lens, shallow depth of field. Premium healthcare advertising. No text, no watermarks." \
  "3:4" "doctor-portrait" "basic"

# 8. Sala de espera — Flux-2 (wide architectural)
create_task_resolution "flux-2/pro-text-to-image" \
  "Professional medical editorial photograph. Modern medical office reception and waiting area. Elegant minimalist design with warm wood paneling, comfortable designer seating, and soft ambient lighting. Large windows with natural light. Indoor plants adding organic touches. Desaturated palette with amber accents. Shot on wide angle 24mm lens. Premium healthcare facility advertising. No text, no watermarks, no people." \
  "16:9" "contacto-sala" "1K"

echo ""
echo "=== All 8 tasks submitted! ==="
echo "Starting parallel polling..."
echo ""

# Poll all tasks in parallel
if [ -f "$OUTPUT_DIR/pending_tasks.txt" ]; then
  while IFS='|' read -r task_id name; do
    poll_and_download "$task_id" "$name" &
  done < "$OUTPUT_DIR/pending_tasks.txt"

  wait
  rm -f "$OUTPUT_DIR/pending_tasks.txt"
fi

echo ""
echo "=== Generation Complete ==="
ls -la "$OUTPUT_DIR"
