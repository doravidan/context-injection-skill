# Example: Jenkins Pipeline Debugging with Context Injection

## Scenario

A DevOps engineer's Jenkins pipeline fails during the deployment stage. The build worked yesterday but fails today with a cryptic error.

---

## ❌ Without Context Injection

**Prompt:**
> My Jenkins pipeline is failing with "Error: Process completed with exit code 1" in the deploy stage. How do I fix it?

**AI Response:**
> Exit code 1 is a generic error. Here are common causes:
> 1. Check your script syntax
> 2. Verify environment variables
> 3. Look at the full console output
> 4. Make sure your credentials are correct
> ...

*A list of generic troubleshooting steps. The developer already tried all of these.*

---

## ✅ With Context Injection

**Prompt:**

```markdown
## Context

### Project
- **Name:** SAP Cloud Integration - CI/CD Pipeline
- **Stack:** SAP BTP Cloud Foundry, MTA build, Node.js 18 CAP application
- **Jenkins:** v2.426.1, running on internal SAP infrastructure
- **Deploy Target:** SAP BTP subaccount `prod-eu10`

### Pipeline Structure
```groovy
pipeline {
    agent { label 'btp-builder' }
    
    stages {
        stage('Build') {
            steps {
                sh 'npm ci'
                sh 'npx mbt build -t ./mta_archives'  // ✅ passes
            }
        }
        stage('Test') {
            steps {
                sh 'npm test'  // ✅ passes
            }
        }
        stage('Deploy') {
            steps {
                sh '''
                    cf login -a https://api.cf.eu10.hana.ondemand.com \
                        -u $CF_USER -p $CF_PASS -o $CF_ORG -s $CF_SPACE
                    cf deploy ./mta_archives/myapp_1.2.0.mtar \
                        -f --version-rule ALL
                '''
                // ❌ FAILS HERE
            }
        }
    }
}
```

### Error Log (from Jenkins console, last 30 lines)
```
[2026-02-09T14:32:15] Deploying multi-target app archive myapp_1.2.0.mtar
[2026-02-09T14:32:16] Uploading 1 of 1 done
[2026-02-09T14:32:18] Processing service "myapp-xsuaa"...
[2026-02-09T14:32:19] Processing service "myapp-dest"...
[2026-02-09T14:32:20] Processing service "myapp-hdi"...
[2026-02-09T14:32:45] Creating application "myapp-srv"...
[2026-02-09T14:33:01] Staging application "myapp-srv"...
[2026-02-09T14:34:12] Error staging application: 
    Buildpack "nodejs_buildpack" failed to stage: 
    None of the specified NodeJS versions (18.19.0) are available.
    Available versions: 18.19.1, 20.11.0, 20.11.1, 22.0.0
[2026-02-09T14:34:12] Process failed with exit code 1
ERROR: script returned exit code 1
```

### What Changed Recently
- **Yesterday (worked):** Last successful deploy was myapp_1.1.9
- **Today (fails):** SAP updated the Cloud Foundry buildpacks overnight (standard maintenance)
- **No code changes** between 1.1.9 and 1.2.0 deploy attempts (only version bump)

### Relevant Config Files

**mta.yaml (excerpt):**
```yaml
modules:
  - name: myapp-srv
    type: nodejs
    path: gen/srv
    parameters:
      buildpack: nodejs_buildpack
      memory: 256M
    properties:
      NODE_ENV: production
```

**package.json (excerpt):**
```json
{
  "name": "myapp",
  "engines": {
    "node": "18.19.0"
  }
}
```

### Constraints
- Cannot pin buildpack version (SAP-managed infrastructure)
- Must stay on Node.js 18.x (LTS) — not ready for 20.x yet
- Pipeline must not have downtime > 30 minutes (SLA)

---

## Task
1. Explain the root cause
2. Provide the fix (minimal change to unblock deployment)
3. Suggest a long-term solution to prevent this from recurring
```

**AI Response:**

### Root Cause

SAP updated the Cloud Foundry `nodejs_buildpack` overnight, which removed Node.js `18.19.0` from the available versions. Your `package.json` has `"node": "18.19.0"` (exact pinning), so the buildpack can't find a matching version and fails staging.

This is a **buildpack version rotation**, not a code issue.

### Immediate Fix (< 5 minutes)

Update `package.json` to use a semver range instead of an exact version:

```json
{
  "engines": {
    "node": "^18.19.0"
  }
}
```

The `^` prefix allows any compatible `18.x.x` version ≥ `18.19.0`. The buildpack will pick `18.19.1` (the closest available match).

**Alternatively**, if you want to pin to the exact available version:

```json
{
  "engines": {
    "node": "18.19.1"
  }
}
```

### Long-Term Solution

1. **Use semver ranges** — Always use `^18` or `>=18.19.0 <19` instead of exact versions
2. **Add a buildpack check stage** to your pipeline:
   ```groovy
   stage('Pre-Deploy Check') {
       steps {
           sh '''
               cf buildpacks | grep nodejs
               echo "Available Node versions will be validated at staging"
           '''
       }
   }
   ```
3. **Subscribe to SAP BTP release notes** for buildpack update notifications
4. **Add a Slack notification** on pipeline failure to reduce response time

---

## Key Takeaways

| Context Element | What It Enabled |
|----------------|-----------------|
| Full error log | AI immediately identified the buildpack version mismatch |
| `package.json` engines field | Root cause pinpointed to exact version pinning |
| "What changed recently" | Confirmed buildpack update as trigger, not code changes |
| Constraints (can't pin buildpack) | Solution respects SAP infrastructure limitations |
| SLA requirement | Prioritized quick fix before long-term solution |

**Without context:** Generic "check your logs" advice.
**With context:** Root cause identified, fix provided, deploy unblocked in 5 minutes.
