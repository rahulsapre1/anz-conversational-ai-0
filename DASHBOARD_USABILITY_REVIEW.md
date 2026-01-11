# Dashboard Usability Review Report
**Reviewer Perspective:** External Recruiter (No prior context)  
**Date:** January 11, 2026  
**Application:** ContactIQ - ANZ Conversational AI Dashboard  
**URL Reviewed:** http://localhost:8501

---

## Executive Summary

As a recruiter reviewing this dashboard for the first time, I found several usability issues that reduce clarity and impact. The dashboard appears professionally designed with comprehensive metrics, but lacks clear context, purpose explanation, and user guidance. The primary concern is **ambiguity about the dashboard's target audience and purpose** - it's unclear whether this is for end-users, internal analytics, or portfolio demonstration.

**Overall Assessment:** ⚠️ **Moderate - Needs Improvement**

---

## Key Findings

### 🔴 Critical Issues

#### 1. **Unclear Purpose and Target Audience**
- **Issue:** The title "ContactIQ KPI Dashboard" with subtitle "Analytics & Performance Metrics" doesn't clarify whether this is:
  - A portfolio demonstration of the candidate's work
  - An internal analytics tool for ANZ
  - A user-facing feature for customers/bankers
- **Impact:** Recruiters/evaluators cannot immediately understand what they're viewing or what it demonstrates
- **Evidence:** Title suggests internal analytics, but the sidebar still shows "Assistant Mode" selection, creating confusion

#### 2. **Lack of Context/Introduction**
- **Issue:** No introduction, "About" section, or explanation of what the dashboard demonstrates
- **Impact:** Viewers must infer the purpose from metrics alone
- **Missing Elements:**
  - No statement like "This dashboard demonstrates..." or "Portfolio Project:..."
  - No brief explanation of ContactIQ's purpose
  - No context about what these metrics represent in real-world terms

#### 3. **Technical Terminology Without Explanation**
- **Issue:** Many technical terms are used without definitions:
  - "Containment Rate" (what does this mean in practical terms?)
  - "Escalation Rate" (what triggers escalations?)
  - "Intent Classification" (what are intents?)
  - "Confidence Score" (confidence in what? How is it calculated?)
  - "Citation Coverage" (citations for what purpose?)
- **Impact:** Non-technical reviewers cannot fully understand the value being demonstrated
- **Example:** A chart showing "Intent Frequency Distribution" doesn't explain why this matters

#### 4. **Mixed User Context**
- **Issue:** The sidebar shows "Assistant Mode: Customer/Banker" selection even on the Dashboard page, which doesn't apply to dashboard viewing
- **Impact:** Creates confusion - why is mode selection visible if I'm viewing analytics?
- **Expected Behavior:** Mode selection should only appear on the Chat interface

### 🟡 Moderate Issues

#### 5. **Metrics Without Business Context**
- **Issue:** Metrics are displayed without explaining:
  - What good/bad values look like
  - Why each metric matters
  - How metrics relate to business outcomes
- **Examples:**
  - "81.1% Containment Rate" - Is this good? What's the target?
  - "89.30% Average Confidence" - What does confidence mean here?
  - "33.8% Failed Retrieval Rate" - Is this acceptable?

#### 6. **No Visual Hierarchy for Key Demonstrations**
- **Issue:** All metrics appear with equal weight - it's unclear which metrics are most important for demonstrating the candidate's capabilities
- **Impact:** Important achievements (e.g., high containment rate, citation system) are buried among many metrics
- **Suggestion:** Highlight key differentiators or achievements prominently

#### 7. **Missing Quick Wins Section**
- **Issue:** No summary section highlighting:
  - Key achievements/differentiators
  - Technical capabilities demonstrated
  - Business value delivered
- **Impact:** Recruiters must analyze all metrics to understand the value proposition

#### 8. **Dashboard Organization Could Be Improved**
- **Issue:** Sections flow logically but don't tell a story
- **Suggestion:** Group metrics by story (e.g., "System Performance", "Business Impact", "Technical Capabilities")

---

## What Works Well ✅

1. **Professional Visual Design:** Clean, branded interface with ANZ colors
2. **Comprehensive Metrics:** Extensive data coverage shows thorough thinking
3. **Good Data Visualization:** Charts are well-formatted and readable
4. **Technical Depth:** Shows sophisticated metrics (Risk × Value Matrix, Confidence Distribution)
5. **Real-time Data:** Dashboard appears to use actual interaction data

---

## Recommendations

### 🎯 High Priority (Must Fix)

#### 1. Add Clear Introduction/Context Banner
**Location:** Top of dashboard, below title  
**Content:**
```
📋 About This Dashboard
This dashboard demonstrates the analytics and performance monitoring capabilities 
of ContactIQ, an AI-powered conversational assistant for ANZ banking services.

Key Capabilities Demonstrated:
• Real-time interaction analytics and monitoring
• Intelligent intent classification and routing
• Confidence scoring and risk-based escalation
• Performance optimization tracking
• Citation and source tracking for transparency
```

#### 2. Add Glossary/Tooltips for Key Terms
**Implementation Options:**
- Info icons next to metric names that expand explanations
- Collapsible "Glossary" section at the top
- Hover tooltips on metric labels

**Key Terms to Define:**
- **Containment Rate:** Percentage of user queries resolved without human escalation
- **Escalation Rate:** Percentage of queries requiring human intervention
- **Intent Classification:** Automatic categorization of user queries (e.g., "fee_inquiry", "policy_lookup")
- **Confidence Score:** System's certainty level (0-100%) that its answer is accurate and appropriate
- **Citation Coverage:** Percentage of responses that include source citations

