#!/usr/bin/env python3
"""
Proctologos.mx — Batch Image Generation via Kie AI
Models: Flux-2 Pro, Nano Banana 2, Seedream 5.0 Lite
"""

import json
import os
import subprocess
import sys
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

API_KEY = "5f79f80ec3b15c78db437ee493e260e4"
BASE_URL = "https://api.kie.ai/api/v1/jobs/createTask"
POLL_URL = "https://api.kie.ai/api/v1/jobs/recordInfo"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "..", "images", "generated")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Image definitions ──────────────────────────────────────────────────
IMAGES = [
    {
        "name": "proc-laser",
        "model": "flux-2/pro-text-to-image",
        "prompt": (
            "Professional medical editorial photograph. Close-up of modern "
            "minimally invasive laser surgical equipment in a pristine clinical "
            "setting. Subtle blue and amber LED indicators on the device. Clean "
            "white surfaces, soft diffused lighting. Shallow depth of field, "
            "85mm macro lens. Premium healthcare technology advertising. "
            "No text, no watermarks, no people."
        ),
        "aspect_ratio": "3:4",
        "resolution": "1K",
    },
    {
        "name": "proc-ligadura",
        "model": "seedream/5-lite-text-to-image",
        "prompt": (
            "Professional medical editorial photograph. A sterile modern "
            "operating room prepared for a minimally invasive procedure. "
            "Clean stainless steel instruments arranged precisely on a "
            "surgical tray. Soft overhead surgical lighting creating clean "
            "shadows. Desaturated color palette with warm amber accents. "
            "Shot on medium format camera, 50mm lens. Premium healthcare "
            "advertising aesthetic. No text, no watermarks, no people."
        ),
        "aspect_ratio": "3:4",
        "quality": "basic",
    },
    {
        "name": "proc-thd",
        "model": "nano-banana-2",
        "prompt": (
            "Professional medical editorial photograph. Modern digital "
            "diagnostic display showing medical imaging on a sleek monitor "
            "in a dark consultation room. Soft ambient lighting from the "
            "screen casting subtle blue and amber tones. Clean minimalist "
            "medical office environment. Shallow depth of field. Premium "
            "healthcare technology aesthetic. No text, no watermarks, no people."
        ),
        "aspect_ratio": "3:4",
        "resolution": "1K",
    },
    {
        "name": "proc-lift-vaaft",
        "model": "seedream/5-lite-text-to-image",
        "prompt": (
            "Professional medical editorial photograph. An advanced minimally "
            "invasive surgical setup in a modern operating room. Fiber optic "
            "equipment with subtle blue light glow. Ultra-clean environment "
            "with white and chrome surfaces. Soft natural light from frosted "
            "windows. Shallow depth of field, 85mm lens. Desaturated color "
            "palette with warm amber tones. Premium healthcare advertising. "
            "No text, no watermarks, no people."
        ),
        "aspect_ratio": "3:4",
        "quality": "basic",
    },
    {
        "name": "proc-silac",
        "model": "flux-2/pro-text-to-image",
        "prompt": (
            "Professional medical editorial photograph. A modern medical "
            "consultation room with a doctor reviewing patient charts on a "
            "tablet. Clean minimalist interior with warm wood accents and "
            "soft natural light through large windows. Desaturated palette "
            "with amber highlights. Shot on medium format camera, 50mm lens. "
            "Premium healthcare advertising. No text, no watermarks."
        ),
        "aspect_ratio": "3:4",
        "resolution": "1K",
    },
    {
        "name": "proc-diagnostico",
        "model": "nano-banana-2",
        "prompt": (
            "Professional medical editorial photograph. Advanced proctological "
            "diagnostic equipment in a pristine examination room. Modern "
            "medical technology with subtle LED indicators. Clean white "
            "surfaces, professional medical environment. Soft diffused "
            "overhead lighting. Desaturated color palette. Premium healthcare "
            "technology advertising aesthetic. No text, no watermarks, no people."
        ),
        "aspect_ratio": "3:4",
        "resolution": "1K",
    },
    {
        "name": "doctor-portrait",
        "model": "seedream/5-lite-text-to-image",
        "prompt": (
            "Professional medical portrait photograph. A confident male Latin "
            "American doctor in his 40s wearing a pristine white lab coat, "
            "standing in a modern medical office. Warm natural light from "
            "large window. Clean background with subtle medical office "
            "elements. Desaturated color palette with warm amber tones. "
            "Shot on medium format camera, 85mm portrait lens, shallow "
            "depth of field. Premium healthcare advertising. No text, "
            "no watermarks."
        ),
        "aspect_ratio": "3:4",
        "quality": "basic",
    },
    {
        "name": "contacto-sala",
        "model": "flux-2/pro-text-to-image",
        "prompt": (
            "Professional medical editorial photograph. Modern medical office "
            "reception and waiting area. Elegant minimalist design with warm "
            "wood paneling, comfortable designer seating, and soft ambient "
            "lighting. Large windows with natural light. Indoor plants adding "
            "organic touches. Desaturated palette with amber accents. Shot on "
            "wide angle 24mm lens. Premium healthcare facility advertising. "
            "No text, no watermarks, no people."
        ),
        "aspect_ratio": "16:9",
        "resolution": "1K",
    },
]


