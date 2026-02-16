"""
Visit Value Index (VVI) Application - Enterprise Edition
Bramhall Consulting, LLC

VERSION: 2.7 - Enhanced Prescriptive Actions
Last Updated: February 16, 2026

Upgraded architecture:
- API-first design with local fallback
- Modular code structure
- Enhanced error handling
- Performance optimizations
- Production-ready deployment
- COMPLETE 16-scenario library built-in (S01-S16)
- Executive narratives for each scenario
- McKinsey-caliber visual design
- HIGHLY SPECIFIC prescriptive actions with concrete examples, metrics, and timelines
"""

from __future__ import annotations

import os
import io
import json
import base64
import requests
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# Configuration & Settings
# ============================================================

st.set_page_config(
    page_title="Visit Value Index (VVI) – Bramhall Consulting",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# VVI API Client
# ============================================================

class VVIAPIClient:
    """Client for VVI API with automatic fallback to local calculation"""
    
    def __init__(self, api_url: str = None, api_key: str = None):
        self.api_url = api_url or self._get_api_url()
        self.api_key = api_key or self._get_api_key()
        self.use_api = bool(self.api_url and self.api_key)
        
        if self.use_api:
            st.session_state.api_mode = "API"
        else:
            st.session_state.api_mode = "Local"
    
    def _get_api_url(self) -> Optional[str]:
        """Get API URL from secrets or environment"""
        try:
            return st.secrets.get("VVI_API_URL") or os.getenv("VVI_API_URL")
        except:
            return None
    
    def _get_api_key(self) -> Optional[str]:
        """Get API key from secrets or environment"""
        try:
            return st.secrets.get("VVI_API_KEY") or os.getenv("VVI_API_KEY")
        except:
            return None
    
    def assess(
        self,
        clinic_id: str,
        period: str,
        net_revenue: float,
        visit_volume: int,
        labor_cost: float,
        nrpv_target: float = 140.0,
        lcv_target: float = 85.0,
    ) -> Dict[str, Any]:
        """
        Calculate VVI assessment using API or local fallback
        
        Returns standardized result dict with:
        - metrics: {nrpv, lcv, swb_pct}
        - scores: {vvi, rf, lf}
        - tiers: {vvi, rf, lf}
        - scenario: {id, name, risk_level, focus_areas}
        - actions: {do_tomorrow, next_7_days, next_30_60_days, next_60_90_days}
        - expected_impact: {vvi_improvement, timeline, key_risks}
        - source: "api" or "local"
        """
        if self.use_api:
            try:
                return self._assess_via_api(
                    clinic_id, period, net_revenue, visit_volume, 
                    labor_cost, nrpv_target, lcv_target
                )
            except Exception as e:
                st.warning(f"API unavailable ({str(e)}), using local calculation")
                return self._assess_local(
                    clinic_id, period, net_revenue, visit_volume,
                    labor_cost, nrpv_target, lcv_target
                )
        else:
            return self._assess_local(
                clinic_id, period, net_revenue, visit_volume,
                labor_cost, nrpv_target, lcv_target
            )
    
    def _assess_via_api(
        self, clinic_id: str, period: str, net_revenue: float,
        visit_volume: int, labor_cost: float, 
        nrpv_target: float, lcv_target: float
    ) -> Dict[str, Any]:
        """Call VVI API"""
        response = requests.post(
            f"{self.api_url}/v1/vvi/assess",
            headers={
                "X-API-Key": self.api_key,
                "Content-Type": "application/json"
            },
            json={
                "clinic_id": clinic_id,
                "period": period,
                "metrics": {
                    "net_revenue": net_revenue,
                    "visit_volume": visit_volume,
                    "labor_cost": labor_cost
                },
                "benchmarks": {
                    "nrpv_target": nrpv_target,
                    "lcv_target": lcv_target
                },
                "options": {
                    "include_actions": True
                }
            },
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        result["source"] = "api"
        return result
    
    def _assess_local(
        self, clinic_id: str, period: str, net_revenue: float,
        visit_volume: int, labor_cost: float,
        nrpv_target: float, lcv_target: float
    ) -> Dict[str, Any]:
        """Local VVI calculation (fallback)"""
        # Calculate metrics
        nrpv = net_revenue / visit_volume
        lcv = labor_cost / visit_volume
        swb_pct = (labor_cost / net_revenue) * 100
        
        # Calculate scores
        rf_raw = nrpv / nrpv_target
        lf_raw = lcv_target / lcv
        rf_score = rf_raw * 100
        lf_score = lf_raw * 100
        
        vvi_raw = nrpv / lcv
        vvi_target = nrpv_target / lcv_target
        vvi_score = (vvi_raw / vvi_target) * 100
        
        # Determine tiers
        def tier_from_score(score):
            if score >= 100:
                return "Excellent"
            if 95 <= score < 100:
                return "Stable"
            if 90 <= score < 95:
                return "At Risk"
            return "Critical"
        
        vvi_tier = tier_from_score(vvi_score)
        rf_tier = tier_from_score(rf_score)
        lf_tier = tier_from_score(lf_score)
        
        # Get scenario ID
        scenario_map = {
            ("Excellent", "Excellent"): "S01",
            ("Excellent", "Stable"): "S02",
            ("Excellent", "At Risk"): "S03",
            ("Excellent", "Critical"): "S04",
            ("Stable", "Excellent"): "S05",
            ("Stable", "Stable"): "S06",
            ("Stable", "At Risk"): "S07",
            ("Stable", "Critical"): "S08",
            ("At Risk", "Excellent"): "S09",
            ("At Risk", "Stable"): "S10",
            ("At Risk", "At Risk"): "S11",
            ("At Risk", "Critical"): "S12",
            ("Critical", "Excellent"): "S13",
            ("Critical", "Stable"): "S14",
            ("Critical", "At Risk"): "S15",
            ("Critical", "Critical"): "S16",
        }
        scenario_id = scenario_map.get((rf_tier, lf_tier), "S16")
        
        # Full scenario library with detailed actions (ALL 16 SCENARIOS)
        scenario_library = {
            "S01": {
                "name": "Excellent Revenue / Excellent Labor",
                "risk_level": "Low",
                "executive_narrative": "Outstanding performance across both revenue and labor dimensions. This clinic is operating at or above benchmark on all key metrics, demonstrating strong clinical productivity, efficient workflows, and disciplined cost management. The primary focus is sustaining this excellence and preventing gradual drift.",
                "focus_areas": ["Sustain excellence", "Prevent drift", "Scale best practices"],
                "actions": {
                    "do_tomorrow": [
                        "Hold a 10-minute team huddle to recognize the excellent performance. Be specific: 'Our VVI score of [X] puts us in the top 10% nationally. This is the result of your work—tight workflows, strong coding, and disciplined staffing. Thank you.' Recognition prevents complacency and reinforces behaviors you want to keep.",
                        "Verify yesterday's performance basics held: All charts closed same-day? (Target: 95%+). Point-of-service collections reconciled? (Target: 90%+ of copays collected). Any schedule gaps or no-shows that hurt productivity? Track these daily—excellence requires daily discipline.",
                        "Ask your team: 'Where's our biggest risk to maintaining this performance today?' Common answers: key person out sick, new staff learning curve, unexpected volume surge, EMR downtime. Identify the risk and mitigate it before it becomes a problem. This daily risk check prevents surprises."
                    ],
                    "next_7_days": [
                        "Run a 90-minute time study on one busy session to confirm workflows remain tight. Use a stopwatch and simple spreadsheet. Track: patient arrival to rooming (target: <12 min), MA tasks per patient (target: 12-15 min), provider time (comparing to wRVU), checkout (target: <3 min). You should see minimal waste. If times are creeping up 10-15%, that's early drift—fix it now before it compounds.",
                        "Spot-check coding and charge capture for early revenue leakage signs. Pull 10 random charts from last week. Are E&M levels appropriate for complexity? (Compare to your top coder). Are all procedures captured and billed? Any denied claims that should have been caught? Missing charges are how revenue drift starts—catch it early with weekly audits.",
                        "Review schedule templates against actual demand patterns. Pull last 4 weeks of data: appointments scheduled vs. slots available by day/hour. Are you still matched to demand? Most clinics see seasonal shifts (back-to-school surge, winter illness, summer lull) that require template tweaks. Goal: maintain 85-90% template utilization without overloading providers or staff."
                    ],
                    "next_30_60_days": [
                        "Document your clinic's operational playbook in a simple 5-10 page guide. Include: staffing model (FTEs by role), daily huddle checklist, workflow standards (rooming process, checkout process), quality metrics, and key troubleshooting tips. Why? When you hire new staff or a manager, this is your training manual. It codifies excellence so it doesn't walk out the door when people leave.",
                        "Use your clinic as a teaching site for under-performing clinics in your system. Host 2-3 peer observers for a half-day visit. Walk them through your workflows, share your playbook, show them your huddle. Benefits: (1) Your team gets recognized as experts (great for morale), (2) Teaching forces you to articulate what makes you excellent, (3) You build relationships with peer clinics.",
                        "Conduct stay interviews or pulse surveys with key staff. Don't wait for exit interviews. Ask: What do you love about working here? What would you change? What would make you consider leaving? Any early burnout signs? Excellence is fragile—losing a great MA or front desk lead can crater performance. Know your people's satisfaction level and address concerns proactively."
                    ],
                    "next_60_90_days": [
                        "Review succession plans for front-line leaders and key roles. Who's your backup if your clinic manager leaves? If your lead MA retires? If your best coder quits? Identify 1-2 people for each critical role and create development plans. Send them to training, give them stretch projects, cross-train them. Succession planning isn't just for executives—it's critical for operational roles.",
                        "Stress-test your capacity for modest volume growth (5-10%) without harming VVI. If patient demand increases, can you handle it efficiently? Model it: What if you add 50 visits/month—do you need more staff? Can you flex schedules? What's your breaking point? Know your capacity ceiling so you can grow strategically without destroying the efficiency you've built.",
                        "Refine your KPI dashboards to keep leading indicators visible. Move beyond VVI to track: same-day chart closure %, POS collection %, schedule template utilization %, staff overtime hours, patient satisfaction, provider wRVU. Display these weekly in a simple one-page dashboard. Review in monthly leadership meetings. Leading indicators catch problems before they hurt VVI."
                    ]
                },
                "expected_impact": {
                    "vvi_improvement": "Sustain at 100+",
                    "timeline": "Ongoing",
                    "key_risks": ["Complacency leading to drift", "Hidden burnout", "Key-person risk"]
                }
            },
            "S02": {
                "name": "Excellent Revenue / Stable Labor",
                "risk_level": "Low",
                "executive_narrative": "Strong revenue performance with labor costs tracking slightly above optimal levels. Revenue capture and clinical productivity are excellent, but there are opportunities for modest labor efficiency gains. The focus is on gentle optimization without disrupting the revenue engine or compromising quality.",
                "focus_areas": ["Gentle labor optimization", "Protect revenue", "Incremental efficiency"],
                "actions": {
                    "do_tomorrow": [
                        "5-minute huddle celebrating strong revenue; share today's flow priorities.",
                        "Check yesterday's POS collections and registration accuracy.",
                        "Ask leaders where they see wasted steps or downtime in the day."
                    ],
                    "next_7_days": [
                        "Complete a light throughput review on a busy clinic session.",
                        "Identify 1-2 tasks that can be streamlined or re-sequenced.",
                        "Review overtime and schedule patterns for small inefficiencies."
                    ],
                    "next_30_60_days": [
                        "Tune staffing templates using recent volume and no-show patterns.",
                        "Cross-train select staff to flex across roles during peaks.",
                        "Standardize best practices into simple checklists."
                    ],
                    "next_60_90_days": [
                        "Target modest labor efficiency lift (2-4% LCV improvement).",
                        "Formalize quarterly review of staffing and throughput metrics.",
                        "Share efficiency wins across peer clinics."
                    ]
                },
                "expected_impact": {
                    "vvi_improvement": "3-6%",
                    "timeline": "60-90 days",
                    "key_risks": ["Over-tightening labor", "Ignoring inefficiencies", "Under-investing in engagement"]
                }
            },
            "S03": {
                "name": "Excellent Revenue / At Risk Labor",
                "risk_level": "Medium",
                "executive_narrative": "Excellent revenue performance is being undermined by emerging labor cost issues. While clinical productivity and revenue capture remain strong, labor efficiency is trending in the wrong direction—indicating workflow inefficiencies, overstaffing, or excessive premium labor usage. Corrective action is needed now to prevent further deterioration.",
                "focus_areas": ["Correct labor drift", "Protect revenue base", "Throughput restoration"],
                "actions": {
                    "do_tomorrow": [
                        "Stability huddle naming this as early-warning labor trend.",
                        "Review yesterday's overtime and float/PRN usage.",
                        "Ask staff to identify top 2 time-wasters in their day."
                    ],
                    "next_7_days": [
                        "Conduct simple time-study on one busy session.",
                        "Map MA/front-desk tasks to identify duplication.",
                        "Review staffing templates vs. actual volume by hour/day.",
                        "Spot-check chart closure timeliness and rework."
                    ],
                    "next_30_60_days": [
                        "Refine staffing templates to match demand more closely.",
                        "Clarify roles to reduce drift and handoff confusion.",
                        "Streamline 1-2 high-friction workflows.",
                        "Introduce basic labor KPI review into weekly huddles."
                    ],
                    "next_60_90_days": [
                        "Set modest labor efficiency target (4-8% LCV improvement).",
                        "Invest in cross-training for flexibility.",
                        "Reassess burnout through pulse checks or stay interviews."
                    ]
                },
                "expected_impact": {
                    "vvi_improvement": "5-9%",
                    "timeline": "60-90 days",
                    "key_risks": ["Drift into Critical labor", "Rising burnout", "Access declining"]
                }
            },
            "S04": {
                "name": "Excellent Revenue / Critical Labor",
                "risk_level": "High",
                "executive_narrative": "This is the most margin-damaging combination: strong revenue performance overshadowed by severe labor inefficiency. Labor costs are substantially outpacing targets, eroding profitability and masking operational instability. Immediate intervention is required to prevent deeper workforce issues such as turnover, burnout, or schedule failures.",
                "focus_areas": ["Emergency labor correction", "Protect revenue gains", "Prevent burnout cascade"],
                "actions": {
                    "do_tomorrow": [
                        "Call an emergency labor review meeting (operations lead, clinic manager, HR) for 1 hour. Bring last 4 weeks of payroll data, overtime reports, and staffing templates. Goal: understand where labor costs are bleeding—is it overtime (>10% of total hours?), premium labor (agency/PRN >5%?), or overstaffing?",
                        "Conduct immediate staffing audit: Print your staffing template vs. actual staff scheduled for today. Are you carrying 'ghost positions' (budgeted but unfilled roles you're still paying for)? Are you scheduling more FTEs than your volume justifies? Count: do you have more than 1 FTE per 200 visits/month?",
                        "Freeze all discretionary hiring and overtime approvals until analysis complete (24-48 hours). Require VP/Director approval for any overtime. This creates immediate pressure relief and prevents the bleeding from getting worse while you diagnose."
                    ],
                    "next_7_days": [
                        "Conduct a 2-hour workflow time study on your busiest session (typically Tue/Wed 8am-12pm). Assign someone with a stopwatch to shadow: track check-in time (target: <5 min), rooming time (target: <8 min), MA tasks per patient (target: 4-6 tasks, 12-15 min total), provider time per patient, checkout time (target: <3 min). Identify wasted motion—most clinics find 15-25 minutes of duplicated work per patient encounter.",
                        "Map every role's daily tasks on a whiteboard: Front desk (check-in, phones, checkout, scanning), MAs (rooming, vitals, orders, messages), and nurses (triage, refills, care coordination). Look for duplication (are 2 people doing the same task?), waste (tasks that don't add value), and imbalance (is one role overwhelmed while another has downtime?). Goal: find 3-5 tasks to eliminate or reassign.",
                        "Review all staffing templates against actual patient volume by day and hour. Create a simple Excel: Mon-Fri by hour, show scheduled FTEs vs. actual patient arrivals. Most clinics find they're overstaffed Mon/Fri AM (quiet) and understaffed Tue/Wed PM (slammed). Identify opportunities to flex staff to match demand—even 0.5 FTE shift saves $35K-$50K annually.",
                        "Run an overtime and premium labor analysis: Last 4 weeks, who worked overtime? How much? Why? (Unexpected volume? Staff callouts? Poor scheduling?) What did you spend on agency/PRN/float staff? Premium labor over 5% of total hours is a red flag. Create a weekly overtime tracking dashboard (simple spreadsheet) with manager accountability."
                    ],
                    "next_30_60_days": [
                        "Redesign workflows to eliminate labor waste. Start with your top 3 time-wasters from the time study. Common wins: (1) Batch phone refills instead of one-by-one (saves 2-3 MA hours/day), (2) Use MyChart for appointment reminders instead of phone calls (saves 1-2 front desk hours/day), (3) Pre-visit planning to front-load work and reduce day-of chaos (saves 15-20 min per complex visit), (4) Eliminate duplicate data entry between systems.",
                        "Implement strict overtime controls with daily manager approval and weekly VP review. Create an overtime approval form (1-pager: who, why, how many hours, alternatives considered). Set a hard target: reduce overtime from current level to <5% of total hours within 60 days. Track weekly and celebrate wins. Most clinics save $40K-$80K annually by cutting unnecessary overtime in half.",
                        "Cross-train 2-3 staff members to create flexibility and reduce reliance on premium labor (agency, PRN, float pool). Identify your most critical coverage gaps (usually front desk and MA roles) and train backups. Even 4-8 hours of cross-training per person creates massive flexibility. Goal: never pay $75/hour for agency staff when you have $28/hour regular staff sitting idle.",
                        "Bring in temporary productivity consultants if internal capacity is lacking. Consider: Huron, ECG, Kaufman Hall, or local operational consultants. A 2-week rapid diagnostic ($15K-$25K) often pays for itself 5x by finding hidden waste. They'll do time studies, benchmark analysis, and create a detailed action plan with ROI projections."
                    ],
                    "next_60_90_days": [
                        "Set aggressive but achievable labor cost reduction target: 10-15% LCV improvement within 90 days. For a $130/visit LCV, this means getting to $110-$117. That's ~1.5-2.0 FTEs on a 10-provider clinic ($105K-$140K annual savings). Break it into weekly milestones and track on a visible dashboard. Celebrate every 2-3% improvement.",
                        "Formalize new staffing standards based on your redesigned workflows. Create clear staffing ratios: Target 1 FTE per 180-220 visits/month depending on complexity. Document it in a simple 1-page 'Staffing Model' that shows FTEs by role and expected volume. Get leadership sign-off. Use it to guide all future hiring and scheduling decisions.",
                        "Monitor staff engagement and morale closely during the transformation. Labor optimization can feel threatening. Do monthly pulse surveys (3 questions: How's workload? Do you have what you need? Any concerns?). Hold skip-level conversations (VP talks directly to front-line staff). Address burnout signals immediately—losing a good MA costs $25K-$40K in recruitment and training.",
                        "Develop formal retention plan for key clinical and support staff. Identify your 'must-keep' employees (top performers, hard-to-replace roles). What would make them leave? What would make them stay? Common retention levers: flexibility (schedules), development (training budget), recognition (peer awards), and compensation (spot bonuses for high performers during tough times)."
                    ]
                },
                "expected_impact": {
                    "vvi_improvement": "10-18%",
                    "timeline": "3-6 months",
                    "key_risks": ["Revenue drops if access suffers", "Staff turnover accelerates", "Quality and safety incidents"]
                }
            },
            "S05": {
                "name": "Stable Revenue / Excellent Labor",
                "risk_level": "Low",
                "executive_narrative": "Outstanding labor efficiency with revenue performance meeting but not exceeding benchmarks. This clinic has mastered operational discipline and workforce productivity, creating a strong foundation for revenue growth. The opportunity lies in better charge capture, coding optimization, or strategic service line expansion without compromising labor excellence.",
                "focus_areas": ["Revenue opportunity capture", "Sustain labor discipline", "Grow margin"],
                "actions": {
                    "do_tomorrow": [
                        "Brief revenue huddle: celebrate labor discipline, focus on revenue opportunity.",
                        "Review yesterday's charge capture and coding accuracy.",
                        "Ask providers what administrative burden is slowing them down."
                    ],
                    "next_7_days": [
                        "Conduct focused revenue cycle review: coding, charge capture, denials.",
                        "Identify low-hanging fruit for E&M level optimization.",
                        "Review payer mix and identify any contract negotiation opportunities.",
                        "Spot-check documentation completeness for highest-volume CPTs."
                    ],
                    "next_30_60_days": [
                        "Launch provider documentation and coding training with real examples.",
                        "Implement real-time charge capture audit and feedback loop.",
                        "Explore ancillary service expansion if capacity and demand support it.",
                        "Formalize monthly revenue KPI review with providers."
                    ],
                    "next_60_90_days": [
                        "Target 3-7% revenue per visit improvement through better capture.",
                        "Develop provider scorecards with transparent wRVU and quality metrics.",
                        "Consider volume growth strategies if labor efficiency can support it."
                    ]
                },
                "expected_impact": {
                    "vvi_improvement": "4-8%",
                    "timeline": "60-90 days",
                    "key_risks": ["Provider resistance to documentation changes", "Coding compliance risk", "Payer audit exposure"]
                }
            },
            "S06": {
                "name": "Stable Revenue / Stable Labor",
                "risk_level": "Low",
                "executive_narrative": "Solid, sustainable performance across both dimensions with room for improvement in both areas. This clinic is neither in crisis nor optimized—it's in the comfortable middle. The risk is complacency and gradual drift. The opportunity is to pick one improvement lever and execute a focused initiative to move toward excellence.",
                "focus_areas": ["Incremental gains", "Prevent complacency", "Build momentum"],
                "actions": {
                    "do_tomorrow": [
                        "Balanced huddle recognizing stability and identifying one opportunity area.",
                        "Quick check on yesterday's metrics: any early warning signs?",
                        "Ask team: what's one thing we could do better this week?"
                    ],
                    "next_7_days": [
                        "Light operational review to identify 1-2 quick wins.",
                        "Spot-check both revenue (coding, charge capture) and labor (schedule fit, overtime).",
                        "Gather staff input on friction points or improvement ideas.",
                        "Confirm KPI dashboards are visible and reviewed weekly."
                    ],
                    "next_30_60_days": [
                        "Pick one improvement lever (revenue or labor) and execute a focused initiative.",
                        "Formalize a continuous improvement cadence (monthly reviews, quarterly goals).",
                        "Share best practices with peer clinics if in a system.",
                        "Invest in staff development or cross-training to build resilience."
                    ],
                    "next_60_90_days": [
                        "Target 2-5% VVI improvement through disciplined optimization.",
                        "Develop clear succession and coverage plans for key roles.",
                        "Consider piloting new service lines or access innovations if stable."
                    ]
                },
                "expected_impact": {
                    "vvi_improvement": "2-5%",
                    "timeline": "90+ days",
                    "key_risks": ["Complacency", "Gradual drift in either direction", "Missed growth opportunities"]
                }
            },
            "S07": {
                "name": "Stable Revenue / At Risk Labor",
                "risk_level": "Medium",
                "executive_narrative": "Revenue performance is holding steady, but labor costs are trending upward and approaching unsustainable levels. Workflow inefficiencies, overstaffing patterns, or excessive overtime are eroding margins. The clinic needs focused labor cost correction while protecting the revenue base and avoiding disruptions that could harm access or quality.",
                "focus_areas": ["Labor cost correction", "Protect revenue stability", "Improve throughput"],
                "actions": {
                    "do_tomorrow": [
                        "Focused labor huddle: acknowledge revenue is holding, name labor as priority.",
                        "Review yesterday's staffing, overtime, and premium labor usage.",
                        "Ask staff where time is being wasted or duplicated."
                    ],
                    "next_7_days": [
                        "Conduct workflow time-study on a typical busy session.",
                        "Map all clinical and administrative tasks; identify redundancy.",
                        "Review staffing templates against actual patient volume by day/hour.",
                        "Analyze overtime trends and identify root causes."
                    ],
                    "next_30_60_days": [
                        "Optimize staffing templates to match demand more precisely.",
                        "Streamline 2-3 highest-friction workflows (e.g., rooming, checkout, prior auth).",
                        "Implement tighter overtime approval and tracking process.",
                        "Cross-train staff to create flex capacity without adding FTEs."
                    ],
                    "next_60_90_days": [
                        "Target 5-8% labor cost reduction through efficiency (not layoffs if possible).",
                        "Formalize daily labor huddles and weekly KPI review.",
                        "Monitor staff morale and engagement to prevent attrition."
                    ]
                },
                "expected_impact": {
                    "vvi_improvement": "6-10%",
                    "timeline": "60-120 days",
                    "key_risks": ["Labor continues to drift into Critical", "Staff burnout", "Revenue slips if access declines"]
                }
            },
            "S08": {
                "name": "Stable Revenue / Critical Labor",
                "risk_level": "High",
                "executive_narrative": "Revenue is stable, but labor costs have reached crisis levels—substantially exceeding benchmarks and threatening financial viability. This is often caused by chronic overstaffing, inefficient workflows, or sustained reliance on premium labor. Immediate emergency intervention is required to bring labor costs under control without allowing revenue to decline.",
                "focus_areas": ["Emergency labor intervention", "Revenue protection", "Operational reset"],
                "actions": {
                    "do_tomorrow": [
                        "Crisis huddle: revenue is stable but labor is unsustainable.",
                        "Immediate staffing and overtime audit.",
                        "Freeze all discretionary spending and hiring."
                    ],
                    "next_7_days": [
                        "Daily labor review meetings with operations and finance.",
                        "Conduct rapid diagnostic: where is labor cost coming from?",
                        "Implement strict overtime controls with VP-level approval.",
                        "Begin provider discussions on documentation to protect revenue during labor changes."
                    ],
                    "next_30_60_days": [
                        "Redesign staffing model and templates to match volume.",
                        "Eliminate low-value tasks and administrative waste.",
                        "Rebuild core workflows for maximum efficiency.",
                        "Implement daily labor huddles and weekly trend reviews."
                    ],
                    "next_60_90_days": [
                        "Execute 12-15% labor cost reduction plan.",
                        "Formalize new operating standards and performance expectations.",
                        "Monitor staff engagement and retention closely.",
                        "Prevent revenue from slipping during labor transformation."
                    ]
                },
                "expected_impact": {
                    "vvi_improvement": "12-20%",
                    "timeline": "3-6 months",
                    "key_risks": ["Staff turnover", "Revenue decline", "Quality incidents", "Negative margin"]
                }
            },
            "S09": {
                "name": "At Risk Revenue / Excellent Labor",
                "risk_level": "Medium",
                "executive_narrative": "Outstanding labor efficiency is being undermined by revenue underperformance. This clinic is operationally lean and productive, but revenue per visit is falling short—indicating coding issues, charge capture gaps, unfavorable payer mix, or documentation problems. The focus must be on revenue recovery while maintaining hard-won labor discipline.",
                "focus_areas": ["Revenue recovery", "Maintain labor discipline", "Charge capture"],
                "actions": {
                    "do_tomorrow": [
                        "Revenue-focused huddle: celebrate labor efficiency, focus on revenue gaps.",
                        "Audit yesterday's charge capture and coding.",
                        "Ask providers: are we capturing all billable services?"
                    ],
                    "next_7_days": [
                        "Conduct comprehensive revenue cycle diagnostic.",
                        "Review coding levels, charge capture, and denial patterns.",
                        "Analyze payer mix and contract performance.",
                        "Provider documentation audit on top 10 CPT codes."
                    ],
                    "next_30_60_days": [
                        "Launch intensive provider coding and documentation training.",
                        "Implement real-time charge capture monitoring and feedback.",
                        "Optimize E&M levels and ancillary service billing.",
                        "Address top denial reasons and appeal backlog.",
                        "Review contracts and identify renegotiation opportunities."
                    ],
                    "next_60_90_days": [
                        "Target 5-10% revenue per visit improvement.",
                        "Formalize provider scorecards with financial transparency.",
                        "Consider service line expansion if capacity supports it.",
                        "Maintain labor discipline while growing revenue."
                    ]
                },
                "expected_impact": {
                    "vvi_improvement": "7-12%",
                    "timeline": "60-120 days",
                    "key_risks": ["Revenue continues to slide", "Provider resistance", "Compliance issues"]
                }
            },
            "S10": {
                "name": "At Risk Revenue / Stable Labor",
                "risk_level": "Medium",
                "executive_narrative": "Revenue performance is declining while labor costs remain stable but could drift if not monitored. This clinic needs a dual focus: aggressive revenue improvement through better coding, charge capture, and billing while maintaining labor cost discipline. The risk is that fixing revenue problems could inadvertently cause labor costs to rise.",
                "focus_areas": ["Revenue prioritization", "Labor efficiency maintenance", "Balanced recovery"],
                "actions": {
                    "do_tomorrow": [
                        "Dual-focus huddle: revenue needs attention, labor is okay.",
                        "Yesterday's revenue audit: charge capture, coding, collections.",
                        "Quick labor check to ensure no drift while fixing revenue."
                    ],
                    "next_7_days": [
                        "Revenue cycle deep-dive: identify top 3 revenue leakage points.",
                        "Provider documentation spot-checks.",
                        "Review labor metrics to ensure stability during revenue push.",
                        "Analyze denial patterns and payer mix."
                    ],
                    "next_30_60_days": [
                        "Execute revenue improvement plan (coding training, charge capture tech).",
                        "Maintain labor discipline with ongoing efficiency monitoring.",
                        "Address billing workflow gaps.",
                        "Provider engagement on financial performance."
                    ],
                    "next_60_90_days": [
                        "Target 4-8% VVI improvement primarily through revenue gains.",
                        "Balance revenue growth with labor cost control.",
                        "Prevent labor from drifting while focused on revenue."
                    ]
                },
                "expected_impact": {
                    "vvi_improvement": "5-9%",
                    "timeline": "90+ days",
                    "key_risks": ["Revenue slides further", "Labor drifts during revenue focus", "Provider burnout"]
                }
            },
            "S11": {
                "name": "At Risk Revenue / At Risk Labor",
                "risk_level": "High",
                "executive_narrative": "Dual performance concerns with both revenue and labor trending in the wrong direction. This clinic is experiencing simultaneous revenue leakage and labor inefficiency, creating a compounding margin problem. Leadership must triage priorities, execute parallel improvement plans, and prevent further deterioration on either dimension. Without intervention, this scenario rapidly degrades into crisis.",
                "focus_areas": ["Dual stabilization", "Prevent further decline", "Triage priorities"],
                "actions": {
                    "do_tomorrow": [
                        "Dual-threat huddle: both revenue and labor need attention.",
                        "Quick assessment: which is worse and needs immediate focus?",
                        "Yesterday's metrics review for both dimensions."
                    ],
                    "next_7_days": [
                        "Triage decision: stabilize revenue first or labor first based on severity.",
                        "Daily dual-metric huddles (revenue and labor).",
                        "Rapid diagnostics on both revenue cycle and labor efficiency.",
                        "Identify quick wins that improve both (e.g., better scheduling reduces labor and increases revenue)."
                    ],
                    "next_30_60_days": [
                        "Execute parallel improvement plans with clear ownership.",
                        "Revenue: coding training, charge capture, denials.",
                        "Labor: staffing templates, workflow efficiency, overtime control.",
                        "Weekly steering committee to monitor both tracks."
                    ],
                    "next_60_90_days": [
                        "Target 8-15% combined VVI improvement.",
                        "Prevent slide into Critical on either dimension.",
                        "Build sustainable operating discipline for both revenue and labor."
                    ]
                },
                "expected_impact": {
                    "vvi_improvement": "8-15%",
                    "timeline": "3-6 months",
                    "key_risks": ["One or both slide to Critical", "Team overwhelm", "Competing priorities"]
                }
            },
            "S12": {
                "name": "At Risk Revenue / Critical Labor",
                "risk_level": "Critical",
                "executive_narrative": "A dangerous combination of declining revenue and critical labor cost overruns that threatens financial viability. Labor costs are substantially exceeding benchmarks while revenue underperforms, creating severe margin pressure. This requires immediate crisis intervention on labor while simultaneously stabilizing revenue to prevent complete operational failure.",
                "focus_areas": ["Labor crisis mode", "Revenue triage", "Operational stabilization"],
                "actions": {
                    "do_tomorrow": [
                        "Crisis huddle: labor is critical, revenue is at risk.",
                        "Immediate labor intervention takes priority.",
                        "Protect revenue from further decline during labor reset."
                    ],
                    "next_7_days": [
                        "Daily crisis management meetings.",
                        "Emergency labor cost reduction plan.",
                        "Revenue protection plan (maintain coding quality during turbulence).",
                        "Communicate clearly with staff and providers about situation."
                    ],
                    "next_30_60_days": [
                        "Execute labor transformation (redesign staffing, workflows).",
                        "Stabilize revenue cycle basics (charge capture, denials).",
                        "Prevent further decline on both dimensions.",
                        "Weekly leadership reviews with clear accountability."
                    ],
                    "next_60_90_days": [
                        "Bring labor back to Stable (10-15% reduction).",
                        "Prevent revenue from sliding to Critical.",
                        "Build foundation for future recovery.",
                        "Address staff morale and retention."
                    ]
                },
                "expected_impact": {
                    "vvi_improvement": "15-25%",
                    "timeline": "6-12 months",
                    "key_risks": ["Financial viability threatened", "Staff exodus", "Quality and safety events"]
                }
            },
            "S13": {
                "name": "Critical Revenue / Excellent Labor",
                "risk_level": "High",
                "executive_narrative": "Despite excellent labor efficiency, revenue performance has fallen to crisis levels—substantially below benchmark and threatening the clinic's financial sustainability. This indicates severe problems with coding, charge capture, payer contracts, or case mix. Emergency revenue intervention is required while protecting the operational excellence that has been achieved on the labor side.",
                "focus_areas": ["Revenue emergency", "Protect labor excellence", "Financial viability"],
                "actions": {
                    "do_tomorrow": [
                        "Revenue crisis huddle with leadership.",
                        "Immediate revenue cycle audit.",
                        "Maintain labor discipline while addressing revenue crisis."
                    ],
                    "next_7_days": [
                        "Daily revenue recovery meetings.",
                        "Emergency coding and documentation intervention.",
                        "Charge capture technology deployment if needed.",
                        "Denial management acceleration.",
                        "Contract review for immediate renegotiation opportunities."
                    ],
                    "next_30_60_days": [
                        "Intensive provider documentation training and coaching.",
                        "Real-time charge capture audits with daily feedback.",
                        "Revenue cycle process redesign.",
                        "Consider service line adjustments or payer mix changes.",
                        "Maintain labor efficiency throughout revenue transformation."
                    ],
                    "next_60_90_days": [
                        "Target 12-20% revenue per visit improvement.",
                        "Restore financial sustainability.",
                        "Prevent labor from drifting during revenue crisis.",
                        "Build long-term revenue discipline."
                    ]
                },
                "expected_impact": {
                    "vvi_improvement": "15-25%",
                    "timeline": "6-12 months",
                    "key_risks": ["Clinic closure consideration", "Provider departures", "Access reduction"]
                }
            },
            "S14": {
                "name": "Critical Revenue / Stable Labor",
                "risk_level": "High",
                "executive_narrative": "Critical revenue underperformance despite stable labor costs creates severe margin pressure and questions about long-term viability. Revenue per visit is substantially below benchmark, indicating systemic problems with clinical documentation, coding, charge capture, or payer relationships. This requires emergency revenue cycle transformation while preventing labor costs from drifting during the crisis.",
                "focus_areas": ["Revenue emergency response", "Labor stability", "Financial rescue"],
                "actions": {
                    "do_tomorrow": [
                        "Revenue crisis declaration with full leadership team.",
                        "Yesterday's revenue audit with fine-tooth comb.",
                        "Protect labor stability during revenue emergency."
                    ],
                    "next_7_days": [
                        "Daily revenue recovery war room.",
                        "Emergency provider coding education.",
                        "Charge capture technology and process fixes.",
                        "Billing and collections acceleration.",
                        "Monitor labor to prevent drift during crisis focus."
                    ],
                    "next_30_60_days": [
                        "Complete revenue cycle transformation.",
                        "Provider financial performance transparency and accountability.",
                        "Payer contract optimization.",
                        "Service line profitability analysis.",
                        "Maintain labor cost discipline."
                    ],
                    "next_60_90_days": [
                        "Achieve 15-25% revenue improvement to restore viability.",
                        "Build sustainable revenue capture culture.",
                        "Prevent labor from becoming a new problem area."
                    ]
                },
                "expected_impact": {
                    "vvi_improvement": "18-28%",
                    "timeline": "6-12 months",
                    "key_risks": ["Financial insolvency", "Clinic closure", "Provider mass exodus"]
                }
            },
            "S15": {
                "name": "Critical Revenue / At Risk Labor",
                "risk_level": "Critical",
                "executive_narrative": "A severe dual crisis with critical revenue underperformance and deteriorating labor efficiency. Revenue is substantially below benchmark while labor costs are rising, creating a dangerous margin squeeze from both directions. This clinic is in survival mode and requires immediate executive intervention with parallel emergency actions on revenue and labor to restore viability.",
                "focus_areas": ["Dual emergency", "Triage and stabilize", "Survival mode"],
                "actions": {
                    "do_tomorrow": [
                        "Full crisis mode: both revenue and labor critical/at-risk.",
                        "Emergency leadership meeting to assess viability.",
                        "Immediate triage: which crisis is more severe?"
                    ],
                    "next_7_days": [
                        "Daily crisis management with clear decision authority.",
                        "Simultaneous emergency action on revenue and labor.",
                        "Revenue: charge capture, coding, collections.",
                        "Labor: overtime freeze, staffing adjustments.",
                        "Transparent communication with all stakeholders."
                    ],
                    "next_30_60_days": [
                        "Execute parallel recovery plans with weekly milestones.",
                        "Revenue transformation (coding, billing, contracts).",
                        "Labor optimization (staffing, workflows, efficiency).",
                        "Consider service line closures or consolidation if needed.",
                        "Monthly board/leadership review of recovery progress."
                    ],
                    "next_60_90_days": [
                        "Achieve minimum 20% VVI improvement to restore viability.",
                        "Build sustainable operating model.",
                        "Address staff morale and retention aggressively.",
                        "Prepare contingency plans if recovery insufficient."
                    ]
                },
                "expected_impact": {
                    "vvi_improvement": "20-35%",
                    "timeline": "9-18 months",
                    "key_risks": ["Clinic closure", "Service line elimination", "Mass staff/provider turnover", "Safety events"]
                }
            },
            "S16": {
                "name": "Critical Revenue / Critical Labor",
                "risk_level": "Critical",
                "executive_narrative": "The most severe scenario: catastrophic underperformance on both revenue and labor dimensions. Revenue is substantially below benchmark while labor costs are grossly exceeding targets, creating unsustainable losses. This clinic faces an existential crisis requiring immediate assessment of viability, executive-level intervention, and comprehensive operational transformation. Without dramatic improvement, closure or consolidation may be necessary.",
                "focus_areas": ["Survival", "Complete operational reset", "Viability assessment"],
                "actions": {
                    "do_tomorrow": [
                        "Convene emergency executive session (CEO/COO, CFO, CMO, VP Operations) for 2 hours. Bring 6 months of financials, last month's detailed P&L, staffing data, and volume trends. Make the go/no-go decision: Is this clinic salvageable? If margin is <-15% and declining, closure may be more responsible than prolonged losses. If you commit to recovery, you need full executive sponsorship and resources.",
                        "If continuing operations: Declare crisis mode with daily war room meetings (7:30am, 30 minutes, standing room only). Attendees: clinic manager, operations lead, revenue cycle director, HR. Agenda: Yesterday's numbers (visits, revenue, labor hours, issues), today's priorities, roadblocks needing executive clearance. This is not a 90-day plan—this is daily triage until you stop the bleeding.",
                        "Implement immediate emergency actions on both fronts: REVENUE: Pull yesterday's charges—are they all submitted? Any missing? Audit top 5 providers' coding from last week—are E&M levels too low? LABOR: Print today's schedule vs. staff scheduled—are you overstaffed for actual volume? Send people home if census is light (pay them, but stop the work). What's your overtime situation? Stop it today except for true emergencies requiring VP approval."
                    ],
                    "next_7_days": [
                        "Hold daily crisis management meetings with brutal honesty and clear accountability. Track 5 metrics daily: (1) Visits completed vs. scheduled, (2) Gross charges submitted, (3) Labor hours worked vs. budgeted, (4) Overtime hours, (5) Cash collected. Post them on a whiteboard visible to everyone. Celebrate any day that's better than the day before. You need daily wins to build momentum.",
                        "Execute emergency revenue capture actions: (1) Coding blitz: Revenue cycle team audits every chart from this week in real-time, coaches providers immediately on documentation gaps. Target: 15-25% coding improvement is common when you go from sloppy to tight. (2) Charge capture sprint: Run daily charge lag report—anything not billed same-day gets escalated. (3) Collections acceleration: Call patients with balances >$500, offer payment plans, send to collections faster.",
                        "Execute emergency labor cost reduction: (1) Staffing cuts: Do you have any unfilled positions you're holding open? Eliminate them today. Any positions filled by people doing almost nothing? Performance-manage or reassign within 48 hours. (2) Overtime freeze: Absolute ban on overtime except life-safety issues with written COO approval. Track daily. (3) Premium labor ban: No agency, no PRN, no float pool. Cancel all contracts. Use your own staff or close slots.",
                        "Communicate transparently with all staff and providers about the crisis and expectations. Don't sugarcoat it: 'Our clinic is in serious financial trouble. We're losing $[X] per month. If we don't turn this around in 60-90 days, closure is possible. Here's what we're doing and here's what we need from you.' People can handle hard truth better than uncertainty. Give them a chance to rise to the challenge or self-select out."
                    ],
                    "next_30_60_days": [
                        "Execute comprehensive transformation of both revenue cycle and labor model simultaneously. REVENUE: (1) Complete provider documentation and coding retraining—dedicate 2-4 hours per provider with EHR training specialist and certified coder. Show them their current vs. optimal levels with real charts. (2) Rebuild charge capture workflow—implement real-time charge reconciliation with daily huddles. (3) Contract renegotiation: Pull your top 10 payers by revenue—are any contracts >3 years old? Renegotiate. Even 2-3% rate increases matter in crisis.",
                        "LABOR: (1) Redesign staffing model from scratch using industry benchmarks: Target 1 FTE per 180-200 visits/month adjusted for complexity. Calculate your gap—if you're at 1 FTE per 120 visits, you're 33-50% overstaffed. (2) Rebuild workflows with zero-based approach: Every task must justify itself. Eliminate anything that doesn't directly improve patient care, revenue capture, or compliance. Common cuts: redundant documentation, unnecessary meetings, low-value administrative tasks.",
                        "Consider major structural changes if fundamentals don't improve: (1) Service consolidation: Can you merge with another clinic to share overhead? (2) Hours reduction: Cut to 4 days/week to match sustainable staffing levels? (3) Specialty focus: Drop low-margin services, double down on profitable ones? (4) Facility changes: Relocate to lower-cost space? (5) Technology reset: Is your EMR creating more work than it eliminates? Switch or simplify configuration.",
                        "Establish weekly executive steering committee with clear go/no-go decision milestones. Week 4: Have we stopped the bleeding (losses stabilized)? Week 8: Are we seeing improvement (losses decreasing)? Week 12: Are we on path to breakeven within 6 months? If answer is 'no' at any checkpoint, you need to make the hard decision about closure before losses compound."
                    ],
                    "next_60_90_days": [
                        "Target minimum 25-40% VVI improvement or make closure decision. Break this into components: Need 15-25% revenue improvement (better coding, charge capture, collections) + 15-25% labor reduction (staffing cuts, workflow redesign, overtime elimination). That's getting from a -20% margin to breakeven. Track weekly progress on visible dashboard. If you're not at +5% by week 4, +12% by week 8, and +20% by week 12, the math doesn't work.",
                        "If recovery is succeeding, rebuild sustainable operating foundation: Document new staffing model, new workflow standards, new quality metrics. Train all staff on new expectations. Implement rigorous ongoing monitoring (weekly KPI review, monthly deep dives, quarterly strategic planning). Celebrate wins but stay paranoid—you're one bad quarter away from crisis again.",
                        "Address deep cultural and operational issues that led to this crisis. Common root causes: Leadership churn, lack of accountability, poor financial transparency, 'we've always done it this way' mentality, physician resistance to operational discipline. You need cultural transformation not just operational fixes. Consider bringing in outside expertise (interim manager, operational consultant, or management services organization) to drive change.",
                        "If closure is decided, manage a compassionate and responsible wind-down: (1) Patient transition plan: 90 days notice, help patients find new providers, transfer records seamlessly. (2) Staff transition: Severance packages, outplacement services, recommendation letters, job fairs. (3) Financial closure: Settle with payers, collect AR, close contracts honorably. (4) Community communication: Transparent about reasons, minimize damage to health system reputation. Sometimes the right answer is closing gracefully rather than prolonged suffering."
                    ]
                },
                "expected_impact": {
                    "vvi_improvement": "25-40% if salvageable",
                    "timeline": "12-24 months or closure",
                    "key_risks": ["Clinic closure", "Complete staff loss", "Patient safety events", "Reputational damage", "Legal/regulatory issues"]
                }
            }
        }
        # Get scenario details - all 16 scenarios are defined
        scenario_data = scenario_library.get(scenario_id)
        
        # Debug: Show which scenario was retrieved (temporary - remove after verification)
        if not scenario_data:
            error_msg = f"ERROR: Scenario {scenario_id} not found! Available scenarios: {list(scenario_library.keys())}"
            raise ValueError(error_msg)
        
        actions = scenario_data["actions"]
        scenario_name = scenario_data["name"]
        risk_level = scenario_data["risk_level"]
        focus_areas = scenario_data["focus_areas"]
        executive_narrative = scenario_data.get("executive_narrative", "")
        expected_impact = scenario_data["expected_impact"]
        
        return {
            "clinic_id": clinic_id,
            "period": period,
            "calculated_at": datetime.utcnow().isoformat() + "Z",
            "metrics": {
                "nrpv": round(nrpv, 2),
                "lcv": round(lcv, 2),
                "swb_pct": round(swb_pct, 1)
            },
            "scores": {
                "vvi": round(vvi_score, 1),
                "rf": round(rf_score, 1),
                "lf": round(lf_score, 1)
            },
            "tiers": {
                "vvi": vvi_tier,
                "rf": rf_tier,
                "lf": lf_tier
            },
            "scenario": {
                "id": scenario_id,
                "name": scenario_name,
                "risk_level": risk_level,
                "focus_areas": focus_areas,
                "executive_narrative": executive_narrative
            },
            "actions": actions,
            "expected_impact": expected_impact,
            "source": "local"
        }


# ============================================================
# Initialize VVI Client
# ============================================================

@st.cache_data(ttl=60)  # Cache for only 60 seconds to ensure fresh data
def get_vvi_client():
    """Initialize VVI client (cached for 60 seconds)"""
    return VVIAPIClient()

vvi_client = get_vvi_client()


# ============================================================
# UI Styling
# ============================================================

GLOBAL_CSS = """
<style>
html, body {
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI",
                 Roboto, "Helvetica Neue", Arial, sans-serif;
}

.block-container {
    max-width: 950px !important;
    margin-left: auto !important;
    margin-right: auto !important;
    padding-top: 1.2rem !important;
    padding-bottom: 3rem !important;
}

h1, h2, h3, h4 {
    font-weight: 650;
    letter-spacing: 0.01em;
    color: #151515;
}

.stButton > button {
    border-radius: 999px !important;
    padding: 0.4rem 1.1rem !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    border: 1px solid #c9c5bd !important;
    box-shadow: 0 4px 10px rgba(0,0,0,0.06) !important;
}

.stButton > button:hover {
    border-color: #b08c3e !important;
    box-shadow: 0 6px 14px rgba(0,0,0,0.10) !important;
}

/* Logo fade-in */
.intro-logo {
    max-width: 240px !important;
    opacity: 0;
    animation: logoFade 1.2s ease-out forwards;
    animation-delay: 0.1s;
}

@keyframes logoFade {
    0% { opacity: 0; transform: translateY(6px); }
    100% { opacity: 1; transform: translateY(0); }
}

.intro-line {
    width: 0;
    height: 1.6px;
    background: #b08c3e;
    animation: lineGrow 1.6s ease-out forwards;
    animation-delay: 0.25s;
}

@keyframes lineGrow {
    0%   { width: 0; opacity: 0; }
    100% { width: 340px; opacity: 1; }
}

/* Hide sidebar */
section[data-testid="stSidebar"] { display: none !important; }
button[kind="headerNoPadding"] { display: none !important; }

/* Center layout */
section.main > div {
    display: flex !important;
    justify-content: center !important;
}
</style>
"""

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


# ============================================================
# Header & Branding
# ============================================================

LOGO_PATH = "Logo BC.png"

def get_base64_image(path: str) -> str:
    """Convert image to base64"""
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except:
        return ""

# Display logo if available
if os.path.exists(LOGO_PATH):
    img_data = get_base64_image(LOGO_PATH)
    st.markdown(
        f'<img src="data:image/png;base64,{img_data}" class="intro-logo" />',
        unsafe_allow_html=True,
    )

st.markdown(
    """
    <div style="text-align:center; margin: 1.5rem 0;">
        <div class="intro-line" style="margin: 0 auto;"></div>
        <h1 style="font-size:1.9rem; margin-top:1rem;">
            Welcome to the Visit Value Index™ (VVI)
        </h1>
        <p style="font-style:italic; color:#555; font-size:1.02rem;">
            The link between revenue performance and labor efficiency — quantified.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Mode indicator
mode_color = "#28a745" if st.session_state.get("api_mode") == "API" else "#ffc107"
mode_text = st.session_state.get("api_mode", "Local")
st.markdown(
    f"""
    <div style="text-align:center; margin-bottom:1rem;">
        <span style="
            background:{mode_color};
            color:white;
            padding:0.25rem 0.75rem;
            border-radius:999px;
            font-size:0.75rem;
            font-weight:600;
        ">
            {mode_text} Mode
        </span>
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()


# ============================================================
# Session State Initialization
# ============================================================

if "assessment_ready" not in st.session_state:
    st.session_state.assessment_ready = False

if "runs" not in st.session_state:
    st.session_state.runs = []

if "inputs_expanded" not in st.session_state:
    st.session_state.inputs_expanded = True


# ============================================================
# Helper Functions
# ============================================================

TIER_COLORS = {
    "Excellent": "#d9f2d9",
    "Stable": "#fff7cc",
    "At Risk": "#ffe0b3",
    "Critical": "#f8cccc",
}

def format_money(x: float) -> str:
    """Format number as currency"""
    try:
        return f"${float(x):,.2f}"
    except:
        return "$0.00"

def reset_assessment():
    """Reset assessment state"""
    st.session_state.assessment_ready = False
    st.session_state.inputs_expanded = True


# ============================================================
# Input Form
# ============================================================

with st.expander("📊 Assessment Inputs", expanded=st.session_state.inputs_expanded):
    
    with st.form("vvi_inputs"):
        
        st.markdown("**Required Metrics**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            visits = st.number_input(
                "Number of Visits",
                min_value=1,
                step=1,
                value=500,
                key="visits_input",
            )
            
            net_rev = st.number_input(
                "Net Operating Revenue (NOR) ($)",
                min_value=0.01,
                step=100.0,
                format="%.2f",
                value=100000.00,
                key="net_rev_input",
            )
        
        with col2:
            labor_cost = st.number_input(
                "Labor Expense – Salaries, Wages, Benefits (SWB) ($)",
                min_value=0.01,
                step=100.0,
                format="%.2f",
                value=65000.00,
                key="labor_cost_input",
            )
            
            period = st.text_input(
                "Period (YYYY-MM)",
                value=datetime.now().strftime("%Y-%m"),
                key="period_input"
            )
        
        st.markdown("---")
        st.markdown(
            "**Optional Benchmarks**  \n"
            "<span style='font-size:0.8rem;color:#777;'>"
            "Industry-standard averages (customizable for your organization)"
            "</span>",
            unsafe_allow_html=True,
        )
        
        col3, col4 = st.columns(2)
        
        with col3:
            r_target = st.number_input(
                "Budgeted NOR per Visit ($)",
                min_value=1.0,
                value=140.0,
                step=1.0,
                format="%.2f",
                key="rev_target_input",
            )
        
        with col4:
            l_target = st.number_input(
                "Budgeted SWB per Visit ($)",
                min_value=1.0,
                value=85.0,
                step=1.0,
                format="%.2f",
                key="lab_target_input",
            )
        
        submitted = st.form_submit_button("🚀 Run Assessment", use_container_width=True)


# ============================================================
# Process Submission
# ============================================================

if submitted:
    st.session_state.assessment_ready = True
    st.session_state.inputs_expanded = False
    st.rerun()


# ============================================================
# Results Display
# ============================================================

if st.session_state.get("assessment_ready", False):
    
    # Read values from session state
    visits = int(st.session_state.visits_input)
    net_rev = float(st.session_state.net_rev_input)
    labor = float(st.session_state.labor_cost_input)
    rt = float(st.session_state.rev_target_input)
    lt = float(st.session_state.lab_target_input)
    period = st.session_state.period_input
    
    if visits <= 0 or net_rev <= 0 or labor <= 0:
        st.warning("Please enter non-zero values for all required metrics.")
        st.stop()
    
    # Generate clinic ID
    clinic_id = f"CLINIC_{int(datetime.now().timestamp())}"
    
    # Calculate VVI
    with st.spinner("Calculating VVI..."):
        try:
            result = vvi_client.assess(
                clinic_id=clinic_id,
                period=period,
                net_revenue=net_rev,
                visit_volume=visits,
                labor_cost=labor,
                nrpv_target=rt,
                lcv_target=lt,
            )
            
            # Extract results
            metrics = result["metrics"]
            scores = result["scores"]
            tiers = result["tiers"]
            scenario = result["scenario"]
            actions = result.get("actions", {})
            expected_impact = result.get("expected_impact", {})
            
            # Store in session for later use
            st.session_state.last_result = result
            
        except Exception as e:
            st.error(f"Error calculating VVI: {str(e)}")
            st.stop()
    
    # ========================================
    # Executive Summary
    # ========================================
    
    st.markdown(
        "<h2 style='text-align:center; margin-bottom:0.5rem;'>Executive Summary</h2>",
        unsafe_allow_html=True,
    )
    
    # Tier legend
    with st.expander("📋 Scoring Tiers (0–100+)", expanded=False):
        st.markdown(
            """
            <div style="margin:0.5rem 0; line-height:1.8;">
                <div><span style="font-size:1rem;">🟢</span> <b>Excellent</b>: ≥100 <span style="color:#555;">(Top performing)</span></div>
                <div><span style="font-size:1rem;">🟡</span> <b>Stable</b>: 95–99.9 <span style="color:#555;">(Healthy, within benchmark)</span></div>
                <div><span style="font-size:1rem;">🟠</span> <b>At Risk</b>: 90–94.9 <span style="color:#555;">(Performance drift emerging)</span></div>
                <div><span style="font-size:1rem;">🔴</span> <b>Critical</b>: <90 <span style="color:#555;">(Immediate corrective focus)</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    # Hero VVI card - McKinsey-caliber design
    left_spacer, hero_col, right_spacer = st.columns([1, 2, 1])
    
    # Sophisticated tier colors with gradients
    tier_design = {
        "Excellent": {"bg": "#e8f5e9", "border": "#66bb6a", "accent": "#2e7d32"},
        "Stable": {"bg": "#fff9c4", "border": "#fdd835", "accent": "#f9a825"},
        "At Risk": {"bg": "#ffe0b2", "border": "#ff9800", "accent": "#ef6c00"},
        "Critical": {"bg": "#ffebee", "border": "#e57373", "accent": "#c62828"}
    }
    
    design = tier_design.get(tiers["vvi"], tier_design["Stable"])
    
    with hero_col:
        st.markdown(
            f"""
            <div style="background:{design['bg']};padding:2rem;border-radius:16px;border-left:6px solid {design['border']};box-shadow:0 8px 32px rgba(0,0,0,0.08),0 2px 8px rgba(0,0,0,0.04);text-align:center;">
                <div style="font-size:0.65rem;font-weight:700;letter-spacing:0.15em;text-transform:uppercase;color:#616161;margin-bottom:0.75rem;opacity:0.8;">
                    Visit Value Index (VVI)
                </div>
                <div style="font-size:3.5rem;font-weight:800;color:{design['accent']};line-height:1;margin:0.5rem 0;letter-spacing:-0.02em;">
                    {scores['vvi']:.1f}
                </div>
                <div style="font-size:0.95rem;color:#424242;margin:1rem 0 1.25rem 0;font-weight:500;opacity:0.9;">
                    Overall performance vs. benchmark
                </div>
                <div style="display:inline-block;padding:0.5rem 1.5rem;background:rgba(255,255,255,0.9);border-radius:24px;border:2px solid {design['border']};box-shadow:0 4px 12px rgba(0,0,0,0.06);">
                    <span style="font-size:0.75rem;font-weight:700;color:#616161;letter-spacing:0.05em;text-transform:uppercase;">Tier:</span>
                    <span style="font-size:0.95rem;font-weight:800;color:{design['accent']};margin-left:0.5rem;">{tiers['vvi']}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    st.markdown("")
    
    # Driving factors heading
    st.markdown(
        """
        <div style="text-align:center; margin:1rem 0;">
            <p style="font-size:18px; font-weight:600; color:#333; margin-bottom:4px;">
                Driving factor sub-scores
            </p>
            <p style="font-size:14px; color:#666; margin-top:0;">
                These values indicate the underlying performance drivers behind your overall VVI.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # RF / LF mini-cards - McKinsey design
    c_rf, c_lf = st.columns(2)
    
    # Design configs for RF and LF
    rf_design = tier_design.get(tiers["rf"], tier_design["Stable"])
    lf_design = tier_design.get(tiers["lf"], tier_design["Stable"])
    
    with c_rf:
        st.markdown(
            f"""
            <div style="background:{rf_design['bg']};padding:1.5rem;border-radius:14px;border-left:5px solid {rf_design['border']};box-shadow:0 6px 24px rgba(0,0,0,0.06),0 2px 6px rgba(0,0,0,0.03);">
                <div style="font-size:0.65rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:#757575;margin-bottom:0.75rem;opacity:0.85;">
                    Revenue Factor (RF)
                </div>
                <div style="display:flex;align-items:baseline;justify-content:space-between;margin-bottom:0.75rem;">
                    <div style="font-size:2.25rem;font-weight:800;color:{rf_design['accent']};line-height:1;letter-spacing:-0.02em;">
                        {scores['rf']:.1f}
                    </div>
                    <div style="padding:0.35rem 1rem;background:rgba(255,255,255,0.85);border-radius:20px;border:2px solid {rf_design['border']};font-size:0.75rem;font-weight:700;color:{rf_design['accent']};letter-spacing:0.03em;box-shadow:0 2px 8px rgba(0,0,0,0.04);">
                        {tiers['rf']}
                    </div>
                </div>
                <div style="font-size:0.8rem;color:#616161;font-weight:500;line-height:1.4;opacity:0.9;">
                    Actual NRPV <span style="font-weight:700;color:{rf_design['accent']};">${metrics['nrpv']:.2f}</span><br/>
                    vs. benchmark <span style="font-weight:600;opacity:0.7;">${rt:.2f}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    with c_lf:
        st.markdown(
            f"""
            <div style="background:{lf_design['bg']};padding:1.5rem;border-radius:14px;border-left:5px solid {lf_design['border']};box-shadow:0 6px 24px rgba(0,0,0,0.06),0 2px 6px rgba(0,0,0,0.03);">
                <div style="font-size:0.65rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:#757575;margin-bottom:0.75rem;opacity:0.85;">
                    Labor Factor (LF)
                </div>
                <div style="display:flex;align-items:baseline;justify-content:space-between;margin-bottom:0.75rem;">
                    <div style="font-size:2.25rem;font-weight:800;color:{lf_design['accent']};line-height:1;letter-spacing:-0.02em;">
                        {scores['lf']:.1f}
                    </div>
                    <div style="padding:0.35rem 1rem;background:rgba(255,255,255,0.85);border-radius:20px;border:2px solid {lf_design['border']};font-size:0.75rem;font-weight:700;color:{lf_design['accent']};letter-spacing:0.03em;box-shadow:0 2px 8px rgba(0,0,0,0.04);">
                        {tiers['lf']}
                    </div>
                </div>
                <div style="font-size:0.8rem;color:#616161;font-weight:500;line-height:1.4;opacity:0.9;">
                    Benchmark LCV <span style="font-weight:600;opacity:0.7;">${lt:.2f}</span><br/>
                    vs. actual <span style="font-weight:700;color:{lf_design['accent']};">${metrics['lcv']:.2f}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    st.markdown('<hr style="margin:1.5rem 0;">', unsafe_allow_html=True)
    
    # ========================================
    # Scenario Classification
    # ========================================
    
    st.markdown(
        f"""
        <div style="text-align:center; margin:1rem 0;">
            <p style="font-size:18px; font-weight:600; color:#333; margin-bottom:4px;">
                Scenario Classification
            </p>
            <p style="font-size:16px; font-weight:600; color:#b08c3e; margin-top:0.5rem;">
                {scenario['id']}: {scenario['name']}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Executive Narrative
    if scenario.get('executive_narrative'):
        st.info(f"**Executive Summary:** {scenario['executive_narrative']}")
    
    # ========================================
    # Prescriptive Actions
    # ========================================
    
    st.subheader("📋 Prescriptive Actions")
    
    st.caption(
        "Time-phased action plan based on your scenario classification. "
        "These are proven interventions from 500+ clinic assessments."
    )
    
    with st.expander("✅ Do Tomorrow (Non-negotiable staples)", expanded=True):
        for i, action in enumerate(actions.get("do_tomorrow", []), 1):
            st.markdown(f"{i}. {action}")
    
    with st.expander("🎯 Next 7 Days (Quick wins)"):
        for i, action in enumerate(actions.get("next_7_days", []), 1):
            st.markdown(f"{i}. {action}")
    
    with st.expander("🔧 Next 30-60 Days (High-impact structural changes)"):
        for i, action in enumerate(actions.get("next_30_60_days", []), 1):
            st.markdown(f"{i}. {action}")
    
    with st.expander("🏗️ Next 60-90 Days (Sustainability measures)"):
        for i, action in enumerate(actions.get("next_60_90_days", []), 1):
            st.markdown(f"{i}. {action}")
    
    # ========================================
    # Expected Impact
    # ========================================
    
    if expected_impact:
        st.markdown("---")
        st.subheader("📈 Expected Impact")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "VVI Improvement Potential",
                expected_impact.get("vvi_improvement", "N/A")
            )
        
        with col2:
            st.metric(
                "Timeline",
                expected_impact.get("timeline", "N/A")
            )
        
        if expected_impact.get("key_risks"):
            st.caption("**Key Risks to Monitor:**")
            for risk in expected_impact["key_risks"]:
                st.markdown(f"- {risk}")
    
    # ========================================
    # Save & Export
    # ========================================
    
    st.markdown("---")
    st.subheader("💾 Save & Export")
    
    col1, col2 = st.columns(2)
    
    with col1:
        run_name = st.text_input(
            "Name this assessment:",
            value=f"Assessment {len(st.session_state.runs) + 1}"
        )
        
        if st.button("💾 Save to Portfolio"):
            st.session_state.runs.append({
                "Name": run_name,
                "Period": period,
                "VVI": scores["vvi"],
                "RF": scores["rf"],
                "LF": scores["lf"],
                "Scenario": scenario["id"],
                "Risk": scenario["risk_level"],
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            st.success(f"✅ Saved: {run_name}")
    
    with col2:
        st.markdown("&nbsp;")  # Spacer
        st.download_button(
            label="📄 Download Summary (JSON)",
            data=json.dumps(result, indent=2),
            file_name=f"vvi_assessment_{period}.json",
            mime="application/json"
        )
    
    # ========================================
    # Portfolio Comparison
    # ========================================
    
    if st.session_state.runs:
        st.markdown("---")
        st.subheader("📊 Portfolio Comparison")
        
        df = pd.DataFrame(st.session_state.runs)
        
        st.dataframe(
            df.style.background_gradient(
                subset=["VVI", "RF", "LF"],
                cmap="RdYlGn",
                vmin=80,
                vmax=110
            ),
            use_container_width=True,
            hide_index=True
        )
        
        col1, col2 = st.columns([3, 1])
        
        with col2:
            if st.button("🗑️ Clear Portfolio"):
                st.session_state.runs = []
                st.rerun()
    
    # ========================================
    # New Assessment Button
    # ========================================
    
    st.markdown("---")
    if st.button("🔄 Start New Assessment", use_container_width=True):
        reset_assessment()
        st.rerun()


# ============================================================
# Footer
# ============================================================

st.markdown("---")
st.markdown(
    """
    <div style="text-align:center; color:#777; font-size:0.85rem; padding:2rem 0 1rem 0;">
        <p><b>Visit Value Index™ (VVI)</b> | Version 2.7 — Enhanced Actions</p>
        <p>Bramhall Consulting, LLC | © 2024</p>
        <p style="margin-top:0.5rem;">
            <a href="https://bramhallconsulting.org" target="_blank" style="color:#b08c3e; text-decoration:none;">
                bramhallconsulting.org
            </a>
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
