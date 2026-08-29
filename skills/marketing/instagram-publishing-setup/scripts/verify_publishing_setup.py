#!/usr/bin/env python3
"""Verify one brand's Instagram programmatic-publishing setup, read-only.

Checks that the access token is stored and valid, that the account can publish,
that the publishing-quota endpoint answers (which is what proves
instagram_business_content_publish was actually granted), and optionally that
the media bucket is private. It never publishes and never prints the token.

Usage:
  python3 verify_publishing_setup.py --project my-gcp-project
  python3 verify_publishing_setup.py --project my-gcp-project --bucket my-media --json
  python3 verify_publishing_setup.py --project my-gcp-project --check-refresh

Exit codes: 0 all checks passed, 1 a check failed, 2 bad input.
"""
import argparse
import json
import shutil
import subprocess
import sys
import urllib.parse

GRAPH = "https://graph.instagram.com/v23.0"
REFRESH_URL = "https://graph.instagram.com/refresh_access_token"
TIMEOUT = 20

GREEN, RED, DIM, RESET = "\033[32m", "\033[31m", "\033[2m", "\033[0m"


class CheckFailed(Exception):
    """A hard failure that should stop the run."""


def run(cmd, stdin_text=None):
    """Run a command, returning (rc, stdout). Never raises on non-zero exit."""
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=60,
                           input=stdin_text)
        return p.returncode, p.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return 1, ""


def curl_quote(value):
    """Quote a value for a curl config file (double-quoted, backslash-escaped)."""
    return '"%s"' % value.replace("\\", "\\\\").replace('"', '\\"')


def redact(text, secret):
    """Strip a secret out of text before it can reach stdout or a log.

    Error text is built from the response body, and the refresh endpoint
    carries the token in its query string — so an API that echoes the request
    back would otherwise print the token. Redact before truncating, or a
    partial token survives at the cut.
    """
    if secret and text:
        return text.replace(secret, "***REDACTED***")
    return text


def get_json(url, token=None, secret_value=None):
    """GET a URL with curl and parse JSON. Returns (data, error_text).

    curl rather than urllib: it uses the system trust store, so this keeps
    working on laptops whose Python was installed without a CA bundle.

    The URL and any token go to curl through a config file on stdin, never
    argv: a token in a command argument is readable by any user via `ps`,
    which is the exposure this skill tells you to avoid everywhere else.

    Error text is redacted, so a returned message is always safe to print.
    """
    secret_value = secret_value or token
    if not shutil.which("curl"):
        return None, "curl not found on PATH"
    config = [
        "url = " + curl_quote(url),
        "silent",
        "show-error",
        "max-time = %d" % TIMEOUT,
        'write-out = "\\n%{http_code}"',
    ]
    if token:
        config.append("header = " + curl_quote("Authorization: Bearer " + token))
    rc, out = run(["curl", "-K", "-"], stdin_text="\n".join(config) + "\n")
    if rc != 0 or not out:
        return None, "network error (curl exit %s)" % rc
    body, _, code = out.rpartition("\n")
    try:
        data = json.loads(body)
    except ValueError:
        safe = redact(body, secret_value)
        return None, "HTTP %s — response was not JSON: %s" % (code, safe[:200])
    if code and not code.startswith("2"):
        return None, "HTTP %s %s" % (code, redact(body, secret_value)[:300])
    return data, None


def check_token(project, secret):
    rc, token = run(["gcloud", "secrets", "versions", "access", "latest",
                     "--secret", secret, "--project", project])
    if rc != 0 or not token:
        raise CheckFailed(
            "could not read secret '%s' in project '%s'" % (secret, project))
    return token


def check_account(token):
    data, err = get_json(GRAPH + "/me?fields=id,username,account_type", token)
    if data is None or not data.get("id"):
        raise CheckFailed("token rejected — %s" % (err or "no id in response"))
    acct = data.get("account_type", "")
    if acct not in ("BUSINESS", "MEDIA_CREATOR"):
        raise CheckFailed("account type '%s' cannot publish — switch to Business/Creator" % acct)
    return data, "@%s · id %s · %s" % (data.get("username", "?"), data["id"], acct)


def check_quota(token, ig_id):
    data, err = get_json("%s/%s/content_publishing_limit" % (GRAPH, ig_id), token)
    used = None
    if data:
        try:
            used = data["data"][0].get("quota_usage")
        except (KeyError, IndexError, TypeError):
            used = None
    if used is None:
        raise CheckFailed(
            "content_publishing_limit unavailable — instagram_business_content_publish "
            "likely not granted (%s)" % (err or "unexpected response shape"))
    return used, "quota endpoint answers — %s posts used in the last 24h" % used


