const puppeteer = require("puppeteer-extra");
const StealthPlugin = require("puppeteer-extra-plugin-stealth");

puppeteer.use(StealthPlugin());

async function scrapeGamma(url) {
  const browser = await puppeteer.launch({
    headless: true, // set false for debugging
    args: ["--no-sandbox", "--disable-setuid-sandbox"],
  });

  const page = await browser.newPage();

  try {
    await page.goto(url, { waitUntil: "networkidle2", timeout: 60000 });

    // Wait for content to load (any visible h1 or cards)
    await page.waitForSelector("h1, [data-card-id]", { timeout: 60000 });

    const data = await page.evaluate(() => {
      const content = [];

      // Recursive function to extract all text from headings, paragraphs, lists
      function traverse(node) {
        if (!node) return;
        const textTags = [
          "H1",
          "H2",
          "H3",
          "H4",
          "H5",
          "H6",
          "P",
          "LI",
          "SPAN",
          "DIV",
        ];
        if (textTags.includes(node.nodeName) && node.innerText?.trim()) {
          content.push(node.innerText.trim());
        }
        node.childNodes.forEach(traverse);
      }

      traverse(document.body);

      return {
        title: document.querySelector("h1")?.innerText || null,
        url: window.location.href,
        content,
      };
    });

    console.log(JSON.stringify(data));
  } catch (err) {
    console.error(JSON.stringify({ error: err.message }));
  } finally {
    await browser.close();
  }
}

// Read URL from command-line argument
const url = process.argv[2];
if (!url) {
  console.error(JSON.stringify({ error: "No URL provided" }));
  process.exit(1);
}

scrapeGamma(url);
