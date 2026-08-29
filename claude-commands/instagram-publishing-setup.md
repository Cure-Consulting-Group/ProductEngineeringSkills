# Instagram Publishing Setup

Stand up **programmatic Instagram publishing for one brand**, end to end: Meta developer app → permissions → token → media hosting → publishing, immediate or scheduled.

Written from a real setup that took a full session of dead ends. Every trap below cost time; none of them are in Meta's docs in a form you'd find before hitting them.

## When to use this

- A brand needs to publish to Instagram from code (reels, images, articles-as-graphics)
- Someone is stuck on **"Insufficient Developer Role"**, a token that seems invisible, or a publish that 400s with an unhelpful message
- You want scheduled Instagram posts — which Meta does **not** provide

## The three things to know before starting

1. **The Content Publishing API is free.** There is no paid tier for posting to your own Instagram Business account. Do not build a manual workflow on the belief that publishing costs money.
2. **There is no scheduling parameter.** `media_publish` goes live the instant it is called. Scheduling must come from your own scheduler. Meta's Business Suite can schedule *Facebook*, not Instagram.
3. **Development mode is enough.** For your *own* account you do not need App Review or Business Verification.

---

## Phase 0 — Prerequisites

Confirm all four before touching the developer console. Each failure here surfaces later as a confusing error.

| Requirement | How to check | If wrong |
|---|---|---|
| Instagram is **Business or Creator**, not Personal | IG app → Settings → Account type | Switch to Professional |
| Instagram account is **public** | Settings → Privacy | Tokens cannot be generated for private accounts |
| Linked to a **Facebook Page** | Page → Settings → Linked accounts | Link it |
| You are **admin** of both | Meta Business Suite → Settings | Get admin |

---

## Phase 1 — Meta app with the Instagram use case

1. <https://developers.facebook.com/apps> → **Create app**
2. Pick the **business** app type
3. Add the use case: **"Manage messaging & content on Instagram"**

Record the **App ID**. App status stays **Unpublished / development** — that is correct and sufficient.

## Phase 2 — Permissions

Use case → **Customize** → **API setup with Instagram login**.

1. **Add all required permissions** (`instagram_business_basic`, `_manage_comments`, `_manage_messages`)
2. **Permissions and features** → find **`instagram_business_content_publish`** → **Add**

> ### ✅ The checkpoint that decides everything
> `instagram_business_content_publish` must read **"Ready for testing."**
>
> That status means publishing works for your own account with **no App Review**. If it says anything else, stop and resolve it — everything downstream depends on it.

**Trap:** the Graph API Explorer's permission dropdown only lists permissions for products already added to the app. If you see just `business_management` and `pages_show_list`, the use case isn't configured — go back to Phase 1 rather than concluding you lack access.

## Phase 3 — Instagram Tester role

> ### ⚠️ This is where most setups fail
> Symptom: clicking **Add account** → login → **"Insufficient Developer Role."**
>
> Cause: the *Instagram account* has no role on the app. Being the app admin is not enough.

1. App → **App roles → Roles** → **More ▾ → Instagram Testers**
2. **Add People** → **Instagram Tester** → enter the IG username → Add
3. **Accept from the Instagram side** — the step people miss:
   **Instagram app → Settings and privacy → Apps and websites → Tester invites → Accept**

Nothing works until the invite is accepted *in Instagram*.

## Phase 4 — Token

Back at **API setup with Instagram login → Generate access tokens → Add account**, log in, then **Generate token**.

- **The token is long-lived — 60 days.** Not one hour. The 1-hour token belongs to the OAuth-code flow; the dashboard button issues a long-lived one directly, so **no app-secret exchange is needed**.
- **It is masked behind a "Show" toggle.** If you "can't see the token," it is there — use the **Copy** button, which puts it on the clipboard without ever rendering it.

> ### 🔒 Never paste a token into a chat, a commit, a log, or a command argument
> Pipe it straight from the clipboard into your secret store:
> ```bash
> pbpaste | gcloud secrets versions add IG_ACCESS_TOKEN \
>   --project=<PROJECT_ID> --data-file=-
> ```
> Create the container empty first (`gcloud secrets create IG_ACCESS_TOKEN --replication-policy=automatic`) so the value never appears in an argument.

## Phase 5 — Verify, and get the *real* account ID

```bash
TOKEN="$(gcloud secrets versions access latest --secret=IG_ACCESS_TOKEN --project=<PROJECT_ID>)"
curl -s -H "Authorization: Bearer ${TOKEN}" "https://graph.instagram.com/v23.0/me?fields=id,username,account_type"
```

> ### ⚠️ Use the ID `/me` returns — not the one on the setup page
> The setup screen shows an Instagram-app-scoped ID. The publishing calls need the ID from `/me`. They are different numbers, and using the wrong one fails **at `media_publish`**, after you have built everything.

Expect `"account_type":"BUSINESS"`. Then check quota:

```bash
curl -s -H "Authorization: Bearer ${TOKEN}" \
  "https://graph.instagram.com/v23.0/<IG_USER_ID>/content_publishing_limit"
```

Docs say 100 posts/24h; third parties say 25. **Trust this endpoint, not either number.**

Or run the bundled checker, which does all of the above read-only and never prints the token:

```bash
python3 scripts/verify_publishing_setup.py --project <GCP_PROJECT> --bucket <MEDIA_BUCKET>
```

