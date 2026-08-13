# NEXUS Full Test and Recording Plan

Run `python run.py`, then open `http://localhost:5173`. Run the checks below in
order; they also form a clean 4–6 minute demo video.

## 1. Startup and navigation

Confirm the dashboard opens and shows **System operational**. Click every left
navigation item. Each button should smoothly move to its matching dashboard
section. Record this for 10 seconds.

## 2. Backend catalog

Click **Backend health**. Confirm GPT-4o, Claude 4, Llama 3, and Mistral show
as **Ready** and Ollama as **Optional**. These are safe simulations: no API key
or local model is required. Record for 15 seconds.

## 3. Orion learned routing

Click **Orion decisions**. Set **Route via** to *Orion auto-route*, task to
*code*, and enter: `Write a Python async rate limiter with a token bucket.`
Click **Run inference**. Confirm the output, selected backend, confidence,
latency, cost, quality, and a reason mentioning Orion. Record for 30 seconds.

## 4. Explicit adapter selection

Keep the same prompt, select `mock-gpt-4o`, and run it. Confirm the selected
backend matches the dropdown. Repeat once with `mock-claude-4`. This proves
adapter selection works independently from Orion. Record for 25 seconds.

## 5. Semantic cache

Choose a new prompt, e.g. `Explain semantic caching in two sentences.` Run it
once, then immediately run it again unchanged. On the second request confirm
**Semantic cache hit**, `0ms`, and the yellow cache marker in Recent decisions.
Record for 30 seconds.

## 6. Live telemetry and WebSocket updates

Click **Analytics** and **Live requests**. Submit three different prompts. After
each one, confirm Requests increases, cost changes, and Recent decisions adds
an event without page refresh. Record this for 25 seconds.

## 7. API contract check

Open `http://localhost:8000/docs`. In `POST /api/v1/infer`, click **Try it
out**, submit a request, and inspect the typed JSON response. Record for 20
seconds.

## 8. Automated regression tests

In a PowerShell terminal at the project root, run:

```powershell
python -m pytest
cd frontend; npm run build
```

Record the passing test summary and successful frontend build for 15 seconds.

## Expected result

All backend tests pass, the dashboard build succeeds, left navigation scrolls,
Orion routes unpinned requests, explicit selection works, cache hits occur on
the second identical request, and live metrics update without reload.
