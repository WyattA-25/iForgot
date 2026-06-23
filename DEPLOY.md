# Deploying iForgot

This is the Week 3 runbook: take the container from Week 2 and put it on a public
URL that ten people can actually use, then capture proof and update the README and
resume. Read the "Pick a platform" section first; the memory math drives everything.

## Pick a platform (read this first)

iForgot is memory-heavy by nature: on startup it loads all five YOLOv8 models plus
PyTorch and OpenCV into a single process. That resident footprint, not disk size, is
what decides where this can run for free.

| Platform | Free RAM | Verdict |
|---|---|---|
| Render (free / starter) | 512 MB | Will OOM on model load. Needs the 2 GB Standard plan. |
| Railway (trial) | 512 MB on trial credit | Same memory wall; fine only on a paid plan with more RAM. |
| Fly.io | 256 MB default | Must bump to 1 GB+ (paid) and it is more setup. |
| Hugging Face Spaces | 16 GB, 2 vCPU, free CPU tier | Comfortable headroom. Recommended. |

Recommendation: deploy to Hugging Face Spaces (Docker SDK) on the free CPU tier.
It is the only free option with enough RAM, it is ML-native, and the same Dockerfile
works unchanged. Render is documented below as a paid fallback (render.yaml is included).

Model file size: the five .pt files total roughly 45 to 50 MB on disk (four YOLOv8n
detectors near 6 MB each, the headphones YOLOv8s detector near 22 MB). Confirm exact
sizes with `du -h models/*.pt`. They are small enough to bundle directly in the image,
so no external model storage is needed. The built image itself is larger, around 1.5
to 2 GB, almost entirely CPU PyTorch and ultralytics dependencies; every platform here
handles that fine.

Cold starts: free tiers sleep when idle. Hugging Face Spaces sleeps after 48 hours of
no traffic and wakes in roughly 30 seconds; Render free sleeps after 15 minutes. The
first request after sleep also pays the model-load cost (10 to 30 seconds). For a demo
where you message people a link, this is acceptable. Open the URL yourself a minute
before you share it so it is warm.

## Option A: Hugging Face Spaces (recommended, free)

Prerequisites: a free huggingface.co account and git with git-lfs installed
(`git lfs install` once).

1. Create the Space: New -> Space -> pick a name (for example `iforgot`) ->
   SDK = Docker -> Blank -> Public. This creates a git repo at
   `https://huggingface.co/spaces/<username>/iforgot`.

2. Hugging Face reads Space config from YAML front matter at the very top of README.md
   in the Space repo. Because the GitHub README has no front matter, the cleanest path
   is to keep the Space as its own repo with its own README. Put this at the top of the
   Space's README.md (the emoji here is Space metadata, the Space avatar, not README
   body text):

   ```
   ---
   title: iForgot
   emoji: 🔎
   colorFrom: indigo
   colorTo: purple
   sdk: docker
   app_port: 7860
   pinned: false
   ---
   ```

3. Track the weights with LFS (Hugging Face wants files over 10 MB in LFS), then push
   the app. From a clean copy of the repo:

   ```
   git clone https://huggingface.co/spaces/<username>/iforgot hf-iforgot
   cd hf-iforgot
   git lfs install
   git lfs track "*.pt"
   # copy these into the Space repo: Dockerfile, requirements.txt,
   # backend_middleware.py, lost-item-chat.html, models/, .dockerignore,
   # and a README.md that starts with the front matter from step 2
   git add .gitattributes README.md Dockerfile requirements.txt \
           backend_middleware.py lost-item-chat.html models .dockerignore
   git commit -m "Deploy iForgot container to Spaces"
   git push
   ```

4. Watch the build logs in the Space's UI. When it finishes, the app is live at
   `https://huggingface.co/spaces/<username>/iforgot`. That is your live URL.

## Option B: Render (paid fallback)

`render.yaml` is included as a Blueprint. It pins the Standard plan (2 GB) on purpose;
the free and Starter 512 MB instances OOM while loading the models.

