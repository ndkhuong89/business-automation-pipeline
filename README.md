# Business Automation Pipeline

A simple end-to-end Business Automation System built with Python and Playwright.

---

## 🎥 Demo Video

[![Watch the demo](https://img.youtube.com/vi/l7QADoWKCq0/maxresdefault.jpg)](https://www.youtube.com/watch?v=l7QADoWKCq0)

▶ [Watch Demo Video](https://www.youtube.com/watch?v=l7QADoWKCq0)

---

## 🚀 Overview

This project automates business workflows including:

- Reading incoming emails
- Extracting order data from attachments
- Validating and processing orders
- Automatically creating orders in an ERP system using browser automation
- Generating and sending automated reports

The system helps reduce manual work and improve operational efficiency.

---

## 🔗 Related Project

This automation pipeline integrates with a separate ERP web application:

▶ [Mini ERP Web](https://github.com/ndkhuong89/mini-erp-web)

The ERP system is used as the target website for browser automation and order creation.

---

## ⚙️ Tech Stack

- Python
- Playwright (Browser Automation)
- APScheduler (Task Scheduling)
- IMAP Email Reader
- Pandas
- OpenPyXL
- Loguru
- SQLite

---

## 📁 Project Structure

```txt
src/
├── crons/
│   ├── cron_pipeline/
│   └── cron_daily_report/
│
├── modules/
│   ├── attachment_worker/
│   ├── auto_create_order/
│   ├── email_reader/
│   ├── generate_random_orders/
│   └── report_xlsx/
│
├── shared/
│   ├── db.py
│   ├── logger.py
│   └── products.py
│
├── config.py
└── main.py
```

---

## 🔄 Workflow

### 1. Email Monitoring

The system automatically checks incoming emails for new order files.

### 2. Attachment Processing

Order attachments are extracted and validated automatically.

### 3. ERP Automation

Using Playwright, the system logs into the ERP website and creates orders automatically through browser automation.

### 4. Report Generation

After processing, the system generates Excel reports including:

- Successful orders
- Failed orders
- Orders requiring manual review

### 5. Daily Reporting

The system can automatically send daily summary reports via email.

---

## ▶️ How to Run

### Install dependencies

```bash
pip install -r requirements.txt
```

### Install Playwright browser

```bash
playwright install
```

---

## ▶️ Run ERP Web Application

```powershell
.\venv\Scripts\Activate.ps1
python -m app
```

---

## ▶️ Run Automation Pipeline

```bash
python -m src.crons.cron_pipeline.cron_pipeline
```

---

## ▶️ Run Daily Report Cron

```bash
python -m src.crons.cron_daily_report.cron_daily_report
```

---

## 📊 Features

- Automated email processing
- Excel attachment parsing
- Order validation
- ERP browser automation
- Automatic report generation
- Daily scheduled reporting
- Logging and error tracking

---

## 🎯 Goal

This project demonstrates how repetitive business operations can be automated using Python and browser automation technologies.

The main objective is to reduce manual work and improve business efficiency through scalable automation workflows.

---

## 🧪 Demo Scenario

The demo video shows the complete workflow:

1. A new email containing order files arrives
2. The automation pipeline detects the email
3. Order data is extracted and validated
4. Orders are automatically created in the ERP system
5. A report email is generated and sent automatically

---

## 📌 Author

Built as a personal Business Automation Portfolio Project using Python and Playwright.