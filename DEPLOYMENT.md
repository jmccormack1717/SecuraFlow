# Deployment Guide

This guide explains how to configure deployment to Render with test-gated deployments.

## Current Setup

The project uses **GitHub Actions** for CI/CD and **Render** for hosting. The CI/CD pipeline includes:

1. **Backend Tests** - Runs pytest tests with coverage
2. **Frontend Tests** - Runs Vitest tests and builds the frontend
3. **Status Check** - Gates deployment when all tests pass

## Test-Gated Deployment

Deployments to Render are now **gated behind passing tests**. This ensures that:
- ✅ Broken code never reaches production
- ✅ All tests must pass before deployment
- ✅ Better production reliability

## Configuring Render to Wait for Tests

To enable test-gated deployment in Render:

### Step 1: Verify Status Check in GitHub

After you push to the repository, check that the "All Tests Pass" status check appears:
1. Go to your GitHub repository
2. Click on a commit or pull request
3. You should see a status check named **"All Tests Pass"**

The status check will only appear on pushes to `main` or `develop` branches (not on pull requests).

### Step 2: Configure Render to Wait for Status Check

1. Log in to [Render Dashboard](https://dashboard.render.com)

2. For each service (Backend and Frontend):
   - Go to your service settings
   - Navigate to **"Settings"** → **"Build & Deploy"** section
   - Find **"Wait for a status check to pass"** option
   - Enable it
   - Enter the status check name: **`All Tests Pass`**
   - Save changes

3. **Important**: You need to do this for both:
   - Backend service
   - Frontend service

### Step 3: Test It Out

1. Make a small change and push to `main` branch
2. Watch GitHub Actions - tests will run first
3. Once all tests pass, the "All Tests Pass" status check will appear
4. Render will then automatically start deploying

If tests fail, Render will **not** deploy, protecting your production environment.

## How It Works

```
Push to main/develop
    ↓
GitHub Actions runs tests
    ↓
[If tests pass] → "All Tests Pass" status check ✅
    ↓
Render sees status check passed
    ↓
Render deploys automatically 🚀

[If tests fail] → Status check fails ❌
    ↓
Render does NOT deploy (stays on previous version)
```

## Troubleshooting

### Status check not appearing?

- Make sure you're pushing to `main` or `develop` branch
- Check that the GitHub Actions workflow ran successfully
- Verify the workflow file `.github/workflows/ci.yml` exists and is correct

### Render not waiting for status check?

- Verify the status check name in Render matches exactly: `All Tests Pass`
- Make sure you enabled "Wait for a status check to pass" in Render settings
- Check that Render has permission to read GitHub status checks (usually automatic with GitHub integration)

### Tests passing but deployment not triggering?

- Check Render service logs for any errors
- Verify Render's GitHub integration is properly connected
- Ensure the branch in Render matches your deployment branch (`main`)

## Manual Deployment

If you need to deploy manually (bypassing tests):

1. Go to Render dashboard
2. Click "Manual Deploy" on your service
3. Select the commit you want to deploy

**Note**: Manual deployments bypass the status check. Use only when necessary.

## CI/CD Pipeline Details

The GitHub Actions workflow (`.github/workflows/ci.yml`) includes:

- **Parallel Test Jobs**: Backend and frontend tests run simultaneously
- **Status Check Job**: Only runs on pushes (not PRs) to gate deployment
- **Test Coverage**: Backend tests include coverage reporting
- **Build Verification**: Frontend build is verified before deployment

For more details, see the workflow file or GitHub Actions logs.


