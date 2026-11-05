# inorikids.com

Static website for Inori Kids. Content is edited in **Pages CMS**; every save rebuilds the site and publishes it to Hostinger.

## How it fits together

| Folder | What's in it | Who edits it |
|---|---|---|
| `content/` | Project photos list, guides, FAQs, awards, contact details | You, through Pages CMS |
| `static/img/` | Photos (uploads from the CMS land here; JPG and PNG are converted to WebP automatically) | You, through Pages CMS |
| `src/` | Page templates, styles and the build script | Developer |

On every change to `main`, the GitHub Action **Build and publish** runs `src/build.py`, puts the finished site on the `live` branch and Cloudflare deploys it to inorikids.com.

## One-time setup

1. **Pages CMS:** go to https://app.pagescms.org, sign in with GitHub, choose this repository. Add collaborators (e.g. Hosung) under Settings → Collaborators.
2. **Cloudflare (hosting):** the Cloudflare Worker named `inorikids` serves inorikids.com. In Cloudflare → Workers & Pages → inorikids → Settings → Build, connect this repository with:
   - Branch: `live`
   - Build command: *(empty)*
   - Deploy command: `npx wrangler deploy`
   - Root directory: `/`
   The `wrangler.jsonc` file in `static/` is copied to the `live` branch and tells Cloudflare to serve the files as they are.

## Everyday editing

- **Add a project photo:** Pages CMS → Project gallery → add item → upload photo, caption, category → Save.
- **Write a guide:** Pages CMS → Guides and articles → Add → title, summary, photo, text → Save. Tick *Draft* to hold it back.
- **Change phone numbers or add the email address:** Pages CMS → Contact details and links.
- **Edit FAQs or awards:** Pages CMS → FAQs / Awards.

The site updates about 1–2 minutes after you press Save.

## Build locally

```
pip install -r requirements.txt
python src/build.py   # output in dist/
```
