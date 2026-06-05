const CloudflareCrawlerClient = require('../src/cloudflare_crawler');

// In a real application, these would come from environment variables
const ACCOUNT_ID = process.env.CLOUDFLARE_ACCOUNT_ID || 'your_account_id';
const API_TOKEN = process.env.CLOUDFLARE_API_TOKEN || 'your_api_token';

async function main() {
  const client = new CloudflareCrawlerClient(ACCOUNT_ID, API_TOKEN);

  try {
    console.log('Initiating crawl job...');
    const jobId = await client.initiateCrawl({
      url: 'https://example.com',
      limit: 5,
      formats: ['markdown'],
      render: false // Fast fetch if JS rendering isn't needed
    });

    console.log(`Crawl job initiated. ID: ${jobId}`);
    console.log('Waiting for completion...');

    const finalResult = await client.waitForCompletion(jobId);

    console.log(`Job Status: ${finalResult.status}`);
    console.log(`Total pages crawled: ${finalResult.total}`);

    // Fetch full results (without limit=1 used during polling)
    const fullResults = await client.getCrawlResults(jobId);

    fullResults.records.forEach((record, index) => {
      console.log(`\n--- Record ${index + 1} ---`);
      console.log(`URL: ${record.url}`);
      console.log(`Status: ${record.status}`);
      if (record.markdown) {
        console.log(`Content (first 100 chars): ${record.markdown.substring(0, 100)}...`);
      }
    });

  } catch (error) {
    console.error('Error during crawl:', error.message);
    if (ACCOUNT_ID === 'your_account_id' || API_TOKEN === 'your_api_token') {
      console.log('\nTip: Make sure to set CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN environment variables.');
    }
  }
}

main();
