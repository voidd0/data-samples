# data samples by vøiddo

Real rows from our own scrapers, so you can see the columns before you order data or run a scraper yourself.
Each file is exactly what one run returned, with no edits.

## computrabajo: accountant jobs in Monterrey, Mexico

| | |
|---|---|
| Files | [`computrabajo/mx-contador-monterrey-10.csv`](computrabajo/mx-contador-monterrey-10.csv), [`.json`](computrabajo/mx-contador-monterrey-10.json) |
| Rows | 10 job ads, 18 columns, UTF-8 |
| Source | mx.computrabajo.com search for "contador" in Monterrey, as listed on 2026-11-26 |
| Made with | [computrabajo-scraper](https://voiddo.com/go/apify/computrabajo-scraper/?src=gh) on Apify, input `{"countries":["mx"],"keywords":["contador"],"location":"Monterrey","includeDetails":true,"maxItems":10}` |

Columns: `jobId`, `title`, `company`, `city`, `region`, `country`, `workMode`, `salaryText`, `salaryMin`, `salaryMax`,
`salaryCurrency`, `salaryInterval`, `contractType`, `schedule`, `education`, `experienceYears`, `postedDate`, `url`.

All 10 rows have a salary, in MXN per month. "Importante empresa del sector" is how Computrabajo shows an employer
that hides its name.

Left out on purpose: the job description text, because it can carry a recruiter's name, email or phone. We checked
every kept text column for emails and phone numbers and found none.

The rows are public job ads as Computrabajo showed them on that day. We claim no rights in them; you are responsible
for how you use them, under the law where you use them and the rules of the site.

## want rows like these for your own search?

- **We run it for you:** [voiddo.com/data](https://voiddo.com/data/?src=gh). Write a site and a search, and we email
  you the file as CSV, Excel and JSON at a fixed price. You can ask for 50 rows from your search first, at no charge.
- **You run it yourself:** every scraper is on the [Apify Store](https://voiddo.com/scrapers/?src=gh), billed per
  result from your own Apify account.

Questions: data@voiddo.com
