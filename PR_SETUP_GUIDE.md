# Step-by-Step Guide: Setting Up the Pull Request

## Prerequisites

1. **GitHub Account**: Make sure you have a GitHub account
2. **Git Installed**: Ensure Git is installed on your system
3. **Fork the Repository**: Go to https://github.com/allin-love/zosapi_autoopt and click "Fork"

## Step 1: Clone Your Fork

```bash
# Replace 'yourusername' with your actual GitHub username
git clone https://github.com/yourusername/zosapi_autoopt.git
cd zosapi_autoopt
```

## Step 2: Set Up Remote Upstream

```bash
# Add the original repository as upstream
git remote add upstream https://github.com/allin-love/zosapi_autoopt.git
git remote -v  # Verify remotes are set up correctly
```

## Step 3: Create a New Branch

```bash
# Create and switch to a new branch for your fix
git checkout -b fix-getcellat-compatibility
```

## Step 4: Copy Your Fixed Files

Copy the following files from your current working directory to the cloned repository:

1. **Copy the fixed `zosapi_lde.py`**:
   ```bash
   # From: d:\neurolabware Dropbox\Zhang Yuanlong\Benchmark\Optics_related\zosapi_autoopt-main\zosapi_autoopt-main\zosapi_autoopt\zosapi_lde.py
   # To: ./zosapi_autoopt/zosapi_lde.py
   ```

## Step 5: Verify Your Changes

```bash
# Check what files have been modified
git status

# Review the specific changes
git diff zosapi_autoopt/zosapi_lde.py
```

You should see the changes in the `_get_cell` method around line 947.

## Step 6: Commit Your Changes

```bash
# Stage the modified file
git add zosapi_autoopt/zosapi_lde.py

# Commit with a clear message
git commit -m "Fix TypeError in _get_cell method for GetCellAt API compatibility

- Convert SurfaceColumn enum to integer for GetCellAt calls
- Add fallback mechanism for backward compatibility  
- Fixes solver methods: set_substitute_solve, set_pickup_solve, etc.
- Resolves TypeError: No method matches given arguments for GetCellAt"
```

## Step 7: Push to Your Fork

```bash
# Push the branch to your fork
git push origin fix-getcellat-compatibility
```

## Step 8: Create Pull Request on GitHub

1. **Go to your fork** on GitHub: `https://github.com/yourusername/zosapi_autoopt`

2. **Click "Compare & pull request"** button (should appear after pushing)

3. **Fill out the PR form**:
   - **Title**: `Fix TypeError in _get_cell method for GetCellAt API compatibility`
   - **Description**: Copy the content from `PULL_REQUEST_TEMPLATE.md` (created above)

4. **Review your changes** in the "Files changed" tab

5. **Click "Create pull request"**

## Step 9: Files to Include in PR Description

Make sure to reference:
- The specific error message and stack trace
- The example script that reproduces the issue (`examples/3p_smartphone.py`)
- The solution approach (enum to integer conversion)
- Backward compatibility considerations

## Step 10: Follow Up

After creating the PR:
1. **Monitor for feedback** from maintainers
2. **Be ready to make changes** if requested
3. **Test thoroughly** if asked
4. **Respond promptly** to questions

## Quick Command Summary

Here's the complete sequence of commands:

```bash
# 1. Fork the repo on GitHub first, then:
git clone https://github.com/yourusername/zosapi_autoopt.git
cd zosapi_autoopt
git remote add upstream https://github.com/allin-love/zosapi_autoopt.git

# 2. Create branch and make changes
git checkout -b fix-getcellat-compatibility
# [Copy your fixed zosapi_lde.py file here]

# 3. Commit and push
git add zosapi_autoopt/zosapi_lde.py
git commit -m "Fix TypeError in _get_cell method for GetCellAt API compatibility"
git push origin fix-getcellat-compatibility

# 4. Create PR on GitHub web interface
```

## Important Notes

1. **Test Before Submitting**: Make sure your fix actually works
2. **Follow Coding Standards**: Ensure your code follows the project's style
3. **Write Clear Commit Messages**: Use descriptive commit messages
4. **Be Patient**: Maintainers may take time to review
5. **Be Collaborative**: Be open to feedback and suggestions

## Expected Files in Your PR

Your pull request should modify only one file:
- `zosapi_autoopt/zosapi_lde.py` (the `_get_cell` method fix)

## Troubleshooting

**If you can't push to upstream**: Make sure you're pushing to your fork (`origin`), not the upstream repository.

**If the PR shows too many changes**: Make sure you branched from the latest upstream code.

**If tests fail**: The maintainer will guide you on fixing any test issues.
