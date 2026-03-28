/**
 * Reviewer Assignment Pattern for GitHub Apps
 *
 * Automatically assign reviewers to PRs based on CODEOWNERS,
 * team availability, and workload balancing.
 */

import { Octokit } from "@octokit/rest";

// =============================================================================
// CODEOWNERS-Based Assignment
// =============================================================================

interface CodeOwner {
  pattern: string;
  owners: string[];
}

/**
 * Parse CODEOWNERS file to determine reviewers for changed files
 */
export async function parseCodeOwners(
  octokit: Octokit,
  owner: string,
  repo: string,
  ref: string = "main"
): Promise<CodeOwner[]> {
  try {
    const { data } = await octokit.repos.getContent({
      owner,
      repo,
      path: "CODEOWNERS",
      ref,
    });

    if ("content" in data) {
      const content = Buffer.from(data.content, "base64").toString();
      return parseCodeOwnersContent(content);
    }
  } catch (error: any) {
    if (error.status !== 404) {
      console.error("Error fetching CODEOWNERS:", error);
    }
    // No CODEOWNERS file found
  }

  return [];
}

function parseCodeOwnersContent(content: string): CodeOwner[] {
  return content
    .split("\n")
    .map(line => line.trim())
    .filter(line => line && !line.startsWith("#"))
    .map(line => {
      const parts = line.split(/\s+/);
      const pattern = parts[0];
      const owners = parts.slice(1).map(owner => owner.replace(/^@/, ""));
      return { pattern, owners };
    })
    .reverse(); // CODEOWNERS uses last-match-wins
}

/**
 * Find code owners for specific file paths
 */
export function getOwnersForFiles(codeOwners: CodeOwner[], filePaths: string[]): string[] {
  const owners = new Set<string>();

  for (const filePath of filePaths) {
    for (const rule of codeOwners) {
      if (matchesPattern(rule.pattern, filePath)) {
        rule.owners.forEach(owner => owners.add(owner));
        break; // First match wins (since we reversed the array)
      }
    }
  }

  return Array.from(owners);
}

function matchesPattern(pattern: string, filePath: string): boolean {
  // Simple glob pattern matching - could be enhanced with proper glob library
  const regexPattern = pattern
    .replace(/\*\*/g, "DOUBLE_STAR")
    .replace(/\*/g, "[^/]*")
    .replace(/DOUBLE_STAR/g, ".*")
    .replace(/\?/g, "[^/]");

  const regex = new RegExp(`^${regexPattern}$`);
  return regex.test(filePath);
}

// =============================================================================
// Team-Based Assignment
// =============================================================================

interface TeamMember {
  login: string;
  availability: "available" | "busy" | "away";
  currentReviews: number;
  expertise: string[];
}

/**
 * Get team members and their current workload
 */
export async function getTeamWorkload(
  octokit: Octokit,
  org: string,
  teamSlug: string
): Promise<TeamMember[]> {
  try {
    const { data: members } = await octokit.teams.listMembersInOrg({
      org,
      team_slug: teamSlug,
    });

    const teamMembers: TeamMember[] = [];

    for (const member of members) {
      const currentReviews = await getCurrentReviewCount(octokit, member.login);

      teamMembers.push({
        login: member.login,
        availability: await getUserAvailability(octokit, member.login),
        currentReviews,
        expertise: await getUserExpertise(octokit, org, member.login),
      });
    }

    return teamMembers;
  } catch (error) {
    console.error("Error fetching team workload:", error);
    return [];
  }
}

async function getCurrentReviewCount(octokit: Octokit, username: string): Promise<number> {
  try {
    const { data: searchResult } = await octokit.search.issuesAndPullRequests({
      q: `type:pr state:open review-requested:${username}`,
      per_page: 1,
    });

    return searchResult.total_count;
  } catch (error) {
    console.error(`Error getting review count for ${username}:`, error);
    return 0;
  }
}

async function getUserAvailability(octokit: Octokit, username: string): Promise<TeamMember["availability"]> {
  try {
    // Check if user has recent activity (simplified availability check)
    const { data: events } = await octokit.activity.listPublicEventsForUser({
      username,
      per_page: 5,
    });

    const recentActivity = events.some(event => {
      const eventDate = new Date(event.created_at);
      const threeDaysAgo = new Date(Date.now() - 3 * 24 * 60 * 60 * 1000);
      return eventDate > threeDaysAgo;
    });

    return recentActivity ? "available" : "away";
  } catch (error) {
    return "available"; // Default to available if we can't determine
  }
}

