
# 📋 Job Board API Inventory

This document outlines common job boards and applicant tracking systems (ATS) with available APIs, their integration capabilities, and usage notes for the Job Search Automation System.

---

## ✅ Supported Job Boards and ATS with APIs

| Platform | API Available? | Notes & Use Cases |
|----------|----------------|-------------------|
| **Greenhouse** | ✅ [API Docs](https://developers.greenhouse.io/) | RESTful API. Common among startups. Easy job ingestion and parsing. |
| **Lever** | ✅ [API Docs](https://help.lever.co/hc/en-us/articles/360003802392-Lever-API-Introduction) | REST API with OAuth2. Supports job posting data and applicant tracking. |
| **Workday** | ⚠️ Partially (via clients) | No public API. Scraping job pages (e.g., `careers.company.com`) is common. |
| **SmartRecruiters** | ✅ [API Docs](https://dev.smartrecruiters.com/) | Job Ads API. Lightweight and structured. |
| **BambooHR** | ✅ [API Docs](https://documentation.bamboohr.com/docs) | HRIS-focused but supports job posting and application endpoints. |
| **Recruitee** | ✅ [API Docs](https://docs.recruitee.com/reference/introduction) | RESTful, easy to integrate, used by mid-size firms. |
| **JazzHR** | ✅ [API Docs](https://api.jazz.co/) | Limited to job data and posting. Good for small companies. |
| **Jobvite** | ⚠️ Partner-only | Requires enterprise or partner access. Use scraping for public boards. |
| **iCIMS** | ⚠️ Private API / OAuth | Closed APIs. Public job page scraping recommended. |
| **ADP Recruiting** | ⚠️ Enterprise only | API exists but is restricted. Public data requires scraping. |
| **Bullhorn** | ✅ [API Docs](https://bullhorn.github.io/rest-api-docs/) | Strong support for staffing workflows. Requires OAuth. |
| **Workable** | ✅ [API Docs](https://developer.workable.com/) | REST API available for jobs and candidates. |
| **Ashby** | ⚠️ Public job boards only | Scrape-friendly, no public API yet. |
| **Greenlight (JobScore)** | ⚠️ Minimal API | Some XML feeds possible. Scraping is fallback. |
| **Teamtailor** | ⚠️ Scraping needed | No accessible API, but job pages are structured. |
| **Indeed** | ❌ Deprecated | Job Search API retired. Use for analytics only. |
| **LinkedIn Jobs** | ❌ No API | No job posting or retrieval APIs available publicly. |

---

## 🛠️ Integration Recommendations

- **Prioritize Greenhouse, Lever, SmartRecruiters** for direct API integration.
- **Fallback to scraping** for Workday, iCIMS, Ashby when APIs aren’t exposed.
- **Map job fields** into your unified Supabase schema: `title`, `company`, `location`, `url`, `description`, etc.
- **Track job source** using a `source_type` field (e.g. `API`, `scraper`, `manual`).

---

Would you like to automate ingestion from these APIs into your Supabase database?
