/**
 * CloudflareCrawlerClient handles interaction with the Cloudflare Browser Rendering /crawl endpoint.
 */
class CloudflareCrawlerClient {
  /**
   * @param {string} accountId - Cloudflare Account ID
   * @param {string} apiToken - Cloudflare API Token with Browser Rendering - Edit permissions
   */
  constructor(accountId, apiToken) {
    this.accountId = accountId;
    this.apiToken = apiToken;
    this.baseUrl = `https://api.cloudflare.com/client/v4/accounts/${accountId}/browser-rendering/crawl`;
  }

  /**
   * Initiates a crawl job.
   * @param {Object} options - Crawl options
   * @param {string} options.url - The starting URL
   * @param {number} [options.limit] - Max pages to crawl
   * @param {number} [options.depth] - Max link depth
   * @param {string[]} [options.formats] - Output formats (html, markdown, json)
   * @param {boolean} [options.render] - Whether to render JS (default: true)
   * @returns {Promise<string>} - The job ID
   */
  async initiateCrawl(options) {
    const response = await fetch(this.baseUrl, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(options),
    });

    const data = await response.json();
    if (!data.success) {
      throw new Error(`Failed to initiate crawl: ${JSON.stringify(data.errors)}`);
    }

    return data.result; // This is the job_id
  }

  /**
   * Gets the status or results of a crawl job.
   * @param {string} jobId - The job ID
   * @param {Object} [queryParams] - Optional query parameters (limit, cursor, status)
   * @returns {Promise<Object>} - The job results/status
   */
  async getCrawlResults(jobId, queryParams = {}) {
    const url = new URL(`${this.baseUrl}/${jobId}`);
    Object.keys(queryParams).forEach(key => url.searchParams.append(key, queryParams[key]));

    const response = await fetch(url.toString(), {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${this.apiToken}`,
      },
    });

    const data = await response.json();
    if (!data.success) {
      throw new Error(`Failed to get crawl results: ${JSON.stringify(data.errors)}`);
    }

    return data.result;
  }

  /**
   * Polls for crawl job completion.
   * @param {string} jobId - The job ID
   * @param {number} [intervalMs=5000] - Polling interval in milliseconds
   * @param {number} [maxAttempts=60] - Maximum number of polling attempts
   * @returns {Promise<Object>} - The final job result
   */
  async waitForCompletion(jobId, intervalMs = 5000, maxAttempts = 60) {
    for (let i = 0; i < maxAttempts; i++) {
      // Use limit=1 for lightweight polling
      const result = await this.getCrawlResults(jobId, { limit: 1 });

      if (result.status !== 'running') {
        return result;
      }

      await new Promise(resolve => setTimeout(resolve, intervalMs));
    }
    throw new Error(`Crawl job ${jobId} did not complete within timeout`);
  }

  /**
   * Cancels a running crawl job.
   * @param {string} jobId - The job ID
   * @returns {Promise<boolean>}
   */
  async cancelCrawl(jobId) {
    const response = await fetch(`${this.baseUrl}/${jobId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${this.apiToken}`,
      },
    });

    const data = await response.json();
    return data.success;
  }
}

module.exports = CloudflareCrawlerClient;
