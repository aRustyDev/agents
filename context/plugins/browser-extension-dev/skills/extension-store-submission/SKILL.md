# Extension Store Submission

Complete guides for submitting browser extensions to Chrome Web Store, Firefox Add-ons (AMO), Safari App Store, and Edge Add-ons. Covers account setup, asset preparation, submission process, and post-publication management.

## Store Overview

| Store | Review Time | Fee | Manifest Version | Update Frequency |
|-------|-------------|-----|------------------|------------------|
| Chrome Web Store | 1-3 days | $5 (one-time) | V3 required | On submission |
| Firefox Add-ons | 1-5 days | Free | V2 or V3 | On submission |
| Safari App Store | 1-7 days | $99/year | V3 required | App Store Connect |
| Edge Add-ons | 1-7 days | Free | V3 required | Partner Center |

## Chrome Web Store

### Account Setup

1. Create or use existing Google account
2. Pay $5 one-time registration fee at [Chrome Web Store Developer Dashboard](https://chrome.google.com/webstore/devconsole)
3. Verify account (email verification required)
4. Set up payment profile for paid extensions

### Required Assets

| Asset | Dimensions | Format | Notes |
|-------|------------|--------|-------|
| Icon | 128x128 | PNG | Required in manifest |
| Screenshots | 1280x800 or 640x400 | PNG/JPEG | 1-5 required |
| Promotional tile (small) | 440x280 | PNG/JPEG | Optional |
| Promotional tile (large) | 920x680 | PNG/JPEG | Featured extensions |
| Marquee | 1400x560 | PNG/JPEG | Homepage features |

### Submission Process

```text
1. Package Extension
   $ wxt zip          # Creates .output/<name>-<version>-chrome.zip

2. Upload to Dashboard
   → Developer Dashboard → Items → Add New Item
   → Upload ZIP file

3. Complete Store Listing
   → Description (up to 132 chars visible)
   → Screenshots (actual functionality)
   → Category selection
   → Language/region targeting

4. Privacy Practices
   → Data collection disclosure
   → Privacy policy URL (if collecting data)
   → Permissions justification

5. Submit for Review
   → Preview listing
   → Submit for review
```

### Permission Justifications

Chrome requires justification for sensitive permissions:

| Permission | Requires Justification | Example Justification |
|------------|------------------------|----------------------|
| `<all_urls>` | Yes | "Required to inject content script on all pages for ad blocking" |
| `tabs` | Yes | "Needed to track tab URLs for bookmark sync" |
| `webRequest` | Yes | "Required to modify request headers for privacy protection" |
| `history` | Yes | "Core functionality: history search and management" |
| `cookies` | Yes | "Session management for authenticated API calls" |

### Common Rejection Reasons

| Reason | Policy | Fix |
|--------|--------|-----|
| Misleading metadata | Accurate descriptions | Match listing to functionality |
| Insufficient functionality | Single purpose | Add meaningful features |
| Excessive permissions | Minimum necessary | Remove unused permissions |
| Remote code execution | No remote code | Bundle all scripts |
| Trademark violation | IP rights | Remove protected terms |
| Spam/deceptive | Quality guidelines | Provide genuine value |

### Review Acceleration

- **Provide clear testing instructions** in reviewer notes
- **Include demo account** if login required
- **Document all permission usage** in privacy section
- **Respond quickly** to reviewer questions
- **No policy violations** = faster reviews

## Firefox Add-ons (AMO)

### Account Setup

1. Create Firefox Account at [addons.mozilla.org](https://addons.mozilla.org)
2. No registration fee required
3. Enable two-factor authentication (recommended)
4. Complete developer agreement

### Required Manifest Fields

```json
{
  "browser_specific_settings": {
    "gecko": {
      "id": "extension@example.com",
      "strict_min_version": "109.0",
      "data_collection_permissions": {
        "required": [],
        "optional": ["technicalAndInteraction"]
      }
    }
  }
}
```

### Required Assets

| Asset | Dimensions | Format | Notes |
|-------|------------|--------|-------|
| Icon | 48x48, 96x96 | PNG | Required in manifest |
| Screenshots | Any reasonable | PNG/JPEG | 1+ showing functionality |
| Header image | 700x280 | PNG/JPEG | Optional |

### Submission Process

```text
1. Build Extension
   $ wxt zip -b firefox  # Creates .output/<name>-<version>-firefox.zip

2. Sign Extension (optional for self-distribution)
   $ web-ext sign --api-key=KEY --api-secret=SECRET

3. Submit to AMO
   → addons.mozilla.org → Submit a New Add-on
   → Upload ZIP file
   → Choose visibility (listed/unlisted)

4. Provide Information
   → Extension name and summary
   → Category selection
   → Support email/URL
   → License selection

5. Source Code Submission (if minified)
   → Upload source archive
   → Include build instructions

6. Review Notes
   → Testing instructions
   → Permission explanations
   → Third-party library list
```

### Data Collection Permissions (Required 2025+)

```json
{
  "browser_specific_settings": {
    "gecko": {
      "data_collection_permissions": {
        "required": ["technicalAndInteraction"],
        "optional": ["locationData", "healthData"]
      }
    }
  }
}
```

| Permission | Description |
|------------|-------------|
| `technicalAndInteraction` | Usage patterns, crash reports |
| `locationData` | Geographic information |
| `healthData` | Health-related data |
| `financialData` | Payment/financial info |
| `personalIdentifiers` | Names, emails, accounts |

### Common Rejection Reasons

| Reason | Fix |
|--------|-----|
| Missing gecko.id | Add unique email-format ID |
| Obfuscated code without source | Submit source code archive |
| eval() or new Function() usage | Refactor to static code |
| Inline scripts in HTML | Move to external files |
| Missing data consent | Add data_collection_permissions |
| Security vulnerabilities | Fix reported issues |

### Listed vs Unlisted

| Type | Review | Distribution | Updates |
|------|--------|--------------|---------|
| Listed | Full review | AMO search/install | Auto-update |
| Unlisted | Automated | Direct download | Manual or auto |

**Use unlisted for**: Enterprise deployments, beta testing, private tools.

## Safari App Store

### Account Setup

1. Enroll in [Apple Developer Program](https://developer.apple.com/programs/) ($99/year)
2. Create App Store Connect account
3. Generate signing certificates in Xcode
4. Register App ID in Developer Portal

### Converting Web Extension

```bash
# Convert existing extension to Safari format
xcrun safari-web-extension-converter /path/to/extension \
  --project-location /path/to/output \
  --app-name "Extension Name" \
  --bundle-identifier com.example.extension

# Open generated Xcode project
open /path/to/output/Extension\ Name.xcodeproj
```

### Required Assets

| Asset | Dimensions | Format | Notes |
|-------|------------|--------|-------|
| App Icon | 1024x1024 | PNG | Plus all required sizes |
| Screenshots (iPhone) | Various sizes | PNG | Per device class |
| Screenshots (iPad) | Various sizes | PNG | If supporting iPad |
| Screenshots (Mac) | 2880x1800 | PNG | For Mac App Store |

### Privacy Manifest (PrivacyInfo.xcprivacy)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>NSPrivacyTracking</key>
  <false/>
  <key>NSPrivacyTrackingDomains</key>
  <array/>
  <key>NSPrivacyCollectedDataTypes</key>
  <array>
    <dict>
      <key>NSPrivacyCollectedDataType</key>
      <string>NSPrivacyCollectedDataTypeBrowsingHistory</string>
      <key>NSPrivacyCollectedDataTypeLinked</key>
      <false/>
      <key>NSPrivacyCollectedDataTypeTracking</key>
      <false/>
      <key>NSPrivacyCollectedDataTypePurposes</key>
      <array>
        <string>NSPrivacyCollectedDataTypePurposeAppFunctionality</string>
      </array>
    </dict>
  </array>
  <key>NSPrivacyAccessedAPITypes</key>
  <array/>
</dict>
</plist>
```

### Submission Process

```text
1. Build in Xcode
   → Product → Archive
   → Select archive → Distribute App
   → App Store Connect → Upload

2. App Store Connect
   → Create new app record
   → Fill app information
   → Upload screenshots
   → Complete privacy questionnaire

3. Submit for Review
   → Select build
   → Add review notes
   → Submit for review
```

### Common Rejection Reasons

| Guideline | Issue | Fix |
|-----------|-------|-----|
| 2.1 Performance | App crashes | Test on all target devices |
| 2.3 Accurate Metadata | Screenshots don't match | Update screenshots |
| 2.5 Software Requirements | Missing privacy manifest | Add PrivacyInfo.xcprivacy |
| 4.2 Minimum Functionality | Extension does too little | Add meaningful features |
| 5.1 Privacy | Undisclosed data collection | Update privacy policy |

### App Store Guidelines for Extensions

- Extension must have a **containing app** with functionality
- Containing app cannot be empty (add settings, instructions)
- Extension should work **offline** where applicable
- Must provide **clear instructions** for enabling extension

## Edge Add-ons

### Account Setup

1. Create Microsoft Partner Center account
2. No registration fee required
3. Complete verification process
4. Accept developer agreement

### Submission Process

```text
1. Package Extension (same as Chrome)
   $ wxt zip          # Chrome format works for Edge

2. Partner Center
   → Partner Center → Microsoft Edge → Extensions
   → Create new extension
   → Upload ZIP file

3. Complete Listing
   → Store listing information
   → Screenshots and assets
   → Category selection

4. Submit for Review
   → Preview and submit
```

### Chrome Extension Migration

Edge accepts Chrome extensions with minimal changes:

```json
{
  "manifest_version": 3,
  "name": "Extension Name",
  "version": "1.0.0",
  "description": "Description"
  // No Edge-specific fields required
}
```

## Version Management

### Semantic Versioning

```text
MAJOR.MINOR.PATCH

1.0.0 → Initial release
1.0.1 → Bug fix
1.1.0 → New feature (backward compatible)
2.0.0 → Breaking changes
```

### Update Strategy

| Store | Update Method | Notes |
|-------|---------------|-------|
| Chrome | Upload new version | Same item, increment version |
| Firefox | Upload new version | Must be higher version |
| Safari | New build in Xcode | Increment build number |
| Edge | Upload new version | Same extension ID |

### Staged Rollouts

**Chrome Web Store** supports staged rollouts:

```text
1. Developer Dashboard → Item → Package
2. Upload new version
3. Set rollout percentage (5%, 10%, 50%, 100%)
4. Monitor crash reports and reviews
5. Increase percentage or rollback
```

## Review Timeline Tips

### Faster Reviews

1. **Clear description**: Explain exactly what extension does
2. **Test instructions**: Step-by-step for reviewers
3. **Demo credentials**: If login required
4. **Permission docs**: Why each permission is needed
5. **Clean code**: No obfuscation, no suspicious patterns
6. **Policy compliance**: Follow all guidelines

### When Reviews Take Longer

| Scenario | Typical Delay | Mitigation |
|----------|---------------|------------|
| First submission | +2-3 days | Thorough preparation |
| Sensitive permissions | +1-2 days | Detailed justification |
| Code review required | +3-5 days | Submit source code |
| Policy questions | Variable | Respond quickly |
| High volume periods | +1-3 days | Avoid holidays |

## Post-Publication

### Monitoring

- **Crash reports**: Chrome DevTools, Firefox crash reporting
- **User reviews**: Respond promptly, address issues
- **Analytics**: Usage patterns, feature adoption
- **Security**: Watch for vulnerability reports

### Responding to Reviews

```markdown
Do:
- Thank users for feedback
- Acknowledge issues promptly
- Provide solutions or workarounds
- Follow up after fixes

Don't:
- Argue with users
- Make excuses
- Ignore negative reviews
- Promise features you can't deliver
```

### Handling Rejection

```text
1. Read rejection reason carefully
2. Understand the specific policy violated
3. Make necessary changes
4. Document changes in notes
5. Resubmit with explanation
6. Appeal if rejection seems incorrect
```

## Multi-Store Publishing Workflow

```bash
# Build for all stores
wxt zip                    # Chrome/Edge
wxt zip -b firefox         # Firefox

# Safari requires Xcode build
# Open project and archive

# Submit in order of review speed
1. Edge Add-ons (fastest)
2. Chrome Web Store
3. Firefox Add-ons
4. Safari App Store (slowest)
```

## Related Resources

- **store-submission-reviewer agent**: Pre-submission compliance checking
- **cross-browser-compatibility skill**: API compatibility matrices
- **validate-extension command**: Automated validation

## Quality Checklist

Before submitting to any store:

- [ ] All functionality tested on target browser
- [ ] Screenshots show actual extension features
- [ ] Description accurately describes functionality
- [ ] Privacy policy covers all data collection
- [ ] All permissions justified and documented
- [ ] No deprecated APIs or patterns
- [ ] Version number incremented correctly
- [ ] Store-specific requirements met