async function getUserExpertise(octokit: Octokit, org: string, username: string): Promise<string[]> {
  // This could be enhanced by analyzing:
  // - Repository languages they contribute to
  // - File patterns they frequently modify
  // - Team memberships

  // For now, return empty array (could be configured per organization)
  return [];
}

// =============================================================================
// Load Balancing Algorithm
// =============================================================================

/**
 * Select reviewers balancing workload and expertise
 */
export function selectBalancedReviewers(
  potentialReviewers: string[],
  teamMembers: TeamMember[],
  filePaths: string[],
  maxReviewers: number = 2
): string[] {
  // Filter to available team members who are potential reviewers
  const availableReviewers = teamMembers.filter(member =>
    potentialReviewers.includes(member.login) &&
    member.availability !== "away"
  );

  if (availableReviewers.length === 0) {
    return potentialReviewers.slice(0, maxReviewers); // Fallback to any potential reviewers
  }

  // Sort by workload (fewer current reviews = higher priority)
  const sortedByWorkload = [...availableReviewers].sort((a, b) => {
    if (a.currentReviews !== b.currentReviews) {
      return a.currentReviews - b.currentReviews;
    }
    // If same workload, prefer available over busy
    if (a.availability !== b.availability) {
      return a.availability === "available" ? -1 : 1;
    }
    return 0;
  });

  // Select up to maxReviewers
  return sortedByWorkload
    .slice(0, maxReviewers)
    .map(member => member.login);
}

// =============================================================================
// Complete Reviewer Assignment Service
// =============================================================================

export class ReviewerAssignmentService {
  constructor(private octokit: Octokit) {}

  async assignReviewers(payload: any): Promise<void> {
    const { repository, pull_request } = payload;
    const { owner, name: repo } = repository;
    const prNumber = pull_request.number;

    try {
      // Get changed files
      const { data: files } = await this.octokit.pulls.listFiles({
        owner: owner.login,
        repo,
        pull_number: prNumber,
      });

      const filePaths = files.map(file => file.filename);
      console.log(`PR #${prNumber} changed files:`, filePaths);

      // Find reviewers based on multiple strategies
      const reviewers = await this.findOptimalReviewers(
        owner.login,
        repo,
        filePaths,
        pull_request.user.login // PR author
      );

      if (reviewers.length > 0) {
        await this.octokit.pulls.requestReviewers({
          owner: owner.login,
          repo,
          pull_number: prNumber,
          reviewers,
        });

        console.log(`Assigned reviewers to PR #${prNumber}:`, reviewers);
      } else {
        console.log(`No reviewers found for PR #${prNumber}`);
      }
    } catch (error) {
      console.error("Reviewer assignment failed:", error);
    }
  }

  private async findOptimalReviewers(
    owner: string,
    repo: string,
    filePaths: string[],
    prAuthor: string,
    maxReviewers: number = 2
  ): Promise<string[]> {
    // Strategy 1: CODEOWNERS-based assignment
    const codeOwners = await parseCodeOwners(this.octokit, owner, repo);
    let potentialReviewers = getOwnersForFiles(codeOwners, filePaths);

    // Remove PR author from potential reviewers
    potentialReviewers = potentialReviewers.filter(reviewer => reviewer !== prAuthor);

    if (potentialReviewers.length === 0) {
      // Strategy 2: Fallback to default reviewers or team
      potentialReviewers = await this.getDefaultReviewers(owner, repo);
    }

    if (potentialReviewers.length === 0) {
      console.log("No potential reviewers found");
      return [];
    }

    // Strategy 3: Load balancing among potential reviewers
    const teamMembers = await this.getRelevantTeamMembers(owner, potentialReviewers);
    const selectedReviewers = selectBalancedReviewers(
      potentialReviewers,
      teamMembers,
      filePaths,
      maxReviewers
    );

    return selectedReviewers;
  }

  private async getDefaultReviewers(owner: string, repo: string): Promise<string[]> {
    try {
      // Try to get repository collaborators with write access
      const { data: collaborators } = await this.octokit.repos.listCollaborators({
        owner,
        repo,
        permission: "write",
      });

      return collaborators
        .slice(0, 3) // Limit to first 3 collaborators
        .map(collab => collab.login);
    } catch (error) {
      console.error("Error fetching default reviewers:", error);
      return [];
    }
  }

