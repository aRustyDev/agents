/**
 * GitHub App Authentication Patterns
 *
 * Examples of different authentication flows for GitHub Apps:
 * - JWT generation for app-level auth
 * - Installation token exchange for repository access
 * - User token flow for user-delegated permissions
 */

import { createAppAuth } from "@octokit/auth-app";
import { Octokit } from "@octokit/rest";
import { sign } from "jsonwebtoken";

// =============================================================================
// Pattern 1: Basic App Authentication (JWT)
// =============================================================================

/**
 * Create app-level Octokit client for installation management
 * Use this for: listing installations, getting installation details
 */
export function createAppOctokit(appId: string, privateKey: string): Octokit {
  return new Octokit({
    authStrategy: createAppAuth,
    auth: {
      appId,
      privateKey,
    },
  });
}

/**
 * Manual JWT creation (useful for debugging or custom auth flows)
 */
export function createAppJWT(appId: string, privateKey: string): string {
  const now = Math.floor(Date.now() / 1000);

  const payload = {
    iat: now - 60, // Issued 1 minute ago (clock skew protection)
    exp: now + (10 * 60), // Expires in 10 minutes (max allowed)
    iss: appId,
  };

  return sign(payload, privateKey, { algorithm: "RS256" });
}

// =============================================================================
// Pattern 2: Installation Token Exchange
// =============================================================================

/**
 * Create installation-scoped Octokit client
 * Use this for: repository operations, API calls on behalf of the app
 */
export async function createInstallationOctokit(
  appId: string,
  privateKey: string,
  installationId: number
): Promise<Octokit> {
  const appOctokit = createAppOctokit(appId, privateKey);

  // Exchange JWT for installation token
  const { token } = await appOctokit.auth({
    type: "installation",
    installationId,
  }) as { token: string };

  return new Octokit({ auth: token });
}

/**
 * Alternative: Manual installation token request
 * Useful when you need the token itself (e.g., for external tools)
 */
export async function getInstallationToken(
  appId: string,
  privateKey: string,
  installationId: number
): Promise<{ token: string; expiresAt: string }> {
  const jwt = createAppJWT(appId, privateKey);

  const response = await fetch(
    `https://api.github.com/app/installations/${installationId}/access_tokens`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${jwt}`,
        Accept: "application/vnd.github.v3+json",
      },
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to get installation token: ${response.statusText}`);
  }

  const { token, expires_at } = await response.json();
  return { token, expiresAt: expires_at };
}

// =============================================================================
// Pattern 3: User Token Flow (OAuth)
// =============================================================================

/**
 * Create user-authorized Octokit client
 * Use this for: actions that require user permission (private repos, etc.)
 */
export async function createUserOctokit(
  appId: string,
  privateKey: string,
  userCode: string
): Promise<Octokit> {
  return new Octokit({
    authStrategy: createAppAuth,
    auth: {
      appId,
      privateKey,
      code: userCode,
    },
  });
}

/**
 * Generate OAuth authorization URL for user consent
 */
export function getUserAuthorizationURL(
  clientId: string,
  redirectUri: string,
  state?: string
): string {
  const params = new URLSearchParams({
    client_id: clientId,
    redirect_uri: redirectUri,
    ...(state && { state }),
  });

  return `https://github.com/login/oauth/authorize?${params}`;
}

// =============================================================================
// Pattern 4: Cloudflare Workers Helper
// =============================================================================

/**
 * Cloudflare Workers-optimized auth helper
 * Handles secrets from Workers environment
 */
export interface WorkerEnv {
  GITHUB_APP_ID: string;
  GITHUB_PRIVATE_KEY: string;
  GITHUB_CLIENT_ID?: string;
  GITHUB_CLIENT_SECRET?: string;
}

export class GitHubAppAuth {
  constructor(private env: WorkerEnv) {}

  /**
   * Get app-level client for installation management
   */
  getAppClient(): Octokit {
    return createAppOctokit(this.env.GITHUB_APP_ID, this.env.GITHUB_PRIVATE_KEY);
  }

  /**
   * Get installation client from webhook payload
   */
  async getInstallationClient(installationId: number): Promise<Octokit> {
    return createInstallationOctokit(
      this.env.GITHUB_APP_ID,
      this.env.GITHUB_PRIVATE_KEY,
      installationId
    );
  }

  /**
   * Extract installation ID from webhook payload
   */
  getInstallationId(payload: any): number {
    return payload.installation?.id;
  }
}

// =============================================================================
// Pattern 5: Error Handling & Token Validation
// =============================================================================

/**
 * Validate that installation token is working
 */
export async function validateInstallationToken(
  octokit: Octokit,
  owner: string,
  repo: string
): Promise<boolean> {
  try {
    await octokit.repos.get({ owner, repo });
    return true;
  } catch (error: any) {
    if (error.status === 401) {
      console.error("Installation token invalid or expired");
      return false;
    }
    if (error.status === 404) {
      console.error("App not installed on repository or repo doesn't exist");
      return false;
    }
    throw error; // Re-throw other errors
  }
}

/**
 * Safe wrapper for operations that might fail due to auth
 */
export async function withAuthRetry<T>(
  operation: () => Promise<T>,
  refreshAuth: () => Promise<void>
): Promise<T> {
  try {
    return await operation();
  } catch (error: any) {
    if (error.status === 401) {
      // Token might be expired, try refreshing
      await refreshAuth();
      return await operation(); // Retry once
    }
    throw error;
  }
}

// =============================================================================
// Example Usage
// =============================================================================

export async function exampleUsage() {
  const env = {
    GITHUB_APP_ID: "123456",
    GITHUB_PRIVATE_KEY: "-----BEGIN RSA PRIVATE KEY-----...",
  };

  const auth = new GitHubAppAuth(env);

  // Get app client to list installations
  const appClient = auth.getAppClient();
  const installations = await appClient.apps.listInstallations();

  console.log(`Found ${installations.data.length} installations`);

  // Get installation client for specific repo operations
  const installationId = installations.data[0].id;
  const installationClient = await auth.getInstallationClient(installationId);

  // Make API calls on behalf of the app
  const repos = await installationClient.apps.listReposAccessibleToInstallation();
  console.log(`App has access to ${repos.data.repositories.length} repositories`);
}
