
# 🔁 Regression Test Suite – Job Search Automation System

This document outlines end-to-end regression test cases that span multiple epics in the Job Search Automation System.

---

## ✅ RT-01: In-Person Event Contact Capture & Enrichment

**Objective**: Validate the mobile app’s ability to scan a LinkedIn QR code, generate an AI summary, create a HubSpot contact, tag event info, and queue follow-up.

**Linked Epics**:  
- Epic 9: Mobile Networking Assistant  
- Epic 3: Contact Identification & Enrichment  
- Epic 6: AI Scoring & Decision Support  
- Epic 4: Application Tracking

**Preconditions**:  
- LinkedIn profile is public  
- User profile is loaded in the mobile app  
- Event is identified (either GPS or manual tag)

**Test Steps**:
1. Scan LinkedIn QR code of a new person
2. System scrapes LinkedIn profile data (public)
3. AI generates a contact summary and suggested ice breakers
4. User saves contact, app tags location and event name
5. HubSpot record created (with source = “Event - [Location]”)
6. Task auto-created in HubSpot: “Follow up with [Name] from [Event]”

**Expected Result**:
- Contact record shows full name, role, org, enriched fields
- Location and event name correctly attached
- AI-generated summary and ice breaker saved to contact
- Task is visible in HubSpot with due date set

---

## ✅ RT-02: Job URL → Enrichment → Resume Match → Application

**Objective**: Validate the workflow from a pasted job URL all the way to submission, including resume scoring and deal creation.

**Linked Epics**:  
- Epic 5: Job Description Parsing & Intake  
- Epic 2: Company Enrichment  
- Epic 6: AI Scoring  
- Epic 1: Resume Optimization & Matching  
- Epic 8: Job Applications  
- Epic 4: Application Tracking

**Preconditions**:  
- Resume variants already exist  
- User profile is complete  
- Job URL is from a Greenhouse-hosted site

**Test Steps**:
1. Paste job URL into form
2. Job description is scraped and parsed
3. Company domain extracted → enrichment + tech verticals assigned
4. Resume scoring engine matches top resume variant (score > threshold)
5. Application is submitted
6. Deal created in HubSpot under company
7. Resume version used is tagged to the deal

**Expected Result**:
- JD stored as structured data  
- Enriched company and tech tags visible in HubSpot  
- Highest scoring resume variant selected and logged  
- Deal visible in HubSpot with date, source, resume version  
- Email follow-up queued for status monitoring

---

## ✅ RT-03: Manual Job Application With Resume Selection & HubSpot Sync

**Objective**: Simulate a manual job application where the user pastes the JD, selects a resume, and pushes to HubSpot.

**Linked Epics**:  
- Epic 1: Resume Optimization  
- Epic 5: JD Parsing  
- Epic 8: Job Applications  
- Epic 4: Application Tracking  
- Epic 2: Company Enrichment

**Preconditions**:  
- JD available in plain text  
- Resume library accessible  
- HubSpot connected

**Test Steps**:
1. User pastes JD into form
2. User selects resume manually (after preview or AI recommendation)
3. System creates Job + Company records
4. HubSpot Company record created or updated
5. HubSpot Deal created, linking to selected resume
6. Application status set to “Submitted”

**Expected Result**:
- Resume match score stored  
- Company enriched and tech verticals tagged  
- Contact + deal appear in HubSpot  
- Resume version tagged in deal properties

---

## ✅ RT-04: Alumni Contact Match Triggers Referral Workflow

**Objective**: Identify an alumni or past company contact at the target company and trigger referral logic.

**Linked Epics**:  
- Epic 3: Contact Enrichment  
- Epic 2: Company Enrichment  
- Epic 6: AI Decision Support  
- Epic 4: Application Tracking  
- Epic 7: Personal Brand Alignment

**Preconditions**:
- User has alumni history stored in profile  
- Company has LinkedIn employees or email domain

**Test Steps**:
1. Job description parsed → Company identified
2. Alumni matching runs (based on university + past employers)
3. Matching contact is found and enriched
4. HubSpot contact record created or updated
5. Deal flagged: “Referral Opportunity”

**Expected Result**:
- Contact record is linked to Deal  
- Referral flag triggers outreach task  
- Contact is tagged as “Potential Referrer”  

---

## ✅ RT-05: AI-Powered Job Prioritization Based on Personal Fit

**Objective**: Score multiple job descriptions and prioritize based on personal brand alignment and resume fit.

**Linked Epics**:  
- Epic 6: AI Scoring & Decision Support  
- Epic 7: Personal Brand & Opportunity Alignment  
- Epic 1: Resume Optimization

**Preconditions**:  
- At least 3 job descriptions stored  
- Resume versions exist  
- Personal Brand intake completed

**Test Steps**:
1. Run AI scoring job for each JD vs resume(s)
2. Compare each JD against brand alignment profile
3. Display final composite ranking
4. Highest ranked jobs marked “Priority” in UI and/or HubSpot

**Expected Result**:
- Each JD scored and explained (score + rationale)
- Final ranking displayed with icons or status
- Composite decision incorporates personal fit and skills alignment
