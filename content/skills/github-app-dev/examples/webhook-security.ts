/**
 * Webhook Security Example
 *
 * Comprehensive webhook security patterns including:
 * - Signature verification with timing-safe comparison
 * - Replay attack protection with sliding window
 * - Rate limiting per installation
 * - Input validation and sanitization
 * - IP allowlisting for GitHub hooks
 * - Audit logging for security events
 */

import crypto from "crypto";
import { Hono } from "hono";

// =============================================================================
// Security Configuration
// =============================================================================

interface SecurityConfig {
  webhookSecret: string;
  replayWindowMs: number; // How long to keep delivery IDs
  maxRequestsPerMinute: number;
  allowedIPs?: string[]; // GitHub's hook IPs (optional)
  requireHTTPS: boolean;
}

interface WebhookDelivery {
  id: string;
  timestamp: number;
  installationId: number;
  event: string;
}

interface RateLimitEntry {
  requests: number[];
  blocked: boolean;
  blockedUntil?: number;
}

// =============================================================================
// Signature Verification
// =============================================================================

class SignatureVerifier {
  constructor(private secret: string) {}

  /**
   * Verify GitHub webhook signature using timing-safe comparison
   */
  verify(payload: string, signature: string): boolean {
    if (!signature.startsWith("sha256=")) {
      return false;
    }

    const receivedSignature = signature.slice(7); // Remove 'sha256=' prefix
    const expectedSignature = crypto
      .createHmac("sha256", this.secret)
      .update(payload, "utf8")
      .digest("hex");

    // Use timing-safe comparison to prevent timing attacks
    return crypto.timingSafeEqual(
      Buffer.from(expectedSignature, "hex"),
      Buffer.from(receivedSignature, "hex")
    );
  }

  /**
   * Verify signature with additional entropy check
   */
  verifyWithEntropy(payload: string, signature: string): boolean {
    // Basic signature check
    if (!this.verify(payload, signature)) {
      return false;
    }

    // Additional entropy check - payload should have reasonable randomness
    const entropy = this.calculateEntropy(payload);
    return entropy > 3.0; // Reasonable threshold for GitHub payloads
  }

  private calculateEntropy(data: string): number {
    const frequencies = new Map<string, number>();

    // Count character frequencies
    for (const char of data) {
      frequencies.set(char, (frequencies.get(char) || 0) + 1);
    }

    // Calculate Shannon entropy
    let entropy = 0;
    const length = data.length;

    for (const count of frequencies.values()) {
      const probability = count / length;
      entropy -= probability * Math.log2(probability);
    }

    return entropy;
  }
}

// =============================================================================
// Replay Attack Protection
// =============================================================================

class ReplayProtection {
  private deliveries = new Map<string, WebhookDelivery>();
  private cleanupInterval: NodeJS.Timer;

  constructor(private windowMs: number = 5 * 60 * 1000) {
    // Clean up old deliveries every minute
    this.cleanupInterval = setInterval(() => {
      this.cleanup();
    }, 60 * 1000);
  }

  /**
   * Check if delivery ID is a replay attack
   */
  isReplay(
    deliveryId: string,
    installationId: number,
    event: string
  ): boolean {
    const delivery = this.deliveries.get(deliveryId);

    if (delivery) {
      // Delivery ID already seen
      return true;
    }

    // Store this delivery
    this.deliveries.set(deliveryId, {
      id: deliveryId,
      timestamp: Date.now(),
      installationId,
      event,
    });

    return false;
  }

