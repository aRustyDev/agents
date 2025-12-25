# Mobile CI GitHub Apps

GitHub Apps specialized for mobile application continuous integration: iOS/Android builds, device testing, app signing, and distribution.

## Common Use Cases

- **iOS Builds** - Xcode builds with code signing
- **Android Builds** - Gradle builds with keystore signing
- **Device Testing** - Real device and emulator testing
- **Beta Distribution** - TestFlight, Firebase App Distribution
- **App Store Deployment** - Automated releases
- **Screenshot Generation** - Multi-device screenshots

## Key Webhooks

| Webhook | Use Case |
|---------|----------|
| `push` | Trigger builds |
| `pull_request.*` | PR builds and tests |
| `release.published` | App store deployment |
| `workflow_run.completed` | Post-build processing |
| `check_run.rerequested` | Re-run builds |

## Recommended Permissions

| Permission | Level | Purpose |
|------------|-------|---------|
| Contents | Read | Clone repository |
| Checks | Write | Report build status |
| Statuses | Write | Set commit status |
| Actions | Write | Trigger workflows |
| Pull requests | Read | Access PR info |

### Minimal Permission Set
```yaml
permissions:
  contents: read
  checks: write
```

## Common Patterns

### iOS Build Pipeline

```typescript
app.on("push", async (context) => {
  const { after, ref, repository } = context.payload;

  // Detect if iOS project
  const hasXcodeProject = await fileExists(context, "*.xcodeproj", after)
    || await fileExists(context, "*.xcworkspace", after);

  if (!hasXcodeProject) return;

  // Create check run
  const { data: check } = await context.octokit.checks.create(
    context.repo({
      name: "iOS Build",
      head_sha: after,
      status: "in_progress",
    })
  );

  try {
    // Dispatch to macOS runner
    const build = await dispatchIOSBuild({
      repo: repository.clone_url,
      sha: after,
      ref,
      checkRunId: check.id,
      config: {
        scheme: await detectScheme(context, after),
        destination: "platform=iOS Simulator,name=iPhone 15",
        buildForTesting: true,
      },
    });

    await context.octokit.checks.update(
      context.repo({
        check_run_id: check.id,
        details_url: build.logsUrl,
        external_id: build.id,
      })
    );
  } catch (error) {
    await context.octokit.checks.update(
      context.repo({
        check_run_id: check.id,
        status: "completed",
        conclusion: "failure",
        output: {
          title: "Build Failed",
          summary: error.message,
        },
      })
    );
  }
});

async function detectScheme(context, sha: string): Promise<string> {
  // Read xcodeproj or xcworkspace to find schemes
  const projectFile = await findFile(context, "*.xcodeproj/project.pbxproj", sha);

  if (projectFile) {
    const content = await getFileContent(context, projectFile, sha);
    // Parse pbxproj to find schemes
    // This is simplified - real implementation needs xcodeproj parsing
    return extractMainScheme(content);
  }

  return "App"; // Default scheme name
}
```

### Android Build Pipeline

```typescript
app.on("push", async (context) => {
  const { after, ref, repository } = context.payload;

  // Detect if Android project
  const hasGradle = await fileExists(context, "build.gradle", after)
    || await fileExists(context, "build.gradle.kts", after);

  if (!hasGradle) return;

  const { data: check } = await context.octokit.checks.create(
    context.repo({
      name: "Android Build",
      head_sha: after,
      status: "in_progress",
    })
  );

  try {
    const build = await dispatchAndroidBuild({
      repo: repository.clone_url,
      sha: after,
      ref,
      checkRunId: check.id,
      config: {
        tasks: ["assembleDebug", "testDebugUnitTest"],
        gradleVersion: await detectGradleVersion(context, after),
      },
    });

    // Report success with APK artifacts
    await context.octokit.checks.update(
      context.repo({
        check_run_id: check.id,
        details_url: build.logsUrl,
        output: {
          title: "Build Complete",
          summary: `APK: [Download](${build.artifactUrl})`,
        },
      })
    );
  } catch (error) {
    await handleBuildFailure(context, check.id, error);
  }
});
```

### Code Signing Management

