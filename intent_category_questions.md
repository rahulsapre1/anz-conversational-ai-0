# ANZ Conversational AI - Intent Category Questions

This document contains sample questions for each intent category that the ANZ Conversational AI system should be able to handle. Questions are organized by assistant mode (Customer/Banker) and intent category (Automatable/Sensitive/Human-only).

## Customer Mode - Automatable Intents

| Intent | Question | Expected Behavior |
|--------|----------|------------------|
| **greeting** | Hello, can you help me with my ANZ account? | Provide friendly greeting and offer assistance |
| **greeting** | Hi there, what services does ANZ offer? | Respond with general information about ANZ services |
| **greeting** | Good morning, I'd like to know about banking options | Greet user and ask for specific banking needs |
| **general_conversation** | Can you tell me what the ANZ app can do? | Explain ANZ app features and capabilities |
| **general_conversation** | How does internet banking work at ANZ? | Describe internet banking functionality |
| **general_conversation** | What are the different ways I can bank with ANZ? | List available banking channels (app, online, branch, etc.) |
| **transaction_explanation** | What does a cash advance transaction mean? | Explain cash advance concept and implications |
| **transaction_explanation** | How do balance transfers work on ANZ credit cards? | Describe balance transfer process and fees |
| **transaction_explanation** | What's the difference between purchases and cash advances? | Explain different transaction types and their terms |
| **fee_inquiry** | What are the annual fees for ANZ credit cards? | List credit card fees and conditions |
| **fee_inquiry** | Are there any fees for using ATMs with my ANZ card? | Explain ATM fees and conditions |
| **fee_inquiry** | What fees apply when I make international transactions? | Detail international transaction fees |
| **account_limits** | What's the daily limit for cash advances on my credit card? | State cash advance limits |
| **account_limits** | How much can I transfer per day using internet banking? | Explain transfer limits and conditions |
| **account_limits** | Are there limits on how many transactions I can make? | Describe transaction limits |
| **card_dispute_process** | How do I dispute a transaction on my credit card? | Provide step-by-step dispute process |
| **card_dispute_process** | What should I do if I see unauthorized charges? | Guide through unauthorized transaction reporting |
| **card_dispute_process** | How long do I have to report a disputed transaction? | State dispute timeframes |
| **application_process** | How do I apply for a new credit card with ANZ? | Explain credit card application process |
| **application_process** | What documents do I need to open a business account? | List required documents for business accounts |
| **application_process** | How long does it take to get approved for a personal loan? | Describe loan approval timeline |

## Customer Mode - Sensitive Intents

| Intent | Question | Expected Behavior |
|--------|----------|------------------|
| **account_balance** | What's my current account balance? | Request authentication before providing balance |
| **account_balance** | How much money do I have in my savings account? | Escalate to authenticated channel for balance inquiry |
| **account_balance** | Can you show me my loan balance? | Guide user to secure channels for sensitive information |
| **transaction_history** | Show me my recent transactions | Request authentication for transaction history |
| **transaction_history** | What payments did I make last month? | Escalate to secure authenticated access |
| **transaction_history** | Can I see my account activity for the past week? | Guide to official ANZ channels for transaction viewing |
| **password_reset** | I forgot my online banking password, how do I reset it? | Provide secure password reset process |
| **password_reset** | How do I change my PIN for internet banking? | Guide through PIN change procedure |
| **password_reset** | I need to update my security questions | Explain security question update process |

## Customer Mode - Human-Only Intents

| Intent | Question | Expected Behavior |
|--------|----------|------------------|
| **financial_advice** | Should I invest in shares or keep my money in savings? | Immediately escalate to human advisor |
| **financial_advice** | What's the best way to pay off my credit card debt? | Escalate for personalized financial advice |
| **financial_advice** | How can I improve my credit score? | Route to human financial counselor |
| **complaint** | I'm unhappy with the service I received from your call center | Escalate to complaints handling team |
| **complaint** | I want to make a formal complaint about billing errors | Route to formal complaint process |
| **complaint** | The bank made a mistake with my account | Escalate for complaint investigation |
| **hardship** | I'm having trouble making my loan payments, can you help? | Connect to financial hardship support team |
| **hardship** | I've lost my job and can't afford my mortgage repayments | Escalate to hardship assistance specialists |
| **hardship** | Due to medical issues, I need assistance with my credit card payments | Route to hardship support services |
| **fraud_alert** | I think someone hacked my account | Immediately escalate to fraud team |
| **fraud_alert** | I received a suspicious email pretending to be from ANZ | Route to security/fraud investigation |
| **fraud_alert** | Someone stole my card and made unauthorized purchases | Escalate for urgent fraud handling |

## Banker Mode - Automatable Intents

