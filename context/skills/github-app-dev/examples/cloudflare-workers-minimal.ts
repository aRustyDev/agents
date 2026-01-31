/**
 * Minimal GitHub App for Cloudflare Workers
 *
 * Features:
 * - Auto-label PRs based on title
 * - Welcome new issues
 * - Webhook signature verification
 */

import { Hono } from "hono";
import { Webhooks } from "@octokit/webhooks";
import { createAppAuth } from "@octokit/auth-app";
import { Octokit } from "@octokit/rest";

type Bindings = {
  GITHUB_APP_ID: string;
  GITHUB_PRIVATE_KEY: string;
  GITHUB_WEBHOOK_SECRET: string;
};

const app = new Hono<{ Bindings: Bindings }>();

// Create installation-scoped Octokit
async function createInstallationOctokit(
  env: Bindings,
  installationId: number
): Promise<Octokit> {
  const appOctokit = new Octokit({
    authStrategy: createAppAuth,
    auth: {
      appId: env.GITHUB_APP_ID,
      privateKey: env.GITHUB_PRIVATE_KEY,
    },
  });

  const { token } = await appOctokit.auth({
    type: "installation",
    installationId,
  }) as { token: string };

  return new Octokit({ auth: token });
}

// Webhook endpoint
app.post("/webhook", async (c) => {
  const webhooks = new Webhooks({ secret: c.env.GITHUB_WEBHOOK_SECRET });

  // Auto-label PRs based on title
  webhooks.on("pull_request.opened", async ({ payload }) => {
    const { title, number } = payload.pull_request;
    const { owner, name: repo } = payload.repository;
    const installationId = payload.installation?.id;

    if (!installationId) return;

    const octokit = await createInstallationOctokit(c.env, installationId);
    const labels: string[] = [];

    // Conventional commit labeling
    if (title.startsWith("feat")) labels.push("enhancement");
    if (title.startsWith("fix")) labels.push("bug");
    if (title.startsWith("docs")) labels.push("documentation");
    if (title.startsWith("chore")) labels.push("maintenance");

    if (labels.length > 0) {
      try {
        await octokit.issues.addLabels({
          owner: owner.login,
          repo,
          issue_number: number,
          labels,
        });
        console.log(`Added labels ${labels.join(", ")} to PR #${number}`);
      } catch (error) {
        console.error("Failed to add labels:", error);
      }
    }
  });

  // Welcome new issues
  webhooks.on("issues.opened", async ({ payload }) => {
    const { number } = payload.issue;
    const { owner, name: repo } = payload.repository;
    const installationId = payload.installation?.id;

    if (!installationId) return;

    const octokit = await createInstallationOctokit(c.env, installationId);

    try {
      await octokit.issues.createComment({
        owner: owner.login,
        repo,
        issue_number: number,
        body: "👋 Thanks for opening this issue! We'll take a look and get back to you.",
      });
      console.log(`Welcomed new issue #${number}`);
    } catch (error) {
      console.error("Failed to comment on issue:", error);
    }
  });

  // Process webhook
  const signature = c.req.header("x-hub-signature-256") || "";
  const body = await c.req.text();

  try {
    await webhooks.verifyAndReceive({
      id: c.req.header("x-github-delivery") || "",
      name: c.req.header("x-github-event") as any,
      signature,
      payload: body,
    });
    return c.text("OK");
  } catch (error) {
    console.error("Webhook verification failed:", error);
    return c.text("Unauthorized", 401);
  }
});

// Health check
app.get("/health", (c) => c.text("OK"));

export default app;