```typescript
interface CodeSigningConfig {
  platform: "ios" | "android";
  type: "development" | "distribution";
  teamId?: string;
  bundleId?: string;
  keystoreAlias?: string;
}

async function setupCodeSigning(config: CodeSigningConfig) {
  if (config.platform === "ios") {
    return setupIOSCodeSigning(config);
  } else {
    return setupAndroidCodeSigning(config);
  }
}

async function setupIOSCodeSigning(config: CodeSigningConfig) {
  // Fetch certificates and provisioning profiles from secure storage
  const certificate = await secrets.get(`ios-cert-${config.type}`);
  const profile = await secrets.get(`ios-profile-${config.bundleId}-${config.type}`);

  // Install to keychain (on macOS runner)
  await exec(`security create-keychain -p "" build.keychain`);
  await exec(`security import ${certificate} -k build.keychain -P "" -T /usr/bin/codesign`);

  // Install provisioning profile
  await exec(`mkdir -p ~/Library/MobileDevice/Provisioning\\ Profiles`);
  await exec(`cp ${profile} ~/Library/MobileDevice/Provisioning\\ Profiles/`);

  return {
    keychain: "build.keychain",
    provisioningProfile: profile,
  };
}

async function setupAndroidCodeSigning(config: CodeSigningConfig) {
  // Fetch keystore from secure storage
  const keystore = await secrets.get(`android-keystore-${config.type}`);
  const keystorePassword = await secrets.get(`android-keystore-password-${config.type}`);
  const keyPassword = await secrets.get(`android-key-password-${config.type}`);

  // Write keystore to temp location
  const keystorePath = `/tmp/release.keystore`;
  await fs.writeFile(keystorePath, keystore);

  return {
    keystorePath,
    keystorePassword,
    keyAlias: config.keystoreAlias,
    keyPassword,
  };
}
```

### Device Testing

```typescript
interface DeviceTestConfig {
  platform: "ios" | "android";
  devices: string[];
  testPlan?: string;
  timeout: number;
}

async function runDeviceTests(
  context,
  checkRunId: number,
  buildArtifact: string,
  config: DeviceTestConfig
) {
  // Upload to device farm
  const uploadResult = await deviceFarm.uploadApp({
    appPath: buildArtifact,
    platform: config.platform,
  });

  // Create test run
  const testRun = await deviceFarm.createRun({
    appArn: uploadResult.arn,
    devicePoolArn: getDevicePoolArn(config.devices),
    test: {
      type: config.platform === "ios" ? "XCTEST_UI" : "INSTRUMENTATION",
      testPackageArn: uploadResult.testPackageArn,
    },
  });

  // Poll for completion
  const result = await pollTestRun(testRun.arn, config.timeout);

  // Update check run with results
  await context.octokit.checks.update(
    context.repo({
      check_run_id: checkRunId,
      status: "completed",
      conclusion: result.passed ? "success" : "failure",
      output: {
        title: `Device Tests: ${result.passed ? "Passed" : "Failed"}`,
        summary: formatTestResults(result),
        images: result.screenshots.map(s => ({
          alt: s.deviceName,
          image_url: s.url,
          caption: `${s.deviceName} - ${s.testName}`,
        })),
      },
    })
  );

  return result;
}
```

### Beta Distribution