1. Push this repo to GitHub (make sure models/ is committed; it is not gitignored).
2. In Render: New -> Blueprint -> connect the repo. It reads render.yaml.
3. Render injects $PORT and the container binds it automatically (the Dockerfile CMD
   uses `${PORT:-7860}`). Health checks hit /api/health.
4. Deploy. The URL is shown in the dashboard.

Railway and Fly.io follow the same shape: Docker deploy, bind $PORT, give it at least
1 GB of RAM. Use them only if you prefer them to Render; Hugging Face is still the
free choice.

## Local build and run (Week 2 verification)

Run this on your machine (Docker Desktop) to confirm the container works before
deploying. This is the Week 2 "builds and runs locally" check.

```
docker compose up --build
```

or plain Docker:

```
docker build -t iforgot:latest .
docker run --rm -p 7860:7860 iforgot:latest
```

First boot takes 10 to 30 seconds while the five models load (watch for
"All models loaded successfully" in the logs). Then:

- Open http://localhost:7860/ and upload a photo with a query like "find my keys".
- Health check: `curl http://localhost:7860/api/health` should return
  `{"status":"healthy",...}`.
- Model list: `curl http://localhost:7860/api/models`.

## Post-deploy verification (do this on the live URL)

1. Health: `curl https://<your-live-url>/api/health` returns status healthy.
2. Frontend: open the URL in a browser; the chat UI loads.
3. Real detection: upload a real photo of keys or glasses (your two strongest models,
   mAP about 0.99) with the matching query, and confirm a labeled box comes back.
   Keys and glasses are the most reliable for a first impression.
4. Warm it before sharing: hit the URL once so the first visitor does not wait on a
   cold start.

## Get about ten real people to use it

The point is real usage and proof, not load testing.

- Send the live URL to ten people (group chat, classmates, the robotics club, family)
  with one instruction: "Take or pick a photo with your keys or glasses in it, type
  'find my keys', and send me the result."
- Ask each to screenshot the result, or just confirm it worked.
- Note any failures (item not found, error, slow). These are useful README caveats and
  honest interview talking points.
- Tip: keys and glasses detect best; steer testers there so first impressions land.

## Capture the proof (screenshot or GIF)

Capture a real detection in place, on the live site:

- Screenshot: do a clean run on the live URL, capture the annotated result, save it to
  `docs/demo.png` in the repo.
- GIF (better): record upload -> result with a screen recorder (ScreenToGif on Windows,
  Kap on macOS, or the Xbox Game Bar) and save to `docs/demo.gif`. Keep it under about
  8 seconds and a few MB.
- Reference it near the top of README.md so it is the first thing a recruiter sees.

## Update the README and resume (ship it)

README:
- Replace the Live Demo placeholder with the real URL.
- Add the demo GIF/screenshot near the top.
- The mAP table is already there; leave earbuds and wallets as pending unless you run
  `model.val()` and get numbers.

Resume: add the live link and soften the sliding-window line so it reflects only your
verified contributions (you built the frontend, the Flask middleware/serving API, the
integration, and now the container + deployment; the sliding-window detection approach
and model training were teammates' work). Suggested bullets:

- Built and shipped iForgot, a multi-contributor computer-vision lost-item finder:
  designed the chat-style web frontend and the Flask serving API/middleware that routes
  uploads to five custom-trained YOLOv8 detectors and returns annotated results.
- Containerized the service with Docker (CPU-only PyTorch, single image serving both
  frontend and API) and deployed it to a public URL; budgeted for memory limits, model
  file size, and cold starts across free hosting tiers. Live: <your-live-url>
- Softened sliding-window phrasing (use this instead of claiming you built it):
  "Integrated a team-built sliding-window plus non-maximum-suppression detection
  pipeline behind the API I wrote," rather than "developed sliding-window detection."

## Done definition

iForgot is done when: the live URL serves /api/health and a real detection, about ten
people have used it, a detection GIF/screenshot is in the repo, and the README and
resume carry the live link. Then move on to Waymark (Week 4).
