# 🔐 Security Checklist – Personalized Recommendation System

This document outlines the security practices followed during the development of this recommendation system project, with a focus on safely handling secrets, database access, and deployment.

---

## ✅ Environment Variables

- All sensitive information (e.g., TMDb API key, MongoDB URI) is stored in a `.env` file.
- The `.env` file is excluded from version control via `.gitignore`.
- A `.env.example` file is included to help other developers replicate the environment without compromising secrets.

---

## ✅ Git and Secret Management

- `.env` is never committed to the repository.
- In case of accidental exposure, keys are rotated and Git history is cleaned using [`git filter-branch`](https://git-scm.com/docs/git-filter-branch) or [`BFG Repo-Cleaner`](https://rtyley.github.io/bfg-repo-cleaner/).
- Any exposed secret is considered compromised and replaced.

---

## ✅ MongoDB Atlas Access

- During development, access was temporarily opened to all IP addresses (`0.0.0.0/0`) for ease of testing.
- In production, the following practices are recommended:
  - Whitelist only specific IP addresses or server locations.
  - Create separate users for development and production environments.
  - Assign the minimal required privileges (principle of least privilege).

---

## ✅ TMDb API Usage

- The TMDb API key is loaded via environment variable and never hardcoded in the codebase.
- The system respects TMDb's rate limits (max 40 requests per 10 seconds).
- Results from the API are stored in MongoDB to avoid redundant calls.

---

## ✅ Frontend and Forms

- No API keys or sensitive credentials are embedded in frontend code or HTML forms.
- If a third-party service requires public tokens, usage is carefully controlled and documented.
- In production, any sensitive operation (e.g., sending email, storing user input) should be delegated to a secure backend.

---

## ✅ Key Rotation and Monitoring

- All API keys and database credentials are rotated immediately upon suspected exposure.
- It is recommended to integrate secret scanning tools like [GitGuardian](https://www.gitguardian.com/) or GitHub's secret scanning alerts in future iterations.

---

## ✅ Deployment Readiness

- Before deployment, ensure:
  - No secrets are exposed in frontend or public repos.
  - Database access is locked down to IPs or services.
  - Any cloud provider access keys are protected and have usage limits.

---
