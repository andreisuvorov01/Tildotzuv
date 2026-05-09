const CloudflareCrawlerClient = require('../src/cloudflare_crawler');

describe('CloudflareCrawlerClient', () => {
  let client;
  const accountId = 'test_account';
  const apiToken = 'test_token';

  beforeEach(() => {
    client = new CloudflareCrawlerClient(accountId, apiToken);
    global.fetch = jest.fn();
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  test('initiateCrawl sends correct request', async () => {
    const mockJobId = 'job_123';
    global.fetch.mockResolvedValueOnce({
      json: () => Promise.resolve({ success: true, result: mockJobId }),
    });

    const options = { url: 'https://example.com' };
    const jobId = await client.initiateCrawl(options);

    expect(global.fetch).toHaveBeenCalledWith(
      `https://api.cloudflare.com/client/v4/accounts/${accountId}/browser-rendering/crawl`,
      expect.objectContaining({
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${apiToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(options),
      })
    );
    expect(jobId).toBe(mockJobId);
  });

  test('getCrawlResults sends correct request', async () => {
    const mockResult = { status: 'completed', records: [] };
    global.fetch.mockResolvedValueOnce({
      json: () => Promise.resolve({ success: true, result: mockResult }),
    });

    const jobId = 'job_123';
    const result = await client.getCrawlResults(jobId, { limit: 10 });

    const expectedUrl = `https://api.cloudflare.com/client/v4/accounts/${accountId}/browser-rendering/crawl/${jobId}?limit=10`;
    expect(global.fetch).toHaveBeenCalledWith(
      expectedUrl,
      expect.objectContaining({
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${apiToken}`,
        },
      })
    );
    expect(result).toEqual(mockResult);
  });

  test('waitForCompletion polls until finished', async () => {
    client.getCrawlResults = jest.fn()
      .mockResolvedValueOnce({ status: 'running' })
      .mockResolvedValueOnce({ status: 'completed' });

    const jobId = 'job_123';
    const result = await client.waitForCompletion(jobId, 10, 5);

    expect(client.getCrawlResults).toHaveBeenCalledTimes(2);
    expect(result.status).toBe('completed');
  });

  test('cancelCrawl sends correct request', async () => {
    global.fetch.mockResolvedValueOnce({
      json: () => Promise.resolve({ success: true }),
    });

    const jobId = 'job_123';
    const success = await client.cancelCrawl(jobId);

    expect(global.fetch).toHaveBeenCalledWith(
      `https://api.cloudflare.com/client/v4/accounts/${accountId}/browser-rendering/crawl/${jobId}`,
      expect.objectContaining({
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${apiToken}`,
        },
      })
    );
    expect(success).toBe(true);
  });
});