def api_request(url, data=None, method="GET"):
    """Make an authenticated API request."""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        print(f"  HTTP {e.code}: {error_body[:200]}")
        return None
    except Exception as e:
        print(f"  Error: {e}")
        return None


def create_task(image_def):
    """Submit a generation task to Kie AI."""
    name = image_def["name"]
    model = image_def["model"]

    # Build input based on model type
    input_obj = {
        "prompt": image_def["prompt"],
        "aspect_ratio": image_def["aspect_ratio"],
        "nsfw_checker": False,
    }

    if model == "seedream/5-lite-text-to-image":
        input_obj["quality"] = image_def.get("quality", "basic")
    else:
        input_obj["resolution"] = image_def.get("resolution", "1K")

    payload = {"model": model, "input": input_obj}

    print(f"🚀 [{name}] → {model}")
    result = api_request(BASE_URL, data=payload, method="POST")

    if result and result.get("code") == 200:
        task_id = result["data"]["taskId"]
        print(f"   ✅ taskId={task_id}")
        return task_id, name
    else:
        print(f"   ❌ Failed: {result}")
        return None, name


def poll_and_download(task_id, name, max_attempts=50, interval=8):
    """Poll task status and download when complete."""
    for attempt in range(1, max_attempts + 1):
        time.sleep(interval)
        url = f"{POLL_URL}?taskId={task_id}"
        result = api_request(url)

        if not result or result.get("code") != 200:
            print(f"   ⚠️  [{name}] poll error (attempt {attempt})")
            continue

        state = result["data"].get("state", "unknown")

        if state == "success":
            result_json = json.loads(result["data"]["resultJson"])
            image_url = result_json["resultUrls"][0]
            output_path = os.path.join(OUTPUT_DIR, f"{name}.png")

            # Download image (curl handles redirects better than urllib)
            dl = subprocess.run(
                ["curl", "-L", "-s", "-o", output_path, image_url],
                capture_output=True, text=True, timeout=60
            )
            if dl.returncode != 0:
                print(f"   ⚠️  [{name}] download failed: {dl.stderr[:100]}")
                return False
            size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
            cost = result["data"].get("costTime", "?")
            print(f"   ✅ [{name}] downloaded — {size:,} bytes ({cost}s)")
            return True

        elif state == "fail":
            msg = result["data"].get("failMsg", "unknown error")
            print(f"   ❌ [{name}] failed: {msg}")
            return False

        else:
            if attempt % 3 == 0:  # Print every 3rd attempt to reduce noise
                print(f"   ⏳ [{name}] {state} ({attempt}/{max_attempts})")

    print(f"   ⏰ [{name}] timed out")
    return False


def main():
    print("=" * 50)
    print("  Proctologos.mx — Image Generation")
    print("  Models: Flux-2 Pro · Nano Banana 2 · Seedream 5")
    print("=" * 50)
    print(f"  Output: {OUTPUT_DIR}")
    print()

    # Check credits first
    credit_url = "https://api.kie.ai/api/v1/chat/credit"
    credits = api_request(credit_url)
    if credits and credits.get("code") == 200:
        data = credits.get("data")
        if isinstance(data, (int, float)):
            balance = data
        elif isinstance(data, dict):
            balance = data.get("totalCredits", data)
        else:
            balance = data
        print(f"  💰 Credits available: {balance}")
    print()

    # Submit all tasks
    tasks = []
    for img in IMAGES:
        task_id, name = create_task(img)
        if task_id:
            tasks.append((task_id, name))
        time.sleep(0.5)  # Brief pause between submissions

    print(f"\n{'=' * 50}")
    print(f"  {len(tasks)}/{len(IMAGES)} tasks submitted. Polling...")
    print(f"{'=' * 50}\n")

    # Poll all in parallel
    results = {"success": 0, "failed": 0}
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(poll_and_download, tid, name): name
            for tid, name in tasks
        }
        for future in as_completed(futures):
            name = futures[future]
            try:
                if future.result():
                    results["success"] += 1
                else:
                    results["failed"] += 1
            except Exception as e:
                print(f"   ❌ [{name}] exception: {e}")
                results["failed"] += 1

    # Summary
    print(f"\n{'=' * 50}")
    print(f"  ✅ Success: {results['success']}")
    print(f"  ❌ Failed:  {results['failed']}")
    print(f"{'=' * 50}")
    print(f"\nFiles in {OUTPUT_DIR}:")
    for f in sorted(os.listdir(OUTPUT_DIR)):
        path = os.path.join(OUTPUT_DIR, f)
        if os.path.isfile(path):
            size = os.path.getsize(path)
            print(f"  {f:30s} {size:>10,} bytes")


if __name__ == "__main__":
    main()