def check_refresh(token):
    """Opt-in: consumes a refresh and returns a NEW token, invalidating the clock."""
    url = REFRESH_URL + "?" + urllib.parse.urlencode(
        {"grant_type": "ig_refresh_token", "access_token": token})
    data, err = get_json(url, secret_value=token)
    secs = (data or {}).get("expires_in", 0)
    try:
        secs = int(secs)
    except (TypeError, ValueError):
        secs = 0
    if secs <= 0:
        raise CheckFailed("refresh refused — token may be short-lived or expired (%s)"
                          % (err or "no expires_in"))
    return secs, "long-lived — refresh returns %d days" % (secs // 86400)


def check_bucket(project, bucket):
    rc, _ = run(["gcloud", "storage", "buckets", "describe", "gs://" + bucket,
                 "--project", project])
    if rc != 0:
        raise CheckFailed("gs://%s not reachable" % bucket)
    rc, out = run(["gcloud", "storage", "buckets", "get-iam-policy", "gs://" + bucket,
                   "--project", project, "--format", "json"])
    public = False
    if rc == 0 and out:
        try:
            policy = json.loads(out)
            public = any("allUsers" in b.get("members", [])
                         for b in policy.get("bindings", []))
        except ValueError:
            public = False
    if public:
        raise CheckFailed("gs://%s is PUBLIC — prefer private + short-lived signed URLs" % bucket)
    return "gs://%s reachable and private (signed URLs only)" % bucket


def main():
    ap = argparse.ArgumentParser(
        description="Read-only verification of a brand's Instagram publishing setup. "
                    "Never publishes; never prints the token.")
    ap.add_argument("--project", required=True, help="GCP project holding the token secret")
    ap.add_argument("--secret", default="IG_ACCESS_TOKEN",
                    help="Secret Manager secret name (default: IG_ACCESS_TOKEN)")
    ap.add_argument("--bucket", help="Media bucket to check for private access (optional)")
    ap.add_argument("--check-refresh", action="store_true",
                    help="Also verify token lifetime. WARNING: this CONSUMES a refresh and "
                         "issues a new token — store the result or the old one keeps its clock.")
    ap.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = ap.parse_args()

    results = []
    notes = []

    def record(name, ok, detail):
        results.append({"check": name, "status": "pass" if ok else "fail", "detail": detail})

    try:
        token = check_token(args.project, args.secret)
        record("token_stored", True, "secret '%s' readable (%d chars, value not shown)"
               % (args.secret, len(token)))

        me, detail = check_account(token)
        record("account", True, detail)
        notes.append("use IG user id %s for publishing — not the id shown on the app setup page"
                     % me["id"])

        used, detail = check_quota(token, me["id"])
        record("publishing_quota", True, detail)
        notes.append("docs say 100/24h, third parties say 25; this endpoint is the truth")

        if args.check_refresh:
            _, detail = check_refresh(token)
            record("token_lifetime", True, detail)
            notes.append("a refresh was consumed — store the new token to restart the 60-day clock")
        else:
            results.append({"check": "token_lifetime", "status": "skip",
                            "detail": "not checked — pass --check-refresh (consumes a refresh)"})

        if args.bucket:
            record("media_bucket", True, check_bucket(args.project, args.bucket))
        else:
            results.append({"check": "media_bucket", "status": "skip",
                            "detail": "no --bucket given"})
    except CheckFailed as e:
        results.append({"check": "failed", "status": "fail", "detail": str(e.args[0])})

    failed = [r for r in results if r["status"] == "fail"]

    if args.json:
        print(json.dumps({"project": args.project, "ok": not failed,
                          "checks": results, "notes": notes}, indent=2))
    else:
        print("Instagram publishing setup — project: %s\n" % args.project)
        for r in results:
            mark = {"pass": GREEN + "✓" + RESET, "fail": RED + "✗" + RESET, "skip": DIM + "–" + RESET}[r["status"]]
            print("  %s %s: %s" % (mark, r["check"], r["detail"]))
        for n in notes:
            print("    %s%s%s" % (DIM, n, RESET))
        print()
        print("Ready to publish. Reminder: media_publish is immediate — scheduling is yours to build."
              if not failed else "Setup incomplete — fix the ✗ above.")

    return 1 if failed else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(2)