```typescript
app.on("release.published", async (context) => {
  const { release, repository } = context.payload;

  // Only distribute pre-releases to beta
  if (!release.prerelease) return;

  // Get build artifacts
  const { data: assets } = await context.octokit.repos.listReleaseAssets({
    owner: repository.owner.login,
    repo: repository.name,
    release_id: release.id,
  });

  const iosApp = assets.find(a => a.name.endsWith(".ipa"));
  const androidApp = assets.find(a => a.name.endsWith(".apk") || a.name.endsWith(".aab"));

  const distributions = [];

  if (iosApp) {
    // Upload to TestFlight
    const testflightResult = await uploadToTestFlight({
      ipaUrl: iosApp.browser_download_url,
      releaseNotes: release.body,
      whatsNew: release.name,
    });
    distributions.push({ platform: "iOS", url: testflightResult.url });
  }

  if (androidApp) {
    // Upload to Firebase App Distribution
    const firebaseResult = await uploadToFirebaseDistribution({
      appUrl: androidApp.browser_download_url,
      releaseNotes: release.body,
      groups: ["beta-testers"],
    });
    distributions.push({ platform: "Android", url: firebaseResult.url });
  }

  // Comment on release
  await context.octokit.repos.updateRelease({
    owner: repository.owner.login,
    repo: repository.name,
    release_id: release.id,
    body: `${release.body}\n\n## Beta Distribution\n${distributions.map(d => `- ${d.platform}: ${d.url}`).join("\n")}`,
  });
});
```

### Screenshot Generation

```typescript
interface ScreenshotConfig {
  devices: Array<{
    name: string;
    platform: "ios" | "android";
    simulator: string;
  }>;
  locales: string[];
  screens: string[];
}

async function generateScreenshots(
  context,
  sha: string,
  config: ScreenshotConfig
) {
  const screenshots: Screenshot[] = [];

  for (const device of config.devices) {
    for (const locale of config.locales) {
      // Build app for device
      const app = await buildForDevice(context, sha, device);

      // Boot simulator/emulator
      await bootDevice(device);

      // Set locale
      await setDeviceLocale(device, locale);

      // Install app
      await installApp(device, app);

      // Capture each screen
      for (const screen of config.screens) {
        await navigateToScreen(device, screen);
        const screenshot = await captureScreenshot(device);

        screenshots.push({
          device: device.name,
          locale,
          screen,
          path: screenshot,
        });
      }
    }
  }

  // Upload to artifact storage
  const urls = await uploadScreenshots(screenshots);

  return urls;
}
```

## Mobile-Specific Build Configurations

### iOS xcconfig
```typescript
async function parseXCConfig(context, sha: string) {
  const configFiles = await findFiles(context, "**/*.xcconfig", sha);
  const configs: Record<string, Record<string, string>> = {};

  for (const file of configFiles) {
    const content = await getFileContent(context, file, sha);
    configs[file] = parseXCConfigContent(content);
  }

  return configs;
}
```

### Android build.gradle
```typescript
async function parseGradleConfig(context, sha: string) {
  const buildGradle = await getFileContent(context, "app/build.gradle", sha)
    || await getFileContent(context, "app/build.gradle.kts", sha);

  if (!buildGradle) return null;

  // Extract version info
  const versionCode = buildGradle.match(/versionCode\s+(\d+)/)?.[1];
  const versionName = buildGradle.match(/versionName\s+["'](.+)["']/)?.[1];

  // Extract build types
  const buildTypes = extractBuildTypes(buildGradle);

  return { versionCode, versionName, buildTypes };
}
```

## Security Considerations

- **Protect signing keys** - Never store in repo, use secrets management
- **Rotate certificates** - Before expiration
- **Limit beta access** - Control who can install builds
- **Audit builds** - Track who triggered what
- **Secure artifacts** - Don't expose debug builds publicly
- **Review permissions** - Mobile apps request device permissions

## Platform-Specific Services

| Service | Platform | Purpose |
|---------|----------|---------|
| TestFlight | iOS | Beta distribution |
| App Store Connect | iOS | App Store publishing |
| Firebase App Distribution | Both | Beta distribution |
| Google Play Console | Android | Play Store publishing |
| AWS Device Farm | Both | Real device testing |
| BrowserStack | Both | Device cloud |
| Fastlane | Both | Automation toolkit |

## Example Apps in This Category

- **Bitrise** - Mobile-first CI/CD
- **Codemagic** - Flutter/mobile CI
- **Appcircle** - Mobile DevOps platform
- **Fastlane** - Mobile automation

## Related Categories

- [CI](ci.md) - General CI concepts
- [Testing](testing.md) - Test automation
- [Publishing](publishing.md) - App store distribution

## See Also

- [Fastlane Documentation](https://fastlane.tools/)
- [Xcode Cloud](https://developer.apple.com/xcode-cloud/)
- [Firebase App Distribution](https://firebase.google.com/docs/app-distribution)
