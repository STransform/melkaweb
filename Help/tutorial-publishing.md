# Publishing tutorials on MelkaTech

1. In **Blogs → Blog Categories**, add subjects such as Software Development, DevOps, Cloud, and Security.
2. In **Blogs → Blogs**, choose **Add New**. Enter a title, category, summary, and tutorial body. Cover images are optional.
3. Use Markdown for new tutorials. The editor provides heading, code, list, link, callout, table, screenshot upload, and preview controls. For example:

   ````markdown
   ## Prerequisites
   Install Docker before continuing.

   ## Start the application
   ```bash
   docker compose up --build
   ```

   > **Note:** Never commit real credentials to your repository.
   ````

4. Add tags, difficulty, prerequisites, and an author bio. For a series, give every lesson the same series name and set the lesson order.
5. **Save draft** keeps a tutorial private. **Publish tutorial** makes it appear in the public library at `/tutorials/`. Preview renders the body without publishing. Browser backups are local conveniences; use Save draft to persist writing to the server.
   A successful save opens the saved tutorial's edit page with a confirmation. After publishing, use **Open on the public portal** in the confirmation. Validation failures appear in an error summary and preserve your writing. Formatting opens a live preview; choose the code language before inserting a code block.
6. Existing articles retain their original HTML/text format after migration. Switch to Markdown only when converting the content. Slugs are generated automatically and remain unchanged when titles are edited.
7. Open the published tutorial, copy its URL, and share a short introduction on LinkedIn. Add `?utm_source=linkedin&utm_medium=social&utm_campaign=tutorial` to the link for source reporting. Deploy on a public HTTPS domain before sharing; localhost URLs cannot be read by LinkedIn or other visitors.
8. Approve reader comments in **Blog Comments**. Comment email addresses are never displayed publicly.
9. Open **Blogs → Tutorial analytics** for views, engaged reads, likes, source reporting, and pending comments. Reads are counted once per browser session per day. Engaged reads mean 30 seconds with the page visible. Cookies can be cleared, so these are approximate metrics, not verified people. Rate limiting uses Django's cache; configure a shared cache for multi-worker deployments.

The library supports text search, subject and difficulty filters, pagination, RSS (`/tutorials/feed.xml`), and a tutorial sitemap (`/tutorials/sitemap.xml`). Article pages include social metadata, canonical URLs, structured data, related tutorials, and tutorial-series links. The older numeric article URLs redirect to the new article addresses.

Readers can like articles without creating an account, share to LinkedIn or WhatsApp, or copy a canonical URL. Website likes are separate from LinkedIn reactions. RSS subscriptions work without email delivery or a third-party account; email newsletters and automated LinkedIn posting are not configured.
