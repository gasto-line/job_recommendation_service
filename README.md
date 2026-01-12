# Automatic Job Recommendation Service

_A cloud-native job recommendation platform combining classical NLP embeddings, LLM-based scoring, and user-driven feedback, deployed on AWS with a scalable on-demand inference architecture._

---

## Table of Contents
1. [Project Vision](#project-vision)
2. [Key Features](#key-features)
3. [System Architecture](#system-architecture)
4. [Getting Started](#getting-started)
5. [User Workflow](#user-workflow)
6. [Data & Model Details](#data--model-details)
7. [Cloud & Infrastructure Design](#cloud--infrastructure-design)
8. [Roadmap](#roadmap)
9. [Contributing](#contributing)
10. [Future Perspectives](#future-perspectives)

---

## Project Vision

Traditional job-alert platforms rely on static keyword filters and coarse metadata, often producing noisy or poorly aligned job suggestions.  
**Automatic Job Recommendation Service** addresses this limitation by combining:

- Structured user profiles
- NLP-based semantic representations
- LLM-driven reasoning
- Explicit user feedback

The system is designed as a **cloud-based recommendation service** where users actively participate in improving the relevance of job suggestions through scoring and profile refinement.

**The objective:**  
Deliver high-quality, personalized job recommendations while showcasing a production-oriented cloud and data infrastructure suitable for real-world ML workloads.

---

## Key Features

- **Authenticated User Sessions**  
  Secure user authentication and session management using **Supabase Auth**.

- **Structured Data Layer**  
  PostgreSQL (Supabase) with multiple relational tables and **RPC functions** to ensure controlled and efficient data access from the frontend.

- **Dual Recommendation Engines**  
  - FastText-based semantic similarity using cosine distance on job embeddings  
  - LLM-based scoring for deeper contextual reasoning  
  Users can dynamically choose the model from the UI.

- **On-Demand Inference Infrastructure**  
  FastText batch inference runs on **dynamically provisioned EC2 instances**, automatically started and terminated based on workload.

- **Persistent Backend API**  
  A long-running backend VM exposes **inference and orchestration endpoints** consumed by the Streamlit application.

- **Interactive Streamlit Interface**  
  Users can submit profiles, trigger scoring workflows, and review recommendations.

- **Feedback Loop**  
  User scores and comments are stored and reused to refine future recommendations.

---

## System Architecture

![System Architecture Diagram](https://github.com/user-attachments/assets/f3ac9a9e-b865-48f2-bbe4-43e36caf34f2)

**Main components:**
- Streamlit frontend
- Persistent backend API (FastAPI / Uvicorn)
- PostgreSQL database (Supabase)
- On-demand EC2 workers for FastText inference
- External job data providers
- AWS Route 53 for DNS and service exposure

---

## Getting Started

### Prerequisites
- Python 3.11+
- AWS account
- Supabase project
- Required API keys (job data providers, LLM providers)

### Environment Setup
1. Clone the repository
2. Create a Python virtual environment
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