  /**
   * Get delivery statistics for monitoring
   */
  getStats() {
    const now = Date.now();
    const recentDeliveries = Array.from(this.deliveries.values())
      .filter(d => now - d.timestamp < this.windowMs);

    const eventCounts = recentDeliveries.reduce((acc, d) => {
      acc[d.event] = (acc[d.event] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    return {
      totalDeliveries: this.deliveries.size,
      recentDeliveries: recentDeliveries.length,
      eventCounts,
      windowMs: this.windowMs,
    };
  }

  private cleanup() {
    const cutoff = Date.now() - this.windowMs;
    for (const [id, delivery] of this.deliveries.entries()) {
      if (delivery.timestamp < cutoff) {
        this.deliveries.delete(id);
      }
    }
  }

  destroy() {
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
    }
  }
}

// =============================================================================
// Rate Limiting
// =============================================================================

class RateLimiter {
  private installations = new Map<number, RateLimitEntry>();
  private cleanupInterval: NodeJS.Timer;

  constructor(
    private maxRequestsPerMinute: number = 60,
    private blockDurationMs: number = 5 * 60 * 1000
  ) {
    // Clean up old entries every minute
    this.cleanupInterval = setInterval(() => {
      this.cleanup();
    }, 60 * 1000);
  }

  /**
   * Check if installation is rate limited
   */
  isRateLimited(installationId: number): boolean {
    const now = Date.now();
    const entry = this.installations.get(installationId);

    if (!entry) {
      // First request from this installation
      this.installations.set(installationId, {
        requests: [now],
        blocked: false,
      });
      return false;
    }

    // Check if currently blocked
    if (entry.blocked && entry.blockedUntil && now < entry.blockedUntil) {
      return true;
    }

    // Remove requests older than 1 minute
    const oneMinuteAgo = now - 60 * 1000;
    entry.requests = entry.requests.filter(time => time > oneMinuteAgo);

    // Check if over limit
    if (entry.requests.length >= this.maxRequestsPerMinute) {
      entry.blocked = true;
      entry.blockedUntil = now + this.blockDurationMs;
      return true;
    }

    // Add current request
    entry.requests.push(now);
    entry.blocked = false;
    entry.blockedUntil = undefined;

    return false;
  }

  /**
   * Get rate limiting statistics
   */
  getStats() {
    const stats = {
      totalInstallations: this.installations.size,
      blockedInstallations: 0,
      requestsInLastMinute: 0,
    };

    const oneMinuteAgo = Date.now() - 60 * 1000;

    for (const entry of this.installations.values()) {
      if (entry.blocked) {
        stats.blockedInstallations++;
      }
      stats.requestsInLastMinute += entry.requests.filter(
        time => time > oneMinuteAgo
      ).length;
    }

    return stats;
  }

  private cleanup() {
    const cutoff = Date.now() - 60 * 1000;
    for (const [id, entry] of this.installations.entries()) {
      // Remove old requests
      entry.requests = entry.requests.filter(time => time > cutoff);

      // Remove entries with no recent activity
      if (entry.requests.length === 0 && !entry.blocked) {
        this.installations.delete(id);
      }
    }
  }

  destroy() {
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
    }
  }
}

// =============================================================================
// IP Allowlisting (Optional)
// =============================================================================

class IPAllowlist {
  private allowedRanges: Array<{ start: number; end: number }> = [];

  constructor(allowedCIDRs: string[] = []) {
    // GitHub's webhook IP ranges (as of 2024)
    const defaultGitHubIPs = [
      "192.30.252.0/22",
      "185.199.108.0/22",
      "140.82.112.0/20",
      "143.55.64.0/20",
      "2a0a:a440::/29",
      "2606:50c0::/32",
    ];

    const ipsToCheck = allowedCIDRs.length > 0 ? allowedCIDRs : defaultGitHubIPs;

    for (const cidr of ipsToCheck) {
      if (cidr.includes(":")) {
        // IPv6 - simplified check (production would use proper IPv6 parsing)
        continue;
      }

      const [ip, prefixLength] = cidr.split("/");
      const range = this.cidrToRange(ip, parseInt(prefixLength));
      if (range) {
        this.allowedRanges.push(range);
      }
    }
  }

  isAllowed(ip: string): boolean {
    // Always allow if no ranges configured
    if (this.allowedRanges.length === 0) {
      return true;
    }

    const ipNumber = this.ipToNumber(ip);
    if (ipNumber === null) {
      return false;
    }

    return this.allowedRanges.some(
      range => ipNumber >= range.start && ipNumber <= range.end
    );
  }

  private ipToNumber(ip: string): number | null {
    const parts = ip.split(".");
    if (parts.length !== 4) return null;

    let result = 0;
    for (let i = 0; i < 4; i++) {
      const part = parseInt(parts[i]);
      if (isNaN(part) || part < 0 || part > 255) return null;
      result = result * 256 + part;
    }

    return result;
  }

  private cidrToRange(
    ip: string,
    prefixLength: number
  ): { start: number; end: number } | null {
    const ipNumber = this.ipToNumber(ip);
    if (ipNumber === null) return null;

    const mask = (-1 << (32 - prefixLength)) >>> 0;
    const start = (ipNumber & mask) >>> 0;
    const end = (start | (0xffffffff >>> prefixLength)) >>> 0;

    return { start, end };
  }
}

// =============================================================================
// Input Validation
// =============================================================================

class InputValidator {
  /**
   * Validate webhook payload structure
   */
  validatePayload(payload: any): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    // Check required top-level fields
    if (!payload.repository) {
      errors.push("Missing repository field");
    }

    if (!payload.installation) {
      errors.push("Missing installation field");
    }

    if (!payload.sender) {
      errors.push("Missing sender field");
    }

    // Validate repository structure
    if (payload.repository) {
      if (typeof payload.repository.id !== "number") {
        errors.push("Invalid repository.id");
      }
      if (typeof payload.repository.full_name !== "string") {
        errors.push("Invalid repository.full_name");
      }
    }

    // Validate installation structure
    if (payload.installation) {
      if (typeof payload.installation.id !== "number") {
        errors.push("Invalid installation.id");
      }
    }