| Intent | Question | Expected Behavior |
|--------|----------|------------------|
| **greeting** | Hello, I'm calling about a customer inquiry | Provide professional greeting and assistance |
| **greeting** | Good afternoon, I need information about ANZ policies | Respond professionally and offer help |
| **greeting** | Hi, can you help me understand our fee structure? | Greet and provide requested information |
| **general_conversation** | What are the current interest rates for home loans? | Provide current product information |
| **general_conversation** | How do our credit card rewards programs work? | Explain product features and benefits |
| **general_conversation** | Can you explain the overdraft policy? | Describe banking policies and procedures |
| **policy_lookup** | What's the bank's policy on fee waivers? | Look up and explain relevant policies |
| **policy_lookup** | How does ANZ handle financial hardship cases? | Provide policy information on hardship procedures |
| **policy_lookup** | What are the terms and conditions for business accounts? | Explain account terms and conditions |
| **process_clarification** | How do customers apply for hardship assistance? | Clarify application processes and steps |
| **process_clarification** | What's the process for disputing card transactions? | Explain dispute resolution procedures |
| **process_clarification** | How does the loan approval process work? | Describe loan approval workflow |
| **product_comparison** | What's the difference between ANZ credit cards? | Compare product features and benefits |
| **product_comparison** | How do our home loan products compare? | Provide product comparison information |
| **product_comparison** | Which account is better for small businesses? | Compare account options for specific customer segments |
| **compliance_phrasing** | How should I phrase information about credit card fees? | Provide compliant language guidance |
| **compliance_phrasing** | What's the compliant way to explain interest rates? | Guide on regulatory-compliant explanations |
| **compliance_phrasing** | How do I discuss target market determinations? | Explain compliant disclosure methods |
| **fee_structure** | What fees apply to international transactions? | Detail fee schedules and structures |
| **fee_structure** | How are credit card annual fees structured? | Explain fee calculation and conditions |
| **fee_structure** | What are the charges for business banking? | Provide business banking fee information |
| **eligibility_criteria** | What are the requirements for a personal loan? | List loan eligibility criteria |
| **eligibility_criteria** | Who qualifies for hardship assistance? | Explain hardship eligibility requirements |
| **eligibility_criteria** | What criteria must customers meet for credit cards? | Detail credit card qualification criteria |
| **documentation_requirements** | What documents do customers need for account opening? | List required documentation |
| **documentation_requirements** | What paperwork is required for loan applications? | Explain loan application documentation |
| **documentation_requirements** | What supporting documents are needed for hardship applications? | Detail hardship application requirements |

## Banker Mode - Sensitive Intents

| Intent | Question | Expected Behavior |
|--------|----------|------------------|
| **customer_specific_query** | Can you check this customer's account balance? | Request proper authentication and authorization |
| **customer_specific_query** | What transactions has this customer made recently? | Escalate for customer data access verification |
| **customer_specific_query** | Does this customer have any outstanding fees? | Route through secure customer data channels |

## Banker Mode - Human-Only Intents

| Intent | Question | Expected Behavior |
|--------|----------|------------------|
| **complex_case** | This customer has multiple accounts and complex financial issues | Escalate to senior banker or specialist |
| **complex_case** | We have a customer with legal disputes involving their accounts | Route to legal/compliance team |
| **complex_case** | This case involves potential money laundering concerns | Escalate to compliance and legal teams |
| **complaint_handling** | A customer is complaining about unfair treatment | Connect to complaints resolution team |
| **complaint_handling** | We have a formal complaint about billing errors | Route to formal complaint investigation |
| **complaint_handling** | Customer wants to escalate their dissatisfaction | Escalate to complaints management |
| **regulatory_question** | How do we handle AML compliance for this transaction? | Route to compliance experts |
| **regulatory_question** | What are the regulatory requirements for this product? | Escalate to regulatory compliance team |
| **regulatory_question** | Does this customer situation require ASIC notification? | Route to regulatory affairs specialists |

## Summary Statistics

| Mode | Category | Number of Intents | Total Questions |
|------|----------|-------------------|-----------------|
| Customer | Automatable | 7 | 21 |
| Customer | Sensitive | 3 | 9 |
| Customer | Human-only | 4 | 12 |
| Banker | Automatable | 9 | 27 |
| Banker | Sensitive | 1 | 3 |
| Banker | Human-only | 3 | 9 |
| **Total** | | **27** | **81** |

## Notes

- **Automatable intents**: Can be handled automatically by the AI system using knowledge base retrieval
- **Sensitive intents**: Require authentication/verification but can be handled by AI with proper safeguards
- **Human-only intents**: Must be immediately escalated to human representatives due to complexity, legal, or regulatory requirements
- Questions are designed to test the system's ability to correctly classify intents and route appropriately
- Expected behaviors reflect the system's routing decisions and response handling for each intent type