#### 3. Remove Mode Selection from Dashboard View
**Action:** Hide "Assistant Mode" radio buttons when viewing Dashboard page  
**Current Code Location:** `main.py` line 142 - condition already exists but may need adjustment  
**Expected:** Mode selector should only appear when `page == "💬 Chat"`

#### 4. Add "What This Demonstrates" Summary Card
**Location:** Top section, after introduction  
**Content:**
```
🎯 Capabilities Demonstrated

✅ End-to-end conversational AI system with RAG (Retrieval-Augmented Generation)
✅ Intelligent intent classification and routing
✅ Confidence-based escalation logic for risk management
✅ Comprehensive analytics and monitoring
✅ Citation tracking for transparency and compliance
✅ Performance optimization and bottleneck identification
```

### 🟡 Medium Priority (Should Fix)

#### 5. Add Context to Key Metrics
**Example Enhancement:**
Instead of just:
```
Containment Rate: 81.1%
```

Show:
```
Containment Rate: 81.1%
ℹ️ Percentage of queries resolved without human escalation.
   Target: >75% | Industry Average: 60-70%
```

#### 6. Reorganize Dashboard Sections
**Suggested Flow:**
1. **Introduction & Overview** (new)
2. **Executive Summary** (new - key metrics at a glance)
3. **System Performance** (Usage Metrics, Mode Breakdown, Time Trends)
4. **Business Impact** (Resolution Metrics, Escalation Analysis)
5. **Technical Deep Dive** (Intent Analysis, Confidence Metrics, Performance Metrics)
6. **Quality & Compliance** (Citation Coverage, Risk Matrix)

#### 7. Add Benchmark Indicators
**Implementation:** Color coding or indicators showing:
- Green: Above target/excellent
- Yellow: Within acceptable range
- Red: Needs attention

#### 8. Create "Quick Stats" Summary Cards
**Location:** Top of dashboard  
**Content:** 4-6 key metrics in large cards:
- Total Interactions
- Containment Rate (with indicator)
- Average Confidence
- Most Common Intent
- etc.

### 🔵 Low Priority (Nice to Have)

#### 9. Add "Demo Mode" Indicator
If this is a portfolio project, add a badge/indicator:
```
[DEMO] This is a portfolio demonstration project
```

#### 10. Add Export/Share Functionality
Allow exporting dashboard as PDF or sharing a snapshot

#### 11. Add Time Range Selector
Currently shows all data - add date range filters for focused analysis

---

## Specific Code Changes Needed

### 1. Add Introduction Section to Dashboard
**File:** `ui/dashboard.py`  
**Location:** After line 107 (after header, before metrics)  
**Action:** Insert introduction markdown with context

### 2. Fix Mode Selector Visibility
**File:** `main.py`  
**Location:** Around line 142  
**Action:** Ensure mode selector only shows on Chat page (verify condition)

### 3. Add Metric Tooltips/Help Text
**File:** `ui/dashboard.py`  
**Action:** Add `help` parameters to `st.metric()` calls or create expandable info sections

---

## User Journey Assessment

### Current Experience:
1. ✅ **Login:** Clear and straightforward
2. ✅ **Navigation:** Sidebar navigation is intuitive
3. ⚠️ **Dashboard Entry:** No context provided - user lands directly into metrics
4. ❌ **Understanding:** Must interpret technical metrics without guidance
5. ⚠️ **Value Recognition:** Important achievements may not be immediately obvious

### Improved Experience (After Fixes):
1. ✅ **Login:** Clear and straightforward
2. ✅ **Navigation:** Sidebar navigation is intuitive
3. ✅ **Dashboard Entry:** Clear introduction explains what they're viewing
4. ✅ **Understanding:** Glossary/tooltips help interpret metrics
5. ✅ **Value Recognition:** Summary section highlights key capabilities

---

## Comparison: Internal Analytics vs. Portfolio Demo

**Current State:** Dashboard appears as internal analytics tool
- Title suggests operational monitoring
- No indication it's a portfolio project
- Technical focus without business context

**Recommended State:** Dashboard clearly positioned as portfolio demonstration
- Introduction explains it's a demo/project
- Highlights capabilities being demonstrated
- Provides context for metrics and their significance

---

## Conclusion

The dashboard demonstrates strong technical capabilities and comprehensive analytics implementation. However, it suffers from **lack of context and unclear purpose**, which significantly impacts its effectiveness as a portfolio demonstration tool.

**Priority Actions:**
1. Add clear introduction/context section (5 minutes)
2. Add glossary/tooltips for key terms (15-30 minutes)
3. Remove mode selector from dashboard view (5 minutes)
4. Add "What This Demonstrates" summary (10 minutes)

**Estimated Total Time to Fix Critical Issues:** ~1 hour

These changes would transform the dashboard from a confusing analytics view into a clear portfolio demonstration that effectively showcases the candidate's capabilities.

---

## Reviewer Notes

**Strengths Observed:**
- Professional design and branding
- Comprehensive metric coverage
- Good data visualization
- Technical sophistication evident

**Questions Unanswered (for recruiters):**
- What problem does ContactIQ solve?
- What are the key technical achievements?
- How does this compare to industry standards?
- What was the candidate's specific role/contribution?

**Overall Impression:**
"This looks impressive technically, but I'm not sure what I'm supposed to take away from it. Is this internal ANZ analytics? Is it a demo? What does the candidate want me to notice?"