    // Check payload size (GitHub max is ~25MB, but we can be more restrictive)
    const payloadSize = JSON.stringify(payload).length;
    if (payloadSize > 5 * 1024 * 1024) { // 5MB limit
      errors.push(`Payload too large: ${payloadSize} bytes`);
    }

    return {
      valid: errors.length === 0,
      errors,
    };
  }

  /**
   * Sanitize string inputs to prevent injection attacks
   */
  sanitizeString(input: string, maxLength: number = 1000): string {
    return input
      .slice(0, maxLength)
      .replace(/[<>'"&]/g, "") // Remove potentially dangerous characters
      .trim();
  }

  /**
   * Validate and sanitize user inputs from issue/PR content
   */
  sanitizeUserInput(text: string): string {
    // Remove or escape potentially dangerous patterns
    return text
      .replace(/javascript:/gi, "")
      .replace(/data:/gi, "")
      .replace(/vbscript:/gi, "")
      .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, "")
      .trim();
  }
}

// =============================================================================
// Audit Logging
// =============================================================================

interface SecurityEvent {
  timestamp: string;
  type: "signature_invalid" | "replay_attack" | "rate_limited" | "ip_blocked" | "payload_invalid";
  details: Record<string, any>;
  severity: "low" | "medium" | "high" | "critical";
}

class SecurityAuditor {
  private events: SecurityEvent[] = [];

  logEvent(
    type: SecurityEvent["type"],
    details: Record<string, any>,
    severity: SecurityEvent["severity"] = "medium"
  ) {
    const event: SecurityEvent = {
      timestamp: new Date().toISOString(),
      type,
      details,
      severity,
    };

    this.events.push(event);
    console.log(`[SECURITY] ${severity.toUpperCase()}: ${type}`, details);

    // In production, send to your security monitoring system
    this.sendToSecuritySystem(event);

    // Keep only last 1000 events in memory
    if (this.events.length > 1000) {
      this.events = this.events.slice(-1000);
    }
  }

  getRecentEvents(minutes: number = 60): SecurityEvent[] {
    const cutoff = new Date(Date.now() - minutes * 60 * 1000).toISOString();
    return this.events.filter(event => event.timestamp > cutoff);
  }

