#!/usr/bin/env python3
"""Generate 6 procedure card images via Kie AI GPT Image 2 text-to-image."""
import requests, json, time, subprocess, os

API_KEY = "5f79f80ec3b15c78db437ee493e260e4"
BASE = "https://api.kie.ai/api/v1/jobs"
OUT_DIR = "/Users/carlostamesmosino-macmini/Desktop/ANTIGRAVITY/PROCTOLOGOS.MX 2026/site/images/generated"

# 6 procedure-specific prompts: editorial medical photography style
TASKS = [
    {
        "name": "proc-ligadura",
        "prompt": "Editorial medical photography: close-up of a rubber band ligator device for hemorrhoid treatment on a sterile surgical tray, shallow depth of field, soft blue surgical lighting, dark background, ultra-realistic, 4K, no text"
    },
    {
        "name": "proc-laser",
        "prompt": "Editorial medical photography: a medical-grade diode laser fiber tip emitting a precise red beam during a minimally invasive hemorrhoid procedure, shallow depth of field, dramatic blue and amber surgical lighting, dark operating room background, ultra-realistic, 4K, no text"
    },
    {
        "name": "proc-thd",
        "prompt": "Editorial medical photography: a THD Doppler proctoscope device with ultrasound transducer on a sterile draped surgical table, close-up detail shot, soft blue ambient lighting, dark clinical background, ultra-realistic, 4K, no text"
    },
    {
        "name": "proc-lift-vaaft",
        "prompt": "Editorial medical photography: a video-assisted anal fistula treatment (VAAFT) fistuloscope with attached camera and light source on a surgical instrument tray, macro close-up, dramatic blue surgical lighting, dark background, ultra-realistic, 4K, no text"
    },
    {
        "name": "proc-silac",
        "prompt": "Editorial medical photography: an endoscopic pilonidal sinus treatment instrument with laser fiber attachment, sterile stainless steel, close-up on dark surgical drape, blue-white clinical lighting, ultra-realistic, 4K, no text"
    },
    {
        "name": "proc-diagnostico",
        "prompt": "Editorial medical photography: a high-resolution anoscope and endoanal ultrasound probe side by side on a dark surgical tray, shallow depth of field, soft blue clinical lighting, professional product photography style, ultra-realistic, 4K, no text"
    }
]

def create_task(prompt):
    r = requests.post(f"{BASE}/createTask", json={
        "modelFamily": "gpt-image-2",
        "prompt": prompt,
        "size": "1024x1024",
        "quality": "high"
    }, headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"})
    data = r.json()
    print(f"  → task: {data.get('taskId','?')} status={data.get('status','?')}")
    return data.get("taskId")

def poll(task_id, timeout=300):
    t0 = time.time()
    while time.time() - t0 < timeout:
        r = requests.get(f"{BASE}/recordInfo", params={"taskId": task_id},
                         headers={"Authorization": f"Bearer {API_KEY}"})
        d = r.json()
        st = d.get("status","unknown")
        if st == "completed":
            rj = d.get("resultJson","")
            try:
                urls = json.loads(rj) if isinstance(rj, str) else rj
                if isinstance(urls, list) and urls:
                    return urls[0].get("url") or urls[0].get("image_url") or urls[0]
            except: pass
            return None
        elif st == "failed":
            print(f"  ✗ FAILED: {d.get('failReason','?')}")
            return None
        time.sleep(10)
        elapsed = int(time.time() - t0)
        print(f"  ⏳ {st}... ({elapsed}s)", end="\r")
    return None

print("🎨 Generating 6 procedure images via GPT Image 2...\n")
task_ids = []
for t in TASKS:
    print(f"📤 {t['name']}:")
    tid = create_task(t["prompt"])
    task_ids.append((t["name"], tid))
    time.sleep(1)

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
        print(f"  ✗ {name}: no URL")

print("\n🏁 Done!")
