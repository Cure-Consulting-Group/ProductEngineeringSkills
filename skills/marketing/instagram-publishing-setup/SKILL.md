---
name: instagram-publishing-setup
description: "Use when posting to Instagram from code: Meta app, business portfolio, token, exact-time scheduling, media hosting — or stuck on Insufficient Developer Role, an account missing from the token picker, or a media_publish 400."
when_to_use: "NOT for captions or content strategy (product-marketing), Stories, carousels, or accounts you don't own."
argument-hint: "[brand-name] [gcp-project-id]"
metadata:
  verified: 2026-11-07
---

# Instagram Publishing Setup

Stand up **programmatic Instagram publishing for one brand**, end to end: Meta developer app → business portfolio → permissions → token → media hosting → publishing at an exact time.

Written from two real setups. The first, on 2026-09-23, used the old "Instagram login" screen. The second, for HoopTrace on 2026-11-07, found that screen gone and the flow changed. Every trap below cost time, and none of them are in Meta's docs in a form you'd find before hitting them. Done when the reuse checklist at the bottom is all ticked and the bundled checker is green.

**API version.** Examples use `v26.0`. Keep the version in one variable (`IG_GRAPH_VERSION` for the checker) and check the [changelog](https://developers.facebook.com/docs/graph-api/changelog) before pinning a new integration.

## When to use this

- A brand needs to publish to Instagram from code (reels, images, articles-as-graphics)
- Someone is stuck on **"Insufficient Developer Role"**, an Instagram account missing from the token popup, a token that seems invisible, or a publish that 400s with an unhelpful message
- You want scheduled Instagram posts, which Meta does **not** provide

## The four things to know before starting

1. **The Content Publishing API is free.** There is no paid tier for posting to your own Instagram Business account.
2. **There is no scheduling parameter.** `media_publish` goes live the instant it is called, so the timing has to come from you (Phase 8). Business Suite can schedule *Facebook*, not Instagram.
3. **Development mode is enough** for your *own* account. You need no App Review and no Business Verification.
4. **Which host you call depends on the token.** An `EAA…` token (Facebook Login for Business, what new apps get) goes to `graph.facebook.com`. An `IGAA…` token (the older Instagram-login flow) goes to `graph.instagram.com`. Sending a token to the wrong host fails as an "invalid token", which looks like a revoked credential.

---

## Phase 0 — Prerequisites

| Requirement | How to check | If wrong |
|---|---|---|
| Instagram is **Business or Creator**, not Personal | IG app → Settings → Account type | Switch to Professional |
| Instagram account is **public** | Settings → Privacy | Tokens cannot be generated for private accounts |
| You are **admin** of the Meta developer account | developers.facebook.com/apps loads | Get added |

A linked Facebook Page is **no longer required** on the Unified-login route (Phase 2). The account must be in a business portfolio instead.

## Phase 1 — Meta app with the Instagram use case

1. <https://developers.facebook.com/apps> → **Create app**
2. Name it (e.g. "<Brand> Publisher"). The contact email defaults to the account's; it can be changed later in App settings → Basic.
3. Use cases → filter **Content management** → **Manage messaging & content on Instagram**
4. **Business portfolio:** pick the brand's own, or "I don't want to connect a business portfolio yet". You will need one in Phase 2 either way. One portfolio per brand keeps assets separate.
5. **Create app** agrees to the Meta Platform Terms, so the human approves it. Meta then asks for the **Facebook password again**; the human types it.

Record the **App ID**. App status stays **Unpublished / development**, which is correct and sufficient.

## Phase 2 — Permissions, portfolio, and the account inside it

### 2a. Permissions

Use case → **Customize** → **Permissions and features** → **Add** on:

- `instagram_business_basic`
- `instagram_business_content_publish`

> ### ✅ The checkpoint that decides everything
> `instagram_business_content_publish` must read **"Ready for testing."** That status means publishing works for your own account with **no App Review**.

### 2b. Business portfolio (required)

> ### ⚠️ "API setup with Instagram login is not available for newer apps"
> Apps created after mid-2026 offer only **API setup with Unified login**, which is recommended and the only route getting new features. The alternative is **API setup with Facebook login**, which is legacy and needs a linked Facebook Page. Unified login says **"Business portfolio selection is mandatory."**

Unified login tab → **+ Business portfolio** → select the brand's portfolio, or **Create a new business portfolio** with the name, the owner's name and a business email. **Verify later** is fine for your own account.

### 2c. Put the Instagram account IN the portfolio and assign yourself

> ### ⚠️ The second place setups fail
> Symptom: the token popup's **Instagram Account** list shows every *other* brand's account but not this one.
> Cause: the account isn't owned by the selected portfolio, or no person is assigned to it there.

1. `business.facebook.com/latest/settings/instagram_account?business_id=<portfolio id>` → **Add** → **Add Instagram account**. It logs into Instagram; if the browser is already signed in as the brand, it completes on its own. The account then shows **Owned by: <portfolio>**.
2. Select the account → **Assign people** → yourself → **Full control (Everything)** → **Assign**.

## Phase 3 — Instagram Tester role

> ### ⚠️ Symptom: **"Insufficient Developer Role."**
> Cause: the *Instagram account* has no role on the app. Being the app admin is not enough.

1. App → **App roles → Roles** → **Add People** → **Instagram Tester** → type the IG username → pick it → **Add**. It shows **Pending**.
2. **Accept from the Instagram side** while signed in as the brand account. On web it's `instagram.com/accounts/manage_access/` → **Tester Invites** → **Accept**; in the app it's Settings → Apps and websites → Tester invites. Accepting agrees to Meta's terms, so the human approves it.

Check *which* account the browser is signed into first. The tab is per-account.

## Phase 4 — Token

Unified login tab:

1. **1. Configure your app** → **Create new configuration** → **Create from template**. The template issues a **System-User Access Token that never expires**. It also requests `ads_management`/`ads_read`; grant **no ad account** in the popup and those permissions can touch nothing.
2. **2. Generate access tokens** → the account row → **Generate token**. Without a configuration this fails with "Select a configuration in Step 1".
3. A **popup window** opens. Browser automation usually can't reach it, so the human clicks through: portfolio → the Instagram account → no ad accounts → approve.
4. The dashboard shows **Token generated**, and Meta shows the token **only once**. Tick **I understand** → **Copy**.

> ### 🔒 Never paste a token into a chat, a commit, a log, or a command argument
> Create the container empty first, then pipe the token straight from the clipboard and clear it:
> ```bash
> gcloud secrets create IG_ACCESS_TOKEN --replication-policy=automatic --project=<PROJECT_ID>
> pbpaste | tr -d '\n' | gcloud secrets versions add IG_ACCESS_TOKEN --project=<PROJECT_ID> --data-file=- && printf '' | pbcopy
> ```
> To confirm the clipboard holds a token without printing it: `t="$(pbpaste)"; echo "${#t} ${t:0:4}"; unset t`. A token is about 270 characters and starts with `EAA`.

## Phase 5 — Verify, and record the IG user id

With an `EAA…` token, `/me` returns the **system user** ("<App> System User"), not the Instagram account. Use the IG user id shown under the account on the token row (`1784…`) and query it directly:

```bash
TOKEN="$(gcloud secrets versions access latest --secret=IG_ACCESS_TOKEN --project=<PROJECT_ID>)"
q(){ printf 'header = "Authorization: Bearer %s"\n' "$TOKEN" | curl -s -K - "\$1"; echo; }
q "https://graph.facebook.com/v26.0/<IG_USER_ID>?fields=id,username,followers_count,media_count"
q "https://graph.facebook.com/v26.0/<IG_USER_ID>/content_publishing_limit?fields=quota_usage,config"
unset TOKEN
```

The token reaches curl through a config file on stdin, never argv. Docs say 100 posts per 24 h and third parties say 25; **trust `content_publishing_limit`**. It read `0/100 per 86400s` on 2026-11-07.

Or run the bundled checker, which does all of the above read-only and never prints the token:

```bash
python3 <skill-dir>/scripts/verify_publishing_setup.py --project <GCP_PROJECT> --ig-user-id <IG_USER_ID> --bucket <MEDIA_BUCKET>
```

## Phase 6 — Media hosting

Instagram fetches `video_url` / `image_url` **itself**, at container-creation time only.

- Keep media in a **private** bucket and hand over a **short-lived signed URL** (an hour is plenty). Nothing needs to be world-readable.
- The signing identity needs `roles/iam.serviceAccountTokenCreator` **on itself**, plus read on the bucket.

> ### ⚠️ Instagram accepts **JPEG only** for images
> PNG fails at container creation with an error that never mentions the format. Refuse PNG at queue time and convert:
> ```bash
> sips -s format jpeg -s formatOptions 90 card.png --out card.jpg   # macOS
> magick card.png -quality 90 card.jpg                             # Linux/any (ImageMagick 7)
> ```

Format rules: reels are 9:16 MP4; feed images are JPEG, and 4:5 (1080×1350) is safe.

## Phase 7 — Publish

Three calls, always in this order. Send the token in the **Authorization header**, never in a query string:

```
POST /{ig-user-id}/media          → creation_id
     reels:  media_type=REELS  video_url=…  caption=…
     images: image_url=…  caption=…        ← omit media_type entirely
GET  /{creation-id}?fields=status_code     poll until FINISHED (ERROR/EXPIRED = stop)
POST /{ig-user-id}/media_publish  creation_id=…  → media id
```

**Always poll.** A ~300 KB 11-second reel took 24–55 s to reach FINISHED. Publishing an unfinished container fails.

`media_publish` is the only irreversible step. Everything before it is staging, and an unpublished container expires on its own after 24 h. **Use that for a dry-run mode**: build the container and stop.

## Phase 8 — Scheduling: exact time, no polling

Meta gives you nothing here. **Don't run a cron tick** (every 15 minutes is 96 runs a day to post a few times a week). Schedule each post for its exact time:

- **Queue** each post as a record: `{ caption, mediaPath, mediaType, scheduledAtMs, status, dryRun? }`, server only.
- **Approving** a post enqueues **one Cloud Task** for `scheduledAtMs` (Firebase: an `onDocumentWritten` trigger plus `getFunctions().taskQueue(...)`). Use the task id `<postId>-<scheduledAtMs>`, so a duplicate enqueue is a no-op (`functions/task-already-exists`) and a reschedule gets a fresh task. When the old task fires, it sees a different time on the post and does nothing.
- **Cloud Tasks caps scheduleTime at 30 days.** Enqueue at 29 days out; when that task fires early, it re-enqueues itself ("hops").
- **One attempt, never retried** (`retryConfig: { maxAttempts: 1 }`), and the handler never throws. A retry after a successful `media_publish` **double-posts**, and the API has no idempotency key. Record the error on the post and count it.
- **Claim before calling Meta.** A transaction moves `scheduled → publishing` first, so two deliveries can't both publish. Once `media_publish` returns, record `published` even if bookkeeping after it fails.
- **Gate with a config flag read on every fire**, not by pausing anything. When it's off, park due posts as `held` and require re-approval, so turning it back on never posts a backlog by surprise. Keep it off in dev, with a placeholder token.
- **IAM:** the runtime SA needs `roles/cloudtasks.enqueuer`, plus `roles/iam.serviceAccountUser` **on itself** (the task's OIDC token is minted for it). Enable `cloudtasks.googleapis.com`.
- **Count every outcome** (published / failed / held / dry run) somewhere durable that the owner reads, not just in log lines.

Worked example: HoopTrace `backend/functions/src/social/` (STORY-1996, ADR-0056).

## Phase 9 — Token lifetime

- **System-User token from a Unified-login configuration (`EAA…`): never expires.** There's nothing to rotate. It stops working only if the system user or its access is removed in the portfolio, which shows up as a failed publish. Make sure failures are counted and visible.
- **Instagram-login token (`IGAA…`, older apps): 60 days.** Refresh it weekly with `GET https://graph.instagram.com/refresh_access_token?grant_type=ig_refresh_token&access_token=<current>` and store the result as a new secret version. A refresh whose result you discard has burned a rotation.

---

## Scripts

`<skill-dir>` is the directory containing this SKILL.md (in Claude Code: `${CLAUDE_PLUGIN_ROOT}/skills/marketing/instagram-publishing-setup`).

| Script | Purpose |
|---|---|
| `scripts/verify_publishing_setup.py` | Read-only end-to-end check: secret readable; token valid on the right host (`EAA` → graph.facebook.com, needs `--ig-user-id`; otherwise graph.instagram.com `/me`); account reachable; quota answers; bucket private. Never publishes and never prints the token. `--json` for CI. |

The checker follows the same rule as Phase 4: the token reaches `curl` through a config file on **stdin**, never argv, and error text is redacted before printing.

```bash
python3 <skill-dir>/scripts/verify_publishing_setup.py --project <GCP_PROJECT> \
  [--secret IG_ACCESS_TOKEN] [--ig-user-id <IG_USER_ID>] [--bucket <MEDIA_BUCKET>] [--check-refresh] [--json]
```

Exit codes: `0` all checks passed, `1` a check failed, `2` bad input. Safe to gate a deploy on.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| No "Instagram login" option | Removed for newer apps | Unified login (Phase 2b) |
| "Business portfolio selection is mandatory" | Unified login needs one | Phase 2b |
| Account missing from the token popup | Not owned by the portfolio, or nobody assigned | Phase 2c |
| "Select a configuration in Step 1" | No login configuration | Phase 4 step 1 |
| "Insufficient Developer Role" | IG account has no app role | Phase 3, and **accept the invite in Instagram** |
| Tester invite not visible | Browser signed into a different IG account | Switch accounts, then reopen Tester Invites |
| Popup never appears | Opened outside the automation context, or blocked | The human completes it; allow popups |
| "Invalid OAuth access token" on a fresh token | `EAA` token sent to graph.instagram.com, or the reverse | Match the host to the token (rule 4) |
| `/me` has no username | `EAA` system-user token | Query `/<IG_USER_ID>` instead (Phase 5) |
| Container 400s on an image | PNG, not JPEG | Convert (Phase 6) |
| Fails at `media_publish` only | Wrong IG user id | Use the `1784…` id from the token row |
| Posted twice | A retry after a successful publish | One attempt, never rethrow (Phase 8) |
| Posting resumed by surprise | A backlog published when the gate reopened | Hold due posts, require re-approval (Phase 8) |
| Instagram-login token stopped after ~2 months | 60-day expiry | Phase 9 |

## What this does NOT solve

- **Facebook scheduling**: use Business Suite.
- **Stories, carousels, comments**: different endpoints.
- **Publishing to accounts you don't own**: needs App Review and Business Verification.
- **Caption and content strategy**: use the product-marketing skill.

## Reuse checklist for a new brand

- [ ] IG Business/Creator + public (Phase 0)
- [ ] App created with the Instagram use case; App ID recorded (Phase 1)
- [ ] `instagram_business_content_publish` = **Ready for testing** (Phase 2a)
- [ ] Brand portfolio connected to the app (Phase 2b)
- [ ] IG account **owned by** that portfolio and a person assigned (Phase 2c)
- [ ] Instagram Tester added **and accepted on the Instagram side** (Phase 3)
- [ ] Login configuration created; token generated and piped into the secret store, never shown (Phase 4)
- [ ] Account and quota read back on the right host; IG user id recorded (Phase 5)
- [ ] Private media bucket + signed URLs; JPEG for stills (Phase 6)
- [ ] One dry-run container built and *not* published (Phase 7)
- [ ] Exact-time queue: one task per post, one attempt, claim first, gate flag, counted outcomes (Phase 8)
- [ ] Token lifetime understood: never-expiring SUAT, or weekly refresh for `IGAA` (Phase 9)
- [ ] `verify_publishing_setup.py` green against the brand's project