  getSecuritySummary() {
    const recent = this.getRecentEvents();
    const summary = recent.reduce((acc, event) => {
      acc[event.type] = (acc[event.type] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const severityCounts = recent.reduce((acc, event) => {
      acc[event.severity] = (acc[event.severity] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    return {
      totalEvents: recent.length,
      eventTypes: summary,
      severityCounts,
      lastEventTime: recent.length > 0 ? recent[recent.length - 1].timestamp : null,
    };
  }

  private sendToSecuritySystem(event: SecurityEvent) {
    // In production, integrate with your security monitoring:
    // - Send to SIEM
    // - Alert on critical events
    // - Integrate with incident response tools

    if (event.severity === "critical") {
      // Immediate alert for critical events
      console.error("[CRITICAL SECURITY EVENT]", event);
    }
  }
}

// =============================================================================
// Complete Security Middleware
// =============================================================================

export class WebhookSecurity {
  private signatureVerifier: SignatureVerifier;
  private replayProtection: ReplayProtection;
  private rateLimiter: RateLimiter;
  private ipAllowlist: IPAllowlist;
  private inputValidator: InputValidator;
  private auditor: SecurityAuditor;

  constructor(private config: SecurityConfig) {
    this.signatureVerifier = new SignatureVerifier(config.webhookSecret);
    this.replayProtection = new ReplayProtection(config.replayWindowMs);
    this.rateLimiter = new RateLimiter(config.maxRequestsPerMinute);
    this.ipAllowlist = new IPAllowlist(config.allowedIPs);
    this.inputValidator = new InputValidator();
    this.auditor = new SecurityAuditor();
  }

  /**
   * Complete security validation for incoming webhooks
   */
  async validateWebhook(
    payload: string,
    headers: Record<string, string | undefined>,
    clientIP: string
  ): Promise<{
    valid: boolean;
    error?: string;
    payload?: any;
  }> {
    const deliveryId = headers["x-github-delivery"] || "";
    const signature = headers["x-hub-signature-256"] || "";
    const userAgent = headers["user-agent"] || "";

    try {
      // 1. HTTPS Check (if required)
      if (this.config.requireHTTPS && !headers["x-forwarded-proto"]?.includes("https")) {
        this.auditor.logEvent("signature_invalid", {
          reason: "HTTP not allowed",
          clientIP,
          deliveryId,
        }, "high");
        return { valid: false, error: "HTTPS required" };
      }

      // 2. IP Allowlisting
      if (!this.ipAllowlist.isAllowed(clientIP)) {
        this.auditor.logEvent("ip_blocked", {
          clientIP,
          deliveryId,
          userAgent,
        }, "high");
        return { valid: false, error: "IP not allowed" };
      }

      // 3. Signature Verification
      if (!this.signatureVerifier.verify(payload, signature)) {
        this.auditor.logEvent("signature_invalid", {
          clientIP,
          deliveryId,
          signaturePresent: !!signature,
          userAgent,
        }, "critical");
        return { valid: false, error: "Invalid signature" };
      }

      // 4. Parse payload
      let parsedPayload;
      try {
        parsedPayload = JSON.parse(payload);
      } catch {
        this.auditor.logEvent("payload_invalid", {
          reason: "JSON parse error",
          clientIP,
          deliveryId,
        }, "medium");
        return { valid: false, error: "Invalid JSON payload" };
      }

      // 5. Input Validation
      const validation = this.inputValidator.validatePayload(parsedPayload);
      if (!validation.valid) {
        this.auditor.logEvent("payload_invalid", {
          errors: validation.errors,
          clientIP,
          deliveryId,
        }, "medium");
        return { valid: false, error: `Payload validation failed: ${validation.errors.join(", ")}` };
      }

      const installationId = parsedPayload.installation?.id;
      const event = headers["x-github-event"] || "unknown";

      // 6. Replay Attack Protection
      if (this.replayProtection.isReplay(deliveryId, installationId, event)) {
        this.auditor.logEvent("replay_attack", {
          deliveryId,
          installationId,
          event,
          clientIP,
        }, "high");
        return { valid: false, error: "Replay attack detected" };
      }

      // 7. Rate Limiting
      if (this.rateLimiter.isRateLimited(installationId)) {
        this.auditor.logEvent("rate_limited", {
          installationId,
          clientIP,
          event,
        }, "medium");
        return { valid: false, error: "Rate limit exceeded" };
      }

      // All checks passed
      return {
        valid: true,
        payload: parsedPayload,
      };

    } catch (error) {
      this.auditor.logEvent("signature_invalid", {
        error: error instanceof Error ? error.message : "Unknown error",
        clientIP,
        deliveryId,
      }, "high");
      return { valid: false, error: "Security validation error" };
    }
  }

  /**
   * Get security statistics for monitoring
   */
  getSecurityStats() {
    return {
      replayProtection: this.replayProtection.getStats(),
      rateLimiting: this.rateLimiter.getStats(),
      security: this.auditor.getSecuritySummary(),
    };
  }

  /**
   * Clean up resources
   */
  destroy() {
    this.replayProtection.destroy();
    this.rateLimiter.destroy();
  }
}

// =============================================================================
// Usage Example
// =============================================================================

const app = new Hono();

// Initialize security with configuration
const security = new WebhookSecurity({
  webhookSecret: process.env.GITHUB_WEBHOOK_SECRET!,
  replayWindowMs: 5 * 60 * 1000, // 5 minutes
  maxRequestsPerMinute: 30,
  requireHTTPS: true,
});

// Security monitoring endpoint
app.get("/security/stats", async (c) => {
  const stats = security.getSecurityStats();
  return c.json(stats);
});

// Secure webhook endpoint
app.post("/webhook", async (c) => {
  const clientIP = c.req.header("CF-Connecting-IP") ||
                   c.req.header("X-Forwarded-For") ||
                   c.req.header("X-Real-IP") ||
                   "unknown";

  const payload = await c.req.text();
  const headers = Object.fromEntries(
    Object.entries(c.req.headers).map(([k, v]) => [k.toLowerCase(), v])
  );

  const validation = await security.validateWebhook(payload, headers, clientIP);

  if (!validation.valid) {
    return c.json({ error: validation.error }, 400);
  }

  // Process the validated webhook
  try {
    // Your webhook handling logic here
    console.log("Processing secure webhook:", validation.payload.action);
    return c.json({ status: "processed" });
  } catch (error) {
    console.error("Webhook processing error:", error);
    return c.json({ error: "Processing failed" }, 500);
  }
});

export default app;

/*
Security Features Included:

1. **Signature Verification**
   - Timing-safe comparison to prevent timing attacks
   - Optional entropy checking for additional validation

2. **Replay Attack Protection**
   - Sliding window for delivery ID tracking
   - Automatic cleanup of old delivery records

3. **Rate Limiting**
   - Per-installation rate limiting
   - Automatic blocking with backoff

4. **IP Allowlisting**
   - GitHub's official webhook IP ranges
   - Custom IP range support

5. **Input Validation**
   - Payload structure validation
   - Size limits and sanitization
   - XSS protection for user inputs

6. **Audit Logging**
   - Comprehensive security event logging
   - Severity classification
   - Integration points for SIEM systems

7. **Monitoring**
   - Security statistics endpoint
   - Real-time metrics for monitoring

This provides enterprise-grade security for GitHub App webhooks.
*/