## Phase 6 — Media hosting

Instagram fetches `video_url` / `image_url` **itself**, at container-creation time only.

- Keep media in a **private** bucket and hand over a **short-lived signed URL**. Nothing needs to be world-readable.
- The signing identity needs `roles/iam.serviceAccountTokenCreator` **on itself**, plus read on the bucket.

> ### ⚠️ Instagram accepts **JPEG only** for images
> PNG fails at container creation with an error that never mentions the format. Convert first:
> ```bash
> sips -s format jpeg -s formatOptions 90 card.png --out card.jpg
> ```

Format rules: reels 9:16 MP4; feed images JPEG, 4:5 (1080×1350) is safe.

## Phase 7 — Publish

Three calls, always in this order:

```
POST /{ig-user-id}/media          → creation_id
     reels:  media_type=REELS  video_url=…  caption=…
     images: image_url=…  caption=…        ← omit media_type entirely
GET  /{creation-id}?fields=status_code     poll until FINISHED
POST /{ig-user-id}/media_publish  creation_id=…  → media id
```

**Always poll.** A ~300KB 11-second reel took 24–55s to reach FINISHED. Publishing an unfinished container fails.

`media_publish` is the only irreversible step — everything before it is staging, and an unpublished container simply expires in 24h. **Use that**: build the container to prove the pipeline without posting anything.

## Phase 8 — Scheduling

Meta gives you nothing here, so the pattern is:

- **Queue** each post as a record: `{ caption, media_path, media_type, scheduled_at, approved, posted_at }`
- **Tick frequently** (e.g. every 15 min) and publish whatever is *due* — do **not** hardcode slot times in cron. Slots belong in the data, so changing the calendar is an edit, not a deploy.
- **Publish one per tick.** Quota is per-24h and the true limit is ambiguous.
- **Never rethrow on failure.** A scheduler retry after a successful `media_publish` **double-posts**. Record the error and move on.
- **Gate with a config flag**, not by pausing the scheduler job — a deploy re-provisions and re-enables paused jobs, silently resuming posting.

## Phase 9 — Token rotation

The token expires in 60 days. Without rotation, publishing works for two months and then fails silently — the worst failure shape for a scheduler.

```
GET https://graph.instagram.com/refresh_access_token
    ?grant_type=ig_refresh_token&access_token=<current>
```

Needs **only the token** — no app secret. Run weekly so several failures are survivable, and write the result as a new secret version.

> Refreshing **returns a new token and restarts the clock**. Any call to this endpoint whose result you discard has burned a rotation — which is why the bundled checker leaves it out unless you pass `--check-refresh`.

---

## Scripts

| Script | Purpose |
|---|---|
| `scripts/verify_publishing_setup.py` | Read-only end-to-end check of one brand's setup: secret readable, token valid, account type publishable, publishing quota reachable, bucket private. Never publishes and never prints the token. `--json` for CI. |

The checker holds itself to the rule above: the token reaches `curl` through a config file on **stdin**, never argv, so it stays out of `ps` on shared and CI machines. Hold anything you build to the same line.

```bash
python3 scripts/verify_publishing_setup.py --project <GCP_PROJECT> \
  [--secret IG_ACCESS_TOKEN] [--bucket <MEDIA_BUCKET>] [--check-refresh] [--json]
```

Exit codes: `0` all checks passed, `1` a check failed, `2` bad input. Safe to gate a deploy on.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| "Insufficient Developer Role" | IG account has no app role | Phase 3 — and **accept the invite in Instagram** |
| Only 2 permissions in Explorer | Use case not added | Phase 1 |
| "Can't see the token" | Masked behind **Show** | Use **Copy** |
| Login popup never appears | Opened as a popup outside the automation context | Complete it manually |
| Container 400s on an image | PNG, not JPEG | Convert (Phase 6) |
| Fails at `media_publish` only | Wrong IG user ID | Use the `/me` ID (Phase 5) |
| Worked for ~2 months, now silent | Token expired | Phase 9 |
| Posted twice | Rethrew an error; scheduler retried | Never rethrow (Phase 8) |
| Posting resumed after a deploy | Paused scheduler job re-enabled | Use a config flag (Phase 8) |

## What this does NOT solve

- **Facebook scheduling** — use Business Suite. Its **bulk uploader is reels-only and Facebook-only**; FB *photos* and all Instagram scheduling cannot go through it.
- **Stories, carousels, comments** — different endpoints.
- **Publishing to accounts you don't own** — that needs App Review and Business Verification.
- **Caption and content strategy** — use `/product-marketing`.

## Reuse checklist for a new brand

- [ ] IG Business + public + linked Page + admin (Phase 0)
- [ ] App created, Instagram use case added (Phase 1)
- [ ] `instagram_business_content_publish` = **Ready for testing** (Phase 2)
- [ ] Instagram Tester added **and accepted in the IG app** (Phase 3)
- [ ] Token in a secret store, never in chat/logs/args (Phase 4)
- [ ] `/me` returns BUSINESS; real IG user ID recorded (Phase 5)
- [ ] Private media bucket + signed URLs; JPEG for stills (Phase 6)
- [ ] One container built and *not* published, as a dry run (Phase 7)
- [ ] Queue + tick-and-publish-what's-due + config-flag gate (Phase 8)
- [ ] Weekly token rotation scheduled (Phase 9)
- [ ] `verify_publishing_setup.py` green against the brand's project