  private async getRelevantTeamMembers(
    org: string,
    potentialReviewers: string[]
  ): Promise<TeamMember[]> {
    // For simplicity, create TeamMember objects for potential reviewers
    // In a real implementation, you'd fetch actual team data
    const teamMembers: TeamMember[] = [];

    for (const reviewer of potentialReviewers) {
      const currentReviews = await getCurrentReviewCount(this.octokit, reviewer);

      teamMembers.push({
        login: reviewer,
        availability: await getUserAvailability(this.octokit, reviewer),
        currentReviews,
        expertise: [],
      });
    }

    return teamMembers;
  }
}

// =============================================================================
// Advanced Pattern: Time-Zone Aware Assignment
// =============================================================================

interface ReviewerWithTimezone {
  login: string;
  timezone: string;
  localTime: Date;
  isWorkingHours: boolean;
}

/**
 * Assign reviewers considering their local time zones
 */
export async function getTimeZoneAwareReviewers(
  potentialReviewers: string[],
  maxReviewers: number = 2
): Promise<string[]> {
  const reviewersWithTz: ReviewerWithTimezone[] = [];

  for (const reviewer of potentialReviewers) {
    // In a real implementation, you'd store timezone info in your database
    // or fetch from user profiles
    const timezone = await getReviewerTimezone(reviewer);
    const localTime = new Date(); // Would calculate based on timezone
    const isWorkingHours = isInWorkingHours(localTime);

    reviewersWithTz.push({
      login: reviewer,
      timezone,
      localTime,
      isWorkingHours,
    });
  }

  // Prefer reviewers in working hours
  const workingHoursReviewers = reviewersWithTz.filter(r => r.isWorkingHours);

  if (workingHoursReviewers.length >= maxReviewers) {
    return workingHoursReviewers
      .slice(0, maxReviewers)
      .map(r => r.login);
  }

  // If not enough reviewers in working hours, include others
  return reviewersWithTz
    .slice(0, maxReviewers)
    .map(r => r.login);
}

async function getReviewerTimezone(username: string): Promise<string> {
  // Placeholder - would fetch from user settings or database
  return "UTC";
}

function isInWorkingHours(localTime: Date): boolean {
  const hour = localTime.getHours();
  const day = localTime.getDay();

  // Monday-Friday, 9 AM - 5 PM
  return day >= 1 && day <= 5 && hour >= 9 && hour <= 17;
}

// =============================================================================
// Configuration-Driven Assignment
// =============================================================================

interface ReviewerConfig {
  patterns: Array<{
    files: string;
    reviewers: string[];
    minReviewers: number;
    maxReviewers: number;
  }>;
  defaultReviewers: string[];
  excludeAuthors: boolean;
  balanceWorkload: boolean;
}

/**
 * Load reviewer configuration from repository
 */
export async function loadReviewerConfig(
  octokit: Octokit,
  owner: string,
  repo: string
): Promise<ReviewerConfig | null> {
  try {
    const { data } = await octokit.repos.getContent({
      owner,
      repo,
      path: ".github/reviewers.yml",
    });

    if ("content" in data) {
      const content = Buffer.from(data.content, "base64").toString();
      // Would parse YAML here - using placeholder
      return JSON.parse(content) as ReviewerConfig;
    }
  } catch (error: any) {
    if (error.status !== 404) {
      console.error("Error fetching reviewer config:", error);
    }
  }

  return null;
}

// =============================================================================
// Usage Example
// =============================================================================

export function setupReviewerAssignmentWebhooks(webhooks: any, octokit: Octokit) {
  const reviewerService = new ReviewerAssignmentService(octokit);

  webhooks.on("pull_request.opened", async ({ payload }: any) => {
    await reviewerService.assignReviewers(payload);
  });

  // Also handle when reviewers are removed (re-assign if needed)
  webhooks.on("pull_request.review_requested", async ({ payload }: any) => {
    console.log(`Review requested from ${payload.requested_reviewer?.login}`);
  });

  webhooks.on("pull_request.review_request_removed", async ({ payload }: any) => {
    console.log(`Review request removed from ${payload.requested_reviewer?.login}`);
    // Could trigger re-assignment logic here
  });
}
