# data samples by vøiddo

Real rows from our own scrapers, so you can see the columns before you order data or run a scraper yourself.
Each file holds the rows one run returned. We leave out text fields that can name a person, such as job descriptions,
and change nothing else.

| Set | Rows | Files |
|---|---|---|
| [pracuj.pl: Python jobs in Warszawa, Poland](#pracujpl-python-jobs-in-warszawa-poland) | 50 | [CSV](pracuj-pl/python-warszawa-50.csv), [JSON](pracuj-pl/python-warszawa-50.json) |
| [computrabajo: accountant jobs in Bogotá, Colombia](#computrabajo-accountant-jobs-in-bogotá-colombia) | 25 | [CSV](computrabajo/co-contador-bogota-25.csv), [JSON](computrabajo/co-contador-bogota-25.json) |
| [computrabajo: accountant jobs in Monterrey, Mexico](#computrabajo-accountant-jobs-in-monterrey-mexico) | 10 | [CSV](computrabajo/mx-contador-monterrey-10.csv), [JSON](computrabajo/mx-contador-monterrey-10.json) |

## pracuj.pl: Python jobs in Warszawa, Poland

| | |
|---|---|
| Files | [`pracuj-pl/python-warszawa-50.csv`](pracuj-pl/python-warszawa-50.csv), [`.json`](pracuj-pl/python-warszawa-50.json) |
| Rows | 50 job offers, 14 columns, UTF-8 |
| Source | pracuj.pl search for "python" in Warszawa, as listed on 2026-11-26 (offers posted 2026-11-22 to 2026-11-26) |
| Made with | [pracuj-pl-scraper](https://voiddo.com/go/apify/pracuj-pl-scraper/?src=gh) on Apify, input `{"keywords":["python"],"location":"Warszawa","includeDetails":true,"maxItems":50}` |

Columns: `title`, `company`, `location`, `salaryText`, `salaryMin`, `salaryMax`, `salaryCurrency`, `salaryInterval`,
`positionLevels`, `contractTypes`, `workModes`, `postedAt`, `expiresAt`, `url`. In the CSV a list such as
`workModes` is joined with `; `.

30 of the 50 offers show a salary in PLN: 16 per month and 14 per hour (mostly B2B contracts). 38 offers are in
Warszawa or next to it; pracuj.pl puts 12 offers from other cities into the same search, and the file keeps them as
the site showed them. The scraper collects no recruiter names or phone numbers.

## computrabajo: accountant jobs in Bogotá, Colombia

| | |
|---|---|
| Files | [`computrabajo/co-contador-bogota-25.csv`](computrabajo/co-contador-bogota-25.csv), [`.json`](computrabajo/co-contador-bogota-25.json) |
| Rows | 25 job ads, 18 columns, UTF-8 |
| Source | co.computrabajo.com search for "contador" in Bogotá, as listed on 2026-11-26 |
| Made with | [computrabajo-scraper](https://voiddo.com/go/apify/computrabajo-scraper/?src=gh) on Apify, country `co`, keyword "contador", city Bogotá |

The same 18 columns as the Mexico file below. 19 of the 25 ads show a salary, in COP per month. Six ads come from
an employer that hides its name ("Importante empresa del sector").

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

## License

The rows are a compilation by vøiddo, shared under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The job
ads themselves belong to their publishers, and each row links to the original. They are public job ads as each site
showed them on the day of the run; you are responsible for how you use them, under the law where you use them and the
rules of the site.

## want rows like these for your own search?

- **We run it for you:** [voiddo.com/data](https://voiddo.com/data/?src=gh). Write a site and a search, and we email
  you the file as CSV, Excel and JSON at a fixed price. You can ask for 50 rows from your search first, at no charge.
- **You run it yourself:** every scraper is on the [Apify Store](https://voiddo.com/scrapers/?src=gh), billed per
  result from your own Apify account.

Questions: data@voiddo.com
