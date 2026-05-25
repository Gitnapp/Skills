---
name: xcode-github-release
description: Step-by-step process for bumping a version in Xcode and publishing a GitHub Release manually in a typical macOS workspace environment.
---

# Xcode GitHub Release Skill

This skill documents the workflow for creating a new release of a macOS Xcode application, including bumping the marketing and project version codes, building the binary, and publishing the release using the GitHub CLI (`gh`).

## Prerequisites

1. The project must have a `.xcodeproj` or `.xcworkspace`.
2. Ensure you have the GitHub CLI (`gh`) installed and authenticated (`gh auth status`).
3. Xcode command line tools (`xcodebuild`) should be set up on the macOS instance.

## Step-by-Step Instructions

### Step 1: Bump the Application Version
1. Identify the `project.pbxproj` file, typically located at `<ProjectName>.xcodeproj/project.pbxproj`.
2. Locate the `MARKETING_VERSION` (e.g., `1.0.1`) and `CURRENT_PROJECT_VERSION` (the build number, e.g., `99`) variables inside `project.pbxproj`.
3. Use a tool (such as `sed` or Python scripting) to manually bump the `MARKETING_VERSION` (e.g., to `1.1.0`) and the `CURRENT_PROJECT_VERSION` securely. 

Example:
```bash
sed -i '' 's/MARKETING_VERSION = 1.0.1/MARKETING_VERSION = 1.1.0/g' <ProjectName>.xcodeproj/project.pbxproj
sed -i '' 's/CURRENT_PROJECT_VERSION = 99/CURRENT_PROJECT_VERSION = 100/g' <ProjectName>.xcodeproj/project.pbxproj
```

### Step 2: Commit the Version Bump
Commit and push the new version file changes to the git repository before creating the release tag.
```bash
git add <ProjectName>.xcodeproj/project.pbxproj
git commit -m "chore: bump version to 1.1.0"
git push origin HEAD
```

### Step 3: Compile the Target via Xcodebuild 
*(Note: If you are operating within a Sandbox or restricted environment preventing `xcodebuild` from accessing `DerivedData`, skip straight to **Step 5** or configure a CI/CD GitHub Action instead).*

Use `xcodebuild` to cleanly compile an optimized release build of the Mac application using the workspace schema.

```bash
xcodebuild -project <ProjectName>.xcodeproj \
  -scheme <TargetScheme> \
  -configuration Release \
  clean build \
  CONFIGURATION_BUILD_DIR=$(PWD)/build 
```

### Step 4: Archive the Application
Package the generated `.app` bundle from the `build` directory into a `.zip` archive suitable for an attached release binary.
```bash
cd build
zip -r <ProjectName>.zip <ProjectName>.app
cd ..
```

### Step 5: Publish the GitHub Release
Use the standard GitHub CLI tool (`gh`) to create a tag and a public release. Include the `.zip` archive from Step 4 if it succeeded.

With a binary:
```bash
gh release create 1.1.0 build/<ProjectName>.zip \
  --title "Version 1.1.0" \
  --notes "Release notes go here."
```

Without a binary (Source code only release):
```bash
gh release create 1.1.0 \
  --title "Version 1.1.0" \
  --notes "Source-only release notes go here."
```

## Potential Pitfalls
- **macOS Sandbox Mode / DerivedData Issues**: Running `xcodebuild` in restricted agent environments can frequently fail due to rigid permission constraints around Xcode's `DerivedData` cache directories. The system blocks file mode modifications or writes. In this case, attempting to generate a build folder locally within that sandbox will fail code compilation entirely. Resorting to a source-only Github release or delegating binary building directly to a `.github/workflows/` Action is the recommended resolution.
