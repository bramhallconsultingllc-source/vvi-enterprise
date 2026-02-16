"""
Visit Value Index (VVI) Application - Enterprise Edition
Bramhall Consulting, LLC

VERSION: 2.9 - Root Cause Analysis Added
Last Updated: February 16, 2026

Upgraded architecture:
- API-first design with local fallback
- Modular code structure
- Enhanced error handling
- Performance optimizations
- Production-ready deployment
- COMPLETE 16-scenario library built-in (S01-S16)
- Executive narratives for each scenario
- ROOT CAUSE ANALYSIS for diagnostic insight
- McKinsey-caliber visual design
- URGENT CARE-SPECIFIC prescriptive actions with UC demand patterns, workflows, and metrics
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
                "root_causes": [
                    "Strong operational discipline with daily performance basics (chart closure, POS collection, workflow adherence)",
                    "Staffing appropriately matched to urgent care demand patterns (Monday heavy, Friday light, peak hour surge capacity)",
                    "Efficient workflows with minimal waste (fast rooming, provider charting discipline, streamlined checkout)",
                    "Effective coding and charge capture practices (appropriate E&M levels, procedure documentation, same-shift billing)",
                    "Good provider productivity during peak hours (4-5 patients/hour) without sacrificing quality",
                    "Cross-trained staff creating flexibility without reliance on premium labor or excessive overtime"
                ],
                "focus_areas": ["Sustain excellence", "Prevent drift", "Scale best practices"],
                "actions": {
                    "do_tomorrow": [
                        "Hold a 10-minute team huddle to recognize excellent UC performance. Be specific: 'Our VVI of [X] puts us in the top 10% of urgent cares nationally. Monday 4-7pm we saw 47 patients with 3 providers and no backlog. Sunday we handled 112 patients smoothly. This is your work—efficient rooming, smart provider ordering, tight registration. Thank you.' In UC, recognition prevents Monday burnout and keeps the team sharp.",
                        "Verify yesterday's operational discipline: All charts closed same-shift? (UC target: 100% closed before provider leaves). Point-of-service copay collection at check-in? (Target: 95%+ collected upfront, not at checkout). X-ray/labs resulted and communicated within 60 minutes? Occupational health forms completed same-visit? These daily basics prevent revenue leakage and patient dissatisfaction.",
                        "Ask your team the UC-specific risk question: 'What's our biggest operational risk today?' Common UC answers: key MA out sick during Monday rush, X-ray machine acting up, unexpected school closure bringing surge of kids, staff member new/learning curve. Identify the risk and mitigate before peak hours (4-7pm). This daily check prevents chaos during your highest-revenue window."
                    ],
                    "next_7_days": [
                        "Run a time study during both Monday 5-6pm (peak stress) and Friday 10-11am (off-peak). PEAK: Track door-to-room time (target: <10 min), room-to-provider time (target: <5 min), provider face time (target: 15-20 min for level 3-4), checkout time (target: <2 min). Can you handle 4-5 patients/hour per provider during surge? OFF-PEAK: Are staff idle? Could you operate with fewer FTEs? UC excellence means knowing your peak capacity limits and off-peak efficiency opportunities.",
                        "Audit coding and charge capture for UC-specific revenue optimization. Pull 20 random charts from last week: (1) Are E&M levels appropriate? UC averages 60% level 4, 30% level 3, 10% level 5. If you're showing 80% level 3, you're under-coding by $15-$25 per visit. (2) Are procedures captured? Laceration repairs, splinting, I&D, nebulizers all have separate codes. (3) Are X-rays, labs, and EKGs billed correctly? (4) Occupational health visits coded as such (higher reimbursement)? Even 2-3 missed charges per day = $15K-$25K annual revenue loss.",
                        "Review staffing template against actual UC demand curve. Pull 4 weeks of hourly arrival data and compare to staff scheduled: MONDAY should have 30-40% more FTEs than FRIDAY. Peak hours (9-11am, 4-7pm) should have 20-30% more staff than mid-day lull (1-3pm). Are you still matched? UC demand shifts seasonally (winter respiratory surge, summer injury spike) and you need quarterly template reviews to stay optimized."
                    ],
                    "next_30_60_days": [
                        "Document your UC operational playbook (8-12 pages): (1) Staffing model by day/hour and volume tier, (2) Peak hour surge protocols (when/how to call in extra provider or MA), (3) UC-specific workflows (fast-track for simple visits, full track for complex), (4) Triage protocols (who gets roomed first—chest pain and peds fever trump sore throats), (5) Common procedure checklists (lac repair setup, splinting, abscess I&D), (6) Opening/closing procedures for each role. When you hire new staff or a manager, this playbook gets them productive in days not weeks.",
                        "Host peer observations from underperforming UCs in your region (2-3 visitors for half-day). Walk them through: How you staff Monday vs. Friday (show them your template). How you handle 4-7pm surge (provider works fast, MA preps rooms ahead, front desk batches tasks). How you maintain chart closure discipline (providers chart while patient dresses/checks out). How you cross-train for flexibility (every MA can do registration, every front desk can room simple visits). Benefits: Your team gets recognized as experts, you articulate your excellence, you build regional relationships for coverage sharing.",
                        "Conduct quarterly satisfaction pulse with UC staff (they face unique stressors): (1) How's the Monday/Sunday grind? Feeling burned out? (2) Do you have supplies/equipment you need during peak hours? (3) Any workflow frustrations we can fix? (4) Scheduling requests or flexibility needs? Common UC issues: Weekend burden feels unfair (rotate it visibly), peak hours feel chaotic (add surge protocols), patients are demanding (train de-escalation), occupational health paperwork is tedious (create templates). Address issues quickly—UC staff turnover destroys your efficiency."
                    ],
                    "next_60_90_days": [
                        "Review succession plans for critical UC roles: Who's your backup if your center manager quits? Your best/fastest provider leaves? Your senior MA (who can handle anything) retires? Your X-ray tech is gone? UC has specialized roles that are hard to fill quickly. Identify 1-2 development candidates for each critical position. Send them to UCAOA conference, give them lead shifts, cross-train them on manager duties. Losing a key person in UC can crater your efficiency for 3-6 months during replacement/training.",
                        "Stress-test capacity for UC growth scenarios: (1) What if Monday volume increases 20% (goes from 120 to 144 patients)? Do you add a provider? MA? Extend hours to 9pm? (2) What if occupational health contracts double? Can you dedicate a provider and room? (3) What if pediatric volume surges (school outbreak)? Do you have peds-trained MAs and child-friendly supplies? Model these scenarios now so growth doesn't destroy your VVI—many UCs accept volume they can't handle efficiently and margins collapse.",
                        "Refine UC-specific KPI dashboard beyond VVI: (1) Patients per provider hour by shift (peak vs. off-peak), (2) Door-to-room time by time of day, (3) Left without being seen % (target: <2%), (4) Chart closure same-shift % (target: 100%), (5) POS collection % (target: 95%+), (6) Average minutes per patient encounter, (7) X-ray/lab turnaround time, (8) Occupational health as % of total visits. Display weekly in one-page dashboard. Review monthly. These leading indicators catch UC-specific problems before they hurt VVI."
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
                "root_causes": [
                    "Minor staffing inefficiencies during off-peak hours (Friday mornings, mid-day lulls on Tuesday-Thursday)",
                    "Possible workflow friction points adding 10-15% unnecessary labor time per patient encounter",
                    "Limited staff cross-training creating inflexibility and requiring extra coverage",
                    "Small amount of unnecessary overtime (5-8% of total hours) from poor scheduling coordination"
                ],
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
                "root_causes": [
                    "Labor cost drift from gradual overstaffing as patient volume patterns shifted but templates didn't adjust",
                    "Increasing overtime usage (8-12% of hours) suggesting poor scheduling or inadequate staffing flexibility",
                    "Growing reliance on premium labor (PRN, agency) to cover gaps instead of cross-training core staff",
                    "Workflow inefficiencies creeping in (task duplication, unnecessary steps) adding 15-20% labor time per encounter",
                    "Possible role confusion or task bloat with staff taking on low-value activities"
                ],
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
                "root_causes": [
                    "Staffing misaligned with urgent care demand curve (overstaffing Friday mornings and off-peak hours while potentially understaffing Monday/Sunday 4-7pm peaks)",
                    "Flat staffing templates treating all days equally instead of flexing 30-40% between Monday (highest) and Friday (lowest)",
                    "Excessive overtime or reliance on premium labor (PRN/agency staff) due to poor scheduling or inadequate cross-training",
                    "Workflow inefficiencies during peak hours causing throughput collapse and requiring more staff than necessary",
                    "Poor scheduling flexibility using rigid 8-hour blocks instead of flex shifts (4-hour, 6-hour, split shifts) matched to patient arrival patterns",
                    "Role drift and task bloat with staff performing low-value activities that don't contribute to patient care or revenue"
                ],
                "focus_areas": ["Emergency labor correction", "Protect revenue gains", "Prevent burnout cascade"],
                "actions": {
                    "do_tomorrow": [
                        "Call an emergency labor review meeting (operations lead, center manager, HR) for 1 hour. Bring last 4 weeks of payroll data, overtime reports, and staffing templates. Goal: identify where labor is bleeding—overtime (>10% of total hours?), premium labor (PRN/agency >5%?), or overstaffing during low-volume periods (Friday mornings, Thursday afternoons)?",
                        "Conduct immediate staffing audit: Print your staffing template vs. actual staff scheduled for TODAY. Are you staffing equally for Monday (peak day) and Friday (lowest day)? That's your problem. Count FTEs per 100 visits by day—Friday should have 30-40% fewer staff than Monday. Are you carrying 'ghost positions' or overstaffing your 4-7pm peak when you should be understaffed at 8am and 1-3pm?",
                        "Freeze all discretionary hiring and overtime approvals until analysis complete (24-48 hours). Require director approval for any overtime. This creates immediate pressure relief. Exception: Don't cut Monday 10am-12pm or Sunday/Monday 4-7pm peak hours—those drive your revenue. Cut the fat (Friday 8am-11am, Thursday 2-4pm) not the muscle."
                    ],
                    "next_7_days": [
                        "Run a time study on both PEAK hour (Monday 5-7pm) and OFF-PEAK hour (Friday 10am-12pm). For peak: can 1 provider see 4+ patients/hour with current MA support? Are you bottlenecked at registration, X-ray, lab, or checkout? For off-peak: are staff standing around? Could you operate with 1 fewer provider and 1-2 fewer MAs? Urgent care is all about flex staffing—if you staff flat across all hours, you're burning cash.",
                        "Map every role's tasks during peak vs. off-peak: Front desk (registration, phones, insurance verification, payment collection), MAs (rooming, vitals, EKG, simple procedures, discharge), Providers (see patients, chart, procedures), and X-ray/Lab techs (imaging, point-of-care testing). In UC, the bottleneck shifts by hour—9-11am it's registration, 5-7pm it's providers, off-peak you have excess capacity everywhere. Identify opportunities to cross-train (MA who can also do registration, provider who can room their own patients during slow times).",
                        "Analyze your staffing by day and time block using actual patient arrival data. Pull 4 weeks: arrivals by day of week and hour. Your template should look like: MONDAY (heavy all day): 3-4 providers, 6-8 MAs, 3 front desk, full X-ray/lab. FRIDAY (light): 2 providers, 4 MAs, 2 front desk, part-time imaging. You should flex 30-40% of staff based on demand. If you're staffing Friday like Monday, you're wasting $15K-$25K monthly.",
                        "Run overtime and premium labor analysis specific to UC patterns: Is overtime spiking Monday/Sunday evenings because you understaffed peak hours? That's inefficient—better to staff appropriately. Is overtime on Friday mornings because you're holding everyone till close? That's waste—send people home when volume drops. Are you using agency staff for routine coverage? Ban it. Agency works for emergencies (staff callout during Monday rush) not routine scheduling."
                    ],
                    "next_30_60_days": [
                        "Redesign staffing model around UC demand curve, not primary care thinking. MONDAY template: Full staffing 9am-8pm with surge capacity 4-7pm (add 1 extra provider, 2 extra MAs for these 3 hours). SUNDAY template: Moderate staffing with 4-7pm surge. TUESDAY-THURSDAY template: Baseline staffing with 5-7pm bump. FRIDAY template: Light staffing, especially 8am-2pm, with modest 5-7pm coverage. SATURDAY template: Moderate with injury focus (X-ray tech critical). Calculate FTE needs: Target 1 provider per 20-25 patients/day, 1 MA per 12-15 patients/day, 1 front desk per 30-35 patients/day adjusted by hour.",
                        "Implement UC-specific flex scheduling: (1) Shift-based staffing not 8-hour blocks—use 4-hour, 6-hour, and 10-hour shifts to match demand curve. (2) Split shifts for MAs: 8am-12pm + 4-8pm to cover peaks, skip the dead zone. (3) On-call for surge days: If Monday hits 150+ patients (vs. your 100 average), have 1 provider and 1-2 MAs you can call in within 1 hour. (4) Send-home protocols: If Friday 10am has <3 patients waiting, send 1 MA home (pay 4 hours). If 2pm has <5 patients, send 1 provider home.",
                        "Optimize workflow for UC speed and efficiency: (1) Self-service kiosks for registration (saves 5-8 min per patient, reduces front desk by 1 FTE). (2) Rooming protocols: MA spends exactly 5 minutes—vitals, chief complaint, insurance card scan, payment collection, provider text notification. No chatting, no lingering. (3) Provider documentation: Chart while patient is there (3-5 minutes) not after (15 minutes). Use templates, dot phrases, voice dictation. (4) Discharge protocols: Hand patient their paperwork, aftercare instructions, and work note while checking out—no separate 'discharge nurse' role. Every patient out in <2 minutes after provider finishes.",
                        "Eliminate premium labor dependency: (1) Cross-train 3-4 staff to cover every role (MA who can do front desk, provider who can handle their own rooming during slow times, front desk who can do basic MA tasks). (2) Build a PRN pool from your own staff (offer existing staff extra shifts at straight time before calling agency at 1.5x-2x rate). (3) Create backup coverage protocols: If Monday MA calls out, pull from Tuesday overstaffing. If Sunday provider is sick, ask Saturday provider to extend 4 hours. Never pay $120/hour for agency MD when your own docs will cover for $85/hour."
                    ],
                    "next_60_90_days": [
                        "Target 10-15% labor cost reduction specific to UC inefficiencies: For a UC with $130 LCV, get to $110-$117. That's roughly eliminating: 8-10 hours of unnecessary staffing per day (ex: 1 MA on Friday mornings, 1 front desk Tuesday afternoons, 1 provider Thursday 1-4pm). Typical savings: $8K-$12K monthly from better flex scheduling + $3K-$5K monthly from overtime elimination + $2K-$4K monthly from eliminating agency = $13K-$21K monthly ($156K-$252K annually).",
                        "Formalize UC-specific staffing standards in a simple 2-page document: (1) Staffing ratios by volume tier (<60 pts/day, 60-100, 100-140, >140). (2) Peak hour surge protocols (when do you add extra provider? extra MA?). (3) Minimum safe staffing (never fewer than 2 providers, 3 MAs, 2 front desk even on slowest day). (4) Flex thresholds (at what patient count do you send someone home? call someone in?). Get medical director and operations VP sign-off. Use this to guide all scheduling decisions—no more 'gut feel' staffing.",
                        "Monitor UC-specific staff satisfaction metrics because UC is burnout-prone: (1) Monday/Sunday evening staff get flex Fridays (work Monday 4-8pm peak? Take Friday 9am-1pm off). (2) Rotate weekend coverage fairly—track who worked last 3 Sundays, make it visible. (3) Peak-hour bonuses: Extra $2-3/hour for staff working Monday 4-8pm or Sunday all day. (4) Monthly pulse survey: 'Do you feel overstaffed or understaffed this month? Which shifts are hardest? What would help?' Act on feedback quickly.",
                        "Develop UC retention plan for critical roles: (1) Providers: Flexible scheduling (4x10s, 3x12s, weekends-only, evenings-only). Competitive wRVU model. Autonomy (within guidelines). Path to medical director. (2) Senior MAs: Cross-training to X-ray or lead roles. Weekend differential pay. First choice of schedules. (3) Front desk leads: Technology (kiosks, online check-in) to reduce repetitive work. Empowerment to handle patient issues. Commission on copay collection. UC competes with hospitals, retail, and other UCs for talent—you need to differentiate on flexibility and respect."
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
                "root_causes": [
                    "Provider documentation and coding practices are good but conservative—likely under-coding E&M levels by 1 level on 20-30% of visits",
                    "Missed revenue opportunities from procedures not consistently captured (minor procedures, splinting, nebulizers, extended visits)",
                    "Charge capture workflow gaps allowing some billable services to fall through cracks (X-rays ordered but not billed, labs not linked to visit)",
                    "Limited occupational health penetration or sports medicine services that could increase revenue per visit",
                    "Possible payer mix challenges with higher proportion of lower-reimbursing contracts",
                    "Strong operations but conservative billing practices leaving money on table"
                ],
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
                "root_causes": [
                    "Generally adequate but not optimized performance—no major problems but no excellence either",
                    "Possible complacency from 'good enough' mindset preventing push toward top-tier performance",
                    "Minor inefficiencies on both revenue (some under-coding, occasional missed charges) and labor (slight overstaffing during off-peak)",
                    "Lack of focused improvement initiatives—operating on autopilot without systematic optimization efforts",
                    "Workflow and staffing templates that haven't been reviewed or updated in 6-12+ months as patterns shifted"
                ],
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
                "root_causes": [
                    "Labor costs creeping up from gradual overstaffing during off-peak periods without corresponding revenue growth",
                    "Overtime increasing to 8-12% of total hours from poor scheduling, staff callouts, or inadequate flex staffing",
                    "Workflow inefficiencies slowing throughput and requiring more staff than necessary to handle same patient volume",
                    "Possible task creep with staff taking on activities that don't add value or could be eliminated/automated",
                    "Lack of labor monitoring allowing costs to drift upward without early intervention"
                ],
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
                "root_causes": [
                    "Severe overstaffing with flat templates ignoring demand variation (same staffing Friday as Monday, same staffing 2pm as 6pm)",
                    "Excessive overtime (12-18%+ of hours) or heavy reliance on premium labor (agency, PRN) indicating fundamental scheduling failure",
                    "Major workflow breakdowns causing low productivity—providers seeing 2-3 patients/hour instead of 4-5 during peak",
                    "Possible leadership gaps with no accountability for labor cost management or performance standards",
                    "Cultural issues with staff resistance to efficiency improvements or 'we've always been overstaffed' mentality",
                    "Combination of overstaffing AND inefficiency compounding the problem"
                ],
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
                "root_causes": [
                    "Under-coding by 1-2 E&M levels on significant portion of visits (providers documenting level 4 work but billing level 3)",
                    "Missed procedure charges from incomplete capture workflows (lacerations, splints, extended services not consistently billed)",
                    "Charge lag or billing errors allowing revenue to slip through cracks before submission",
                    "Documentation gaps preventing appropriate coding levels despite clinical complexity",
                    "Possible payer mix deterioration or unfavorable contract rates reducing reimbursement per visit"
                ],
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
                "root_causes": [
                    "Revenue decline from combination of under-coding and missed charges reducing revenue per visit by 10-15%",
                    "Provider documentation not supporting higher E&M levels despite clinical work performed",
                    "Billing workflow gaps or delays allowing charges to be lost or denied",
                    "Possible volume decline or payer mix shift reducing overall revenue",
                    "Lack of revenue monitoring allowing slow erosion without timely intervention"
                ],
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
                "root_causes": [
                    "Simultaneous problems: under-coding/missed charges reducing revenue AND overstaffing/overtime increasing labor costs",
                    "Lack of operational discipline allowing both issues to develop without early intervention",
                    "Possible leadership gaps or accountability issues preventing timely problem-solving",
                    "Workflow inefficiencies affecting both dimensions (slow throughput hurts revenue AND requires more staff)",
                    "Staff and provider engagement issues leading to performance decline across the board"
                ],
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
                "root_causes": [
                    "Critical labor overspend from severe overstaffing combined with excessive overtime and premium labor usage",
                    "Revenue decline from under-coding and missed charges making the labor problem unsustainable",
                    "Complete misalignment of staffing to demand patterns burning 30-50% excess labor",
                    "Workflow collapse during peak hours requiring excessive staff to handle normal volume",
                    "Possible leadership crisis with no one accountable for financial performance or willing to make hard decisions"
                ],
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
                "root_causes": [
                    "Severe under-coding by 1-2 levels on majority of visits (level 2-3 coding when level 4-5 work performed)",
                    "Systemic charge capture failure with 15-30% of billable services not being captured or billed",
                    "Major billing process breakdown allowing charges to be lost, delayed, or denied at high rates",
                    "Possible unfavorable payer mix or contract rates significantly below market",
                    "Provider documentation completely inadequate to support appropriate coding levels despite clinical work"
                ],
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
                "root_causes": [
                    "Critical revenue capture failure from combination of severe under-coding, missed charges, and billing errors",
                    "Provider documentation practices far below standard preventing appropriate reimbursement",
                    "Possible case mix issues with center seeing lower-acuity visits that generate less revenue",
                    "Unfavorable payer contracts or high proportion of low-reimbursing payers",
                    "Billing and collections process failures allowing significant revenue leakage"
                ],
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
                "root_causes": [
                    "Critical revenue failure AND labor cost escalation occurring simultaneously",
                    "Severe under-coding combined with overstaffing creating worst-case margin scenario",
                    "Fundamental operational breakdown across all dimensions (workflows, staffing, documentation, billing)",
                    "Leadership crisis or absence of accountability allowing both issues to spiral",
                    "Possible staff and provider morale collapse leading to performance deterioration",
                    "May indicate deeper structural problems: wrong location, unsustainable payer mix, or market conditions"
                ],
                "focus_areas": ["Dual emergency", "Triage and stabilize", "Survival mode"],
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
                "root_causes": [
                    "Severe revenue capture failure from systemic under-coding, missed charges, poor documentation, or billing process breakdown",
                    "Critical labor inefficiency from overstaffing, poor workflows, excessive overtime, and reliance on premium labor simultaneously",
                    "Complete misalignment of staffing to demand with flat templates ignoring Monday peaks and Friday valleys",
                    "Leadership and accountability gaps allowing both revenue and labor issues to compound without intervention",
                    "Provider documentation and coding practices significantly below standard (heavy level 2-3 coding, missing procedures)",
                    "Cultural dysfunction with staff resistance to change, poor communication, or 'we've always done it this way' mentality",
                    "Possible structural issues: wrong location, unsustainable payer mix, or market conditions that make the center unviable"
                ],
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
        root_causes = scenario_data.get("root_causes", [])
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
                "executive_narrative": executive_narrative,
                "root_causes": root_causes
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
    
    # Root Cause Analysis
    if scenario.get('root_causes'):
        st.markdown("---")
        st.subheader("🔍 Root Cause Analysis")
        st.caption("Why this may be happening (possible primary drivers):")
        
        for cause in scenario['root_causes']:
            st.markdown(f"• {cause}")
    
    # ========================================
    # Prescriptive Actions
    # ========================================
    
    st.markdown("---")
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
        <p><b>Visit Value Index™ (VVI)</b> | Version 2.9 — Root Cause Analysis</p>
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
