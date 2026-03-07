🛡️ SurakshaAI
Multilingual Phishing Protection for India

Detecting phishing attacks in Hindi, Tamil, Telugu, Bengali and other Indian languages — including code-mixed text like Hinglish — using a hybrid Machine Learning + Pattern Analysis system.

🚨 The Problem

India is facing a surge in vernacular phishing attacks targeting users who communicate in regional languages.

🇮🇳 400M+ Indian language users are exposed to phishing messages.

Most cybersecurity tools are English-centric.

Phishing messages in Hindi, Tamil, Telugu, Bengali, and mixed scripts bypass existing filters.

Why Current Systems Fail

Telecom SMS Filters

Built around English keyword blacklists

Miss messages like:
तुरंत OTP भेजें (Send OTP immediately)

Email & Browser Security

Focus only on URL reputation and domain blacklists

Ignore message content written in Indian scripts

Mobile OS Protection

No native models for Devanagari, Tamil, or Telugu

Regional language users receive little protection

➡️ Result: A massive cybersecurity gap in India's multilingual digital ecosystem.

💡 Our Solution

SurakshaAI is a multilingual phishing detection system designed specifically for India.

It combines:

Machine Learning models

Script-aware pattern detection

Contextual risk scoring

Real-time browser scanning

🌏 Languages Supported
Full Detection Support
Language	Script	Coverage
Hindi	Devanagari	60+ phishing keywords
Tamil	Tamil Script	40+ keywords
Telugu	Telugu Script	30+ keywords
Bengali	Bengali Script	30+ keywords
Marathi	Devanagari	30+ keywords
Gujarati	Gujarati Script	30+ keywords
Code-Mixed Language Detection

SurakshaAI detects mixed-language messages, which are extremely common in India.

Examples:

आपका account verify करें
OTP भेजें immediately

Supports:

Hinglish

Tamilglish

Telugu-English combinations

Mixed script patterns

⚙️ Technical Architecture

SurakshaAI uses a hybrid detection engine.

1️⃣ Machine Learning Classifier

TF-IDF + Logistic Regression

Trained on 7,500+ multilingual samples

85% accuracy across Indian languages

Sub-1ms inference time

Special features:

Script-aware thresholding

Lower detection threshold for vernacular languages

2️⃣ Vernacular Pattern Analyzer

Uses Unicode script detection:

Script	Unicode Range
Devanagari	U+0900–U+097F
Tamil	U+0B80–U+0BFF
Telugu	U+0C00–U+0C7F

Instead of simple keyword matching, SurakshaAI:

Extracts full sentences (≥60 characters)

Detects phishing patterns such as:

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

SurakshaAI assigns a risk score to each message.

Risk Level	Score
Low	0–30%
Medium	30–60%
High	60–85%
Critical	85–100%

Threat categories include:

Credential requests

Urgency manipulation

Suspicious links

Impersonation attacks

Fear tactics

Users receive bilingual explanations in Hinglish.

Example:

"Yeh message aapse OTP maang raha hai. Koi bhi asli bank OTP nahi maangta."

🧠 Key Features
🇮🇳 Vernacular-First Detection

Works directly on Indian scripts, not translated English.

🔀 Code-Mixed Language Support

Detects messages mixing English + Indian languages.

Example:

आपका account verify करें - OTP भेजें immediately
📖 Explainable AI

Users see clear explanations of why a message is dangerous.

🌐 Real-Time Browser Integration

Chrome extension highlights phishing phrases directly on webpages.

Color-coded alerts:

🔴 Critical

🟡 High

🟠 Medium

🔒 Privacy-First Design

No persistent storage

No message logging

Messages analyzed in RAM only

Offline detection supported

🖥️ Current Prototype

Built during a 56-hour national hackathon, SurakshaAI includes:

Chrome Extension

Real-time webpage scanning

Highlights phishing text

Works on Gmail, WhatsApp Web, banking sites

Manifest V3 compliant

Desktop Application

Standalone application that:

Scans pasted messages

Supports file uploads

Works offline

Hybrid Detection System
Layer	Technology
Primary	TF-IDF + Logistic Regression
Secondary	Vernacular pattern detection
Optional	LLM analysis (Llama-3.1)
Fallback	Client-side regex detection
📊 Validation Results
Metric	Result
Overall Accuracy	85%
Phishing Detection Rate	90%
Code-Mixed Accuracy	100%
False Positive Rate	30%
Inference Speed	0.2ms avg

System can process 5,000+ messages per second.

🚀 Deployment Potential

SurakshaAI can integrate across multiple layers of India's digital infrastructure.

📱 Telecom SMS Filtering

Carrier-level integration

Block phishing before delivery

Potential partners: Jio, Airtel, Vi

💳 Fintech Fraud Protection API

Integration with:

UPI apps

Banking apps

Payment platforms

Potential clients:

Paytm

PhonePe

Google Pay

SBI

HDFC Bank

🏢 Enterprise Email Security

Deployable as:

Email gateway plugin

Docker container

Cloud or on-premises

📲 Mobile OS Protection

Future integration with:

Android SMS filtering

iOS Message Filter Extensions

📈 Market Opportunity
Message Volume in India
Metric	Value
SMS per year	150B+
Phishing attempts	7.5B
Vernacular phishing	~4.5B
Unserved Market

400M+ regional language users

Elderly users frequently targeted

Rural users lack cybersecurity protection

🏆 What Makes SurakshaAI Different

✅ Built for Indian languages first
✅ Handles code-mixed communication
✅ Provides explainable AI warnings
✅ Works offline
✅ Designed for telecom-scale deployment

🔬 Future Work

We are currently exploring:

Training IndicBERT / mBERT models

Expanding phishing dataset

Telecom carrier integrations

Enterprise API deployment

Federated learning for privacy-preserving training

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

📬 Contact

Team: SurakshaAI
Location: India
Stage: Hackathon Finalist → Exploring commercialization

For:

Enterprise pilots

Telecom integrations

Technical collaborations

Investment discussions
