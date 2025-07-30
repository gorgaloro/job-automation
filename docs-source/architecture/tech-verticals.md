# Tech Vertical Mapping

## Overview

This document outlines the AI-driven process used to assess and categorize companies by their technology verticals.

Using OpenAI, we analyze a company's description (website, job post, or other source) and score its relevance to a predefined list of tech verticals. For each company:

- Any **tech vertical with a score ≥ 60** is selected and pushed to the `Tech Focus` multi-select field in HubSpot.
- A **Tech Summary** text field is also updated with a human-readable explanation of each selected tech vertical, including score and rationale.

This allows us to:
- Automatically segment companies based on their tech footprint.
- Personalize outreach, event invites, or conference panels by tech category.
- Identify strategic alignment between companies and vertical-specific initiatives.

---

## HubSpot Fields

- **Tech Focus** (multi-select): Receives all tech verticals with scores ≥ 60.
- **Tech Summary** (text field): A formatted explanation including each selected vertical, its score, and rationale.  
  _Example:_  
  ```
  AI/ML (92): The company develops deep learning tools for cancer detection.  
  HealthTech / BioTech (88): Offers bioinformatics analytics for medical researchers.
  ```

---

## Tech Vertical Definitions

| Tech Area | Description |
|-----------|-------------|
| **AI/ML** | Companies building artificial intelligence, machine learning, or LLM-based solutions across domains. |
| **Cloud & DevOps** | Infrastructure platforms, cloud-native tools, and developer workflows that improve software delivery or system reliability. |
| **Cybersecurity** | Tools and platforms focused on digital protection, threat detection, encryption, and privacy. |
| **Fintech** | Technology-driven financial services including payments, banking, lending, insurance, and DeFi. |
| **Proptech** | Innovations in real estate, construction, and property management using technology to optimize buying, selling, and operating. |
| **HealthTech / BioTech** | Medical devices, diagnostics, patient care platforms, biotech research tools, and digital health applications. |
| **Climate / CleanTech** | Technologies addressing sustainability, emissions reduction, renewable energy, carbon removal, and circular economies. |
| **EdTech** | Educational tools and platforms for online learning, certifications, school management, and skill development. |
| **AdTech / MarTech** | Platforms for digital advertising, performance tracking, audience targeting, and marketing automation. |
| **E-commerce** | Platforms or tools enabling online retail, storefront management, product discovery, and payments. |
| **Robotics / Autonomous** | Companies building physical automation solutions — including robotics, drones, and autonomous vehicles. |
| **AR / VR / Metaverse** | Companies developing immersive 3D, augmented, or virtual environments for gaming, enterprise, or social use. |
| **Big Data / Analytics** | Infrastructure and platforms for data collection, storage, visualization, and decision support. |
| **IoT / Smart Devices** | Connected devices that gather data, provide automation, or enable remote interaction with the physical world. |
| **Mobility / E-Mobility** | Transportation platforms, micromobility tools, EV infrastructure, and ride-sharing or transit tech. |
| **Semiconductors / Hardware** | Firms designing chips, sensors, computing hardware, or core systems used by digital and physical tech products. |
| **SpaceTech / Aerospace** | Space exploration, satellite technologies, and aerospace innovation. |
| **3D Printing / Advanced Manufacturing** | Technologies for additive manufacturing, smart factories, and materials engineering. |
| **Blockchain / Web3** | Crypto, smart contracts, tokenized assets, decentralized finance, and other distributed ledger technologies. |
| **Social / Community Tech** | Platforms fostering community, collaboration, social connection, or digital belonging. |
| **Audio / Music Tech** | Music platforms, streaming tools, creator monetization, or innovations in audio experience. |
| **Gaming / eSports** | Game studios, tools for streamers, online competition platforms, or game-adjacent communities. |
| **Quantum Computing** | Next-gen computing platforms harnessing quantum physics to solve complex computational problems. |
| **LegalTech / RegTech** | Software tools for legal workflows, compliance tracking, and regulation-aware operations. |
| **AgTech / FoodTech** | Agricultural innovation, food systems automation, supply chain transparency, and lab-grown or alternative foods. |
| **Health & Wellness Tech** | Fitness apps, wellness tracking, telehealth, or digital platforms promoting well-being and lifestyle. |
| **Digital Infrastructure** | Core technologies like APIs, data pipelines, and connectivity platforms that enable other digital services. |
| **Enterprise B2B SaaS & Platforms** | Platforms providing business-critical services including CRMs, ERPs, collaboration tools, and middleware. |
| **Creative Tools & Creator Economy** | Platforms enabling content creation, monetization, audience building, and design innovation. |
| **Travel & Hospitality Tech** | Booking engines, hotel/airline management systems, travel logistics, and guest experience tools. |
| **Gig & Freelance Tech** | Platforms powering flexible work, independent contracting, service marketplaces, and workforce enablement. |

---

## Change Control & Updates

Tech verticals are stored in two systems:
- **Supabase Table**: used for AI scoring and internal logic.
- **HubSpot Property**: used for company records, filtering, and outreach.

### To add or modify a tech vertical:

1. **Update Supabase Table (`tech_areas`)**
   - Add a new row with `value`, `label`, and `description`.
   - Ensure the `value` matches HubSpot formatting exactly (case-sensitive).

2. **Update HubSpot**
   - Navigate to _Settings > Properties > Tech Focus_.
   - Add the same option to the multi-select field.
   - Keep label consistency with Supabase.

3. **Update Docusaurus Docs**
   - Open:  
     ```bash
     open -a TextEdit docs/tech-verticals.md
     ```
   - Update the markdown section under “Tech Vertical Definitions.”
   - Push changes to GitHub:
     ```bash
     git add docs/tech-verticals.md
     git commit -m "Update tech verticals with XYZ addition"
     git push
     ```

---

_This document is version controlled in GitHub and serves as the source of truth for tech area alignment across AI routines and HubSpot mapping._