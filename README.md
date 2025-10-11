# System for Data Extraction from Payment Documents

This project provides a **secure, on-premise solution** for extracting structured financial data (e.g., vendor, date, total, line items) from images of receipts and invoices using state-of-the-art **Vision-Language Models (VLMs)**. Designed with privacy, modularity, and ease of deployment in mind, it enables small and medium businesses to automate financial document processing without relying on cloud services.

---

## ✨ Features

- **On-premise deployment**: Keep sensitive financial data within your infrastructure.
- **Vision-Language Model (Qwen-2.5-VL)**: High-accuracy, template-free extraction of structured JSON from diverse receipt layouts.
- **Dual processing modes**:
  - **On-premise**: Uses a local VLM instance (e.g., quantized Qwen-2.5-VL-7B).
  - **Cloud**: Optional integration with external inference providers (e.g., OpenRouter).
- **User-friendly web interface**: Upload receipts, view/edit extracted data, and manage API tokens.
- **RESTful API**: Secure token-based access for integration with accounting, tax, or ERP systems.
- **Modular microservice architecture**:
  - Read-write backend (uploads, processing)
  - Read-only backend (secure data querying)
- **Containerized with Docker**: Easy deployment via `docker-compose`; ready for Kubernetes.
- **Open-source & extensible**: Full transparency and freedom to customize or fine-tune models.

---

## 📦 Tech Stack

| Component        | Technology                          |
|------------------|-------------------------------------|
| **Frontend**     | React 18, Tailwind CSS, React Router|
| **Backend**      | FastAPI, PyTorch, HuggingFace       |
| **AI Model**     | Qwen-2.5-VL (7B, 4-bit quantized)   |
| **Database**     | PostgreSQL                          |
| **Storage**      | MinIO (S3-compatible)               |
| **Auth**         | JWT + Refresh Tokens, API Keys      |
| **Deployment**   | Docker, docker-compose              |

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- NVIDIA GPU (e.g., RTX 4070) with ≥12 GB VRAM *(for on-premise VLM)*
- At least 16 GB system RAM and 20 GB free disk space

> 💡 **Note**: The quantized `Qwen-2.5-VL-7B-Instruct-AWQ` model is used to enable inference on consumer-grade hardware.

### 1. Clone the Repository

```bash
git clone https://github.com/Lokhmat/ocr_backend.git
cd ocr_backend
```

### 2. Configure Environment

Copy the example env file and adjust settings (e.g., secrets, ports):

```bash
cp env_example.txt .env
# Edit .env as needed
```

### 3. Launch Services

```bash
docker-compose up --build
```

This starts:
- Frontend (`http://localhost:3000`)
- Read-write backend (`http://localhost:8000`)
- Read-only backend (`http://localhost:8001`)
- PostgreSQL + MinIO

### 4. Use the Application

1. Open **http://localhost:3000**
2. Register or log in
3. Upload receipt images (JPEG/PNG, ≤10 MB)
4. Choose **On-premise** or **Cloud** mode
5. View, edit, or download structured JSON results
6. Generate API tokens for external integrations

---

## 🔌 API Integration

After generating an API token in the UI, use it to access extracted data:

```bash
curl -H "Authorization: Bearer <your_token>" http://localhost:8001/api/list
curl -H "Authorization: Bearer <your_token>" "http://localhost:8001/api/image?image_id=123"
```

See full API documentation at `http://localhost:8000/docs` or via the **?** button in the UI.

---

## 🧪 Evaluation & Performance

- **Accuracy**: **97.68% F1 score** on SROIE2019 dataset (character-level evaluation)
- **Throughput**: ~10 docs/sec (scales horizontally)
- **Hardware**: Runs on **RTX 4070** (12 GB VRAM) with 4-bit quantization
- **Latency**: <2 sec per receipt (on supported hardware)

---

## 🛡️ Security

- All user passwords are **hashed & salted**
- JWT access + refresh tokens for web sessions
- API keys with configurable TTL (30–120 days or infinite)
- **Read-only API** isolates sensitive write operations
- No data leaves your infrastructure in on-premise mode

---

## 📈 Future Work

- Fine-tuning Qwen-VL on domain-specific receipts
- Distillation to lighter models (e.g., YOLO + OCR) using auto-labeled data
- Enhanced RBAC (admin/reviewer/user roles)
- Audit logging & alerting
- Kubernetes Helm chart for enterprise deployment

---

## 📄 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.
