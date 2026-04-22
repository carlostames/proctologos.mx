#!/usr/bin/env python3
"""Generate 6 procedure card images via Kie AI Nano Banana 2."""
import requests, json, time, subprocess, os

API_KEY = "5f79f80ec3b15c78db437ee493e260e4"
BASE = "https://api.kie.ai/api/v1/jobs"
OUT_DIR = "/Users/carlostamesmosino-macmini/Desktop/ANTIGRAVITY/PROCTOLOGOS.MX 2026/site/images/generated"

TASKS = [
    {
        "name": "proc-ligadura",
        "prompt": "Professional editorial medical product photography: a rubber band ligator hemorrhoid device with loading mechanism, displayed on dark surgical tray with black velvet background, dramatic single-source studio lighting from left, shallow depth of field, stainless steel gleaming, ultra-photorealistic, 8K detail, no text, no watermarks"
    },
    {
        "name": "proc-laser",
        "prompt": "Professional editorial medical product photography: a medical diode laser handpiece emitting thin red laser beam, fiber optic tip glowing, placed on dark sterile surgical drape, dramatic amber and blue accent lighting, shallow depth of field, ultra-photorealistic, 8K detail, no text, no watermarks"
    },
    {
        "name": "proc-thd",
        "prompt": "Professional editorial medical product photography: a THD Doppler hemorrhoid device with ultrasound probe and circular proctoscope, displayed on dark surgical steel tray, blue ambient LED lighting, shallow depth of field, ultra-photorealistic, 8K detail, no text, no watermarks"
    },
    {
        "name": "proc-lift-vaaft",
        "prompt": "Professional editorial medical product photography: a fistuloscope surgical instrument with video camera attachment for VAAFT procedure, displayed on dark sterile blue drape, dramatic clinical lighting, stainless steel details, ultra-photorealistic, 8K detail, no text, no watermarks"
    },
    {
        "name": "proc-silac",
        "prompt": "Professional editorial medical product photography: a thin laser fiber probe for pilonidal sinus treatment (SiLaC procedure), with endoscope attachment, displayed on dark matte black surgical tray, dramatic blue-white clinical lighting, ultra-photorealistic, 8K detail, no text, no watermarks"
    },
    {
        "name": "proc-diagnostico",
        "prompt": "Professional editorial medical product photography: a high-resolution digital anoscope and endoanal ultrasound transducer probe side by side on dark surgical instrument tray, blue ambient clinical lighting, shallow depth of field, ultra-photorealistic, 8K detail, no text, no watermarks"
    }
]

def create_task(prompt):
    r = requests.post(f"{BASE}/createTask", json={
        "model": "nano-banana-2",
        "input": {
            "prompt": prompt,
            "aspect_ratio": "1:1"
        }
    }, headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"})
    data = r.json()
    tid = data.get("data", {}).get("taskId")
    print(f"  → taskId: {tid}")
    return tid

def poll(task_id, timeout=300):
    t0 = time.time()
    while time.time() - t0 < timeout:
        r = requests.get(f"{BASE}/recordInfo", params={"taskId": task_id},
                         headers={"Authorization": f"Bearer {API_KEY}"})
        d = r.json().get("data", {})
        st = d.get("status", "unknown")
        if st == "completed":
            rj = d.get("resultJson", "")
            try:
                urls = json.loads(rj) if isinstance(rj, str) else rj
                if isinstance(urls, list) and urls:
                    return urls[0].get("url") or urls[0].get("image_url") or str(urls[0])
                if isinstance(urls, dict):
                    return urls.get("url") or urls.get("image_url")
            except:
                pass
            return None
        elif st == "failed":
            print(f"  ✗ FAILED: {d.get('failReason','?')}")
            return None
        elapsed = int(time.time() - t0)
        print(f"  ⏳ {st}... ({elapsed}s)")
        time.sleep(10)
    return None

print("🎨 Generating 6 procedure images via Nano Banana 2...\n")
task_ids = []
for t in TASKS:
    print(f"📤 {t['name']}:")
    tid = create_task(t["prompt"])
    task_ids.append((t["name"], tid))
    time.sleep(0.5)

print(f"\n⏳ Polling {len(task_ids)} tasks...\n")
for name, tid in task_ids:
    if not tid:
        print(f"  ✗ {name}: no task ID")
        continue
    print(f"⏳ {name}:")
    url = poll(tid)
    if url:
        out = os.path.join(OUT_DIR, f"{name}.png")
        subprocess.run(["curl", "-sL", "-o", out, url], check=True)
        sz = os.path.getsize(out)
        print(f"  ✅ {name} → {sz//1024}KB")
    else:
        print(f"  ✗ {name}: no URL returned")

print("\n🏁 Done!")
