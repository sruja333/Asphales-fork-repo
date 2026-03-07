🛡️ SurakshaAI – Multilingual Phishing Protection for India

SurakshaAI is a multilingual phishing detection system designed specifically for India’s diverse language ecosystem. It detects phishing attempts in Hindi, Tamil, Telugu, Bengali, Marathi, Gujarati, and code-mixed languages like Hinglish using a hybrid Machine Learning + Pattern Analysis approach.

🚨 The Problem

India is experiencing a massive rise in vernacular phishing attacks targeting users in regional languages.

400M+ Indian language speakers are vulnerable to phishing messages.

Most cybersecurity tools are built for English.

Phishing messages written in regional scripts bypass traditional filters.

Why Current Protections Fail

1. Telecom SMS Filters

Rely on English keyword lists such as OTP, verify, bank

Miss vernacular messages like:

तुरंत OTP भेजें
(Send OTP immediately)

2. Email & Browser Security

Focus mainly on URL reputation and domain blacklists

Ignore message content written in Indian scripts

3. Mobile OS Protection

Android and iOS warnings do not support Indian language models

No detection for Devanagari, Tamil, or Telugu scripts

➡️ Result: A huge cybersecurity gap where phishing in regional languages goes undetected.

💡 Our Solution

SurakshaAI is a vernacular-first phishing detection platform designed for India's multilingual digital ecosystem.

The system combines:

Machine Learning classification

Unicode script detection

Pattern-based phishing analysis

Contextual risk scoring

Real-time browser scanning

🌏 Supported Languages
Full Detection Coverage
Language	Script	Keywords
Hindi	Devanagari	60+
Tamil	Tamil Script	40+
Telugu	Telugu Script	30+
Bengali	Bengali Script	30+
Marathi	Devanagari	30+
Gujarati	Gujarati Script	30+
Code-Mixed Detection

SurakshaAI can detect phishing messages that mix English with regional languages, which is common in India.

Example:

आपका account verify करें - OTP भेजें immediately

Supported patterns include:

Hinglish

Tamil + English

Telugu + English

Mixed script communication

⚙️ Technical Architecture

SurakshaAI uses a hybrid detection engine composed of multiple layers.

1️⃣ Machine Learning Classifier

TF-IDF + Logistic Regression

Trained on 7,500+ multilingual phishing samples

85% detection accuracy

Sub-1ms inference time

Additional features:

Script-aware thresholds

Lower thresholds for vernacular languages

2️⃣ Vernacular Pattern Analyzer

Uses Unicode-based script detection to identify regional languages.

Script	Unicode Range
Devanagari	U+0900 – U+097F
Tamil	U+0B80 – U+0BFF
Telugu	U+0C00 – U+0C7F
Bengali	U+0980 – U+09FF

The analyzer extracts complete sentences (≥60 characters) instead of matching single keywords.

Example Phishing Indicators

Credential Requests

OTP
पासवर्ड
CVV

Urgency Tactics

तुरंत
உடனே
వెంటనే

Account Threats

बंद
निलंबित
தடை
3️⃣ Contextual Risk Scoring

Each message is assigned a risk score.

Risk Level	Score
Low	0 – 30%
Medium	30 – 60%
High	60 – 85%
Critical	85 – 100%

Threat categories include:

Credential phishing

Urgency manipulation

Suspicious links

Impersonation attacks

Fear tactics

4️⃣ Real-Time Protection

SurakshaAI includes a Chrome Extension that scans webpages in real time.

Features:

Highlights phishing phrases

Color-coded severity levels

Clickable explanations

Visual Indicators

🔴 Red → Critical threat

🟡 Yellow → High risk

🟠 Orange → Medium risk

5️⃣ Privacy-First Design

SurakshaAI prioritizes user privacy.

No persistent storage

Messages analyzed only in RAM

No message logging

Offline detection supported

🖥️ Current Prototype

Built during a 56-hour national hackathon, SurakshaAI currently includes:

Chrome Extension

Real-time webpage scanning

Highlights phishing phrases

Works on Gmail, WhatsApp Web, banking sites

Manifest V3 compliant

Desktop Application

Standalone phishing scanner that allows users to:

Paste suspicious messages

Upload text files

Scan messages offline

Hybrid Detection Engine
Layer	Technology
Primary	TF-IDF Logistic Regression
Secondary	Vernacular pattern analyzer
Optional	LLM analysis (Llama-3.1)
Fallback	Client-side regex detection
📊 Validation Results
Metric	Result
Overall Accuracy	85%
Phishing Detection Rate	90%
Code-Mixed Accuracy	100%
False Positive Rate	30%
Inference Speed	0.2ms avg

The system can process 5000+ messages per second.

🚀 Deployment Opportunities

SurakshaAI can integrate into multiple layers of India’s digital infrastructure.

Telecom SMS Filtering

Potential integration with telecom providers.

Possible partners:

Jio

Airtel

Vodafone Idea

Goal:

Detect phishing before SMS delivery

Fintech Fraud Protection API

Possible integration with payment platforms:

Paytm

PhonePe

Google Pay

SBI

HDFC Bank

Use cases:

UPI fraud detection

Message scanning

Banking app protection

Enterprise Email Security

Enterprise deployment options:

Email gateway plugin

Docker container

Cloud or on-premise deployment

Mobile OS Message Filtering

Future plans include:

Android SMS filtering service

iOS Message Filter extension

📈 Market Opportunity
Scale of Messaging in India
Metric	Value
SMS per year	150B+
Estimated phishing attempts	7.5B
Vernacular phishing messages	4.5B
Unserved Market

400M+ regional language users

High targeting of elderly users

Rural population with limited cybersecurity tools

🏆 What Makes SurakshaAI Unique

Vernacular-first detection
Built specifically for Indian scripts rather than translated English models.

Code-mixed language support
Handles real-world communication patterns like Hinglish.

Explainable AI warnings
Provides easy-to-understand explanations for non-technical users.

Offline detection capability
Ensures protection even without internet connectivity.

Telecom-scale architecture
Designed for high throughput and low latency.

🔬 Future Work

Planned improvements include:

Expanding multilingual phishing datasets

Training IndicBERT / mBERT models

Telecom-level deployment

Enterprise API scaling

Privacy-preserving federated learning

🤝 Contributions & Feedback

We welcome feedback from:

Cybersecurity professionals

NLP researchers

Telecom companies

Fintech platforms

Government cybersecurity agencies

📦 Demo

Available components:

Chrome Extension

Desktop Application

REST API Sandbox

For:

Enterprise pilots

Telecom integrations

Technical collaborations

Investment discussions
