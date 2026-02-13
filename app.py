"""
Visit Value Index (VVI) Application - Enterprise Edition
Bramhall Consulting, LLC

VERSION: 2.3 - Cache Fix + Complete 16 Scenarios
Last Updated: February 13, 2026

Upgraded architecture:
- API-first design with local fallback
- Modular code structure
- Enhanced error handling
- Performance optimizations
- Production-ready deployment
- COMPLETE 16-scenario library built-in (S01-S16)
- Fixed: Cache refresh to ensure latest scenarios load
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
                "focus_areas": ["Sustain excellence", "Prevent drift", "Scale best practices"],
                "actions": {
                    "do_tomorrow": [
                        "Brief huddle to recognize performance and reinforce 'what good looks like.'",
                        "Verify yesterday's charts are closed and POS collections reconciled.",
                        "Ask staff where today's biggest risk to flow might be and mitigate early."
                    ],
                    "next_7_days": [
                        "Run a simple time-study on a busy session to confirm throughput remains tight.",
                        "Spot-check coding and POS for any early signs of revenue leakage.",
                        "Check schedule templates against actual demand to confirm continued fit."
                    ],
                    "next_30_60_days": [
                        "Document this clinic's playbook (staffing, workflows, huddle routines).",
                        "Use this site as a peer-teaching location for under-performing clinics.",
                        "Refresh stay interviews or engagement touchpoints with key staff."
                    ],
                    "next_60_90_days": [
                        "Review succession plans for front-line leaders and key roles.",
                        "Stress-test capacity for modest volume growth without harming VVI.",
                        "Refine KPIs and dashboards to keep leading indicators visible."
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
                "focus_areas": ["Emergency labor correction", "Protect revenue gains", "Prevent burnout cascade"],
                "actions": {
                    "do_tomorrow": [
                        "Emergency labor review meeting with operations and HR.",
                        "Immediate staffing audit: are we carrying ghost positions or excessive overtime?",
                        "Freeze all discretionary hiring and overtime until analysis complete."
                    ],
                    "next_7_days": [
                        "Conduct full workflow analysis to identify waste and duplication.",
                        "Review all staffing templates and adjust to match actual demand.",
                        "Identify tasks that can be eliminated, automated, or reassigned.",
                        "Daily check-ins on labor metrics and overtime."
                    ],
                    "next_30_60_days": [
                        "Redesign workflows to reduce labor intensity while maintaining quality.",
                        "Implement strict overtime controls with daily approval.",
                        "Cross-train staff to create flexibility and reduce reliance on premium labor.",
                        "Consider temporary productivity consultants if internal capacity lacking."
                    ],
                    "next_60_90_days": [
                        "Target 10-15% labor cost reduction to restore sustainability.",
                        "Formalize new staffing standards and daily huddle discipline.",
                        "Monitor staff engagement closely to prevent attrition.",
                        "Develop formal retention plan for key clinical and support staff."
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
                "focus_areas": ["Survival", "Complete operational reset", "Viability assessment"],
                "actions": {
                    "do_tomorrow": [
                        "Emergency executive session: assess whether clinic is salvageable.",
                        "If continuing: declare full crisis mode with daily war room.",
                        "Immediate actions on both revenue and labor fronts."
                    ],
                    "next_7_days": [
                        "Daily executive crisis meetings with board/system visibility.",
                        "Emergency revenue actions: coding blitz, charge capture, collections acceleration.",
                        "Emergency labor actions: staffing cuts, overtime freeze, workflow triage.",
                        "Transparent communication plan for staff, providers, patients.",
                        "Assess whether temporary external support (consultants, interim leaders) needed."
                    ],
                    "next_30_60_days": [
                        "Execute comprehensive transformation of both revenue and labor.",
                        "Revenue: Complete billing cycle redesign, provider retraining, contract renegotiation.",
                        "Labor: Staffing model rebuild, workflow elimination/redesign, productivity standards.",
                        "Consider service consolidation, hours reduction, or other structural changes.",
                        "Weekly progress reviews with clear go/no-go decision points."
                    ],
                    "next_60_90_days": [
                        "Achieve minimum 25-40% VVI improvement or make closure decision.",
                        "Rebuild sustainable operating foundation if recovery succeeds.",
                        "Address deep cultural and operational issues that led to crisis.",
                        "Develop rigorous ongoing monitoring to prevent recurrence.",
                        "If closure decided: manage compassionate wind-down for staff and patients."
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
                "focus_areas": focus_areas
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
    
    # Hero VVI card
    left_spacer, hero_col, right_spacer = st.columns([1, 2, 1])
    vvi_bg = TIER_COLORS.get(tiers["vvi"], "#f5f5f5")
    
    with hero_col:
        st.markdown(
            f"""
            <div style="
                background:{vvi_bg};
                padding:1.3rem 1.5rem;
                border-radius:14px;
                border-top:5px solid #b08c3e;
                box-shadow:0 10px 24px rgba(0,0,0,0.10);
                text-align:center;
            ">
                <div style="font-size:0.7rem; letter-spacing:0.14em;
                            text-transform:uppercase; color:#666; margin-bottom:0.4rem;">
                    Visit Value Index (VVI)
                </div>
                <div style="font-size:2.3rem; font-weight:750; color:#222;">
                    {scores['vvi']:.1f}
                </div>
                <div style="font-size:0.9rem; color:#444; margin-top:0.2rem;">
                    Overall performance vs. benchmark
                </div>
                <div style="margin-top:0.6rem; font-size:0.86rem; color:#333;">
                    Tier: <span style="
                        display:inline-block; padding:0.15rem 0.55rem;
                        border-radius:999px; background:rgba(0,0,0,0.04);
                        font-weight:600; font-size:0.8rem;">
                        {tiers['vvi']}
                    </span>
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
    
    # RF / LF mini-cards
    c_rf, c_lf = st.columns(2)
    rf_bg = TIER_COLORS.get(tiers["rf"], "#f5f5f5")
    lf_bg = TIER_COLORS.get(tiers["lf"], "#f5f5f5")
    
    with c_rf:
        st.markdown(
            f"""
            <div style="background:{rf_bg}; padding:0.85rem 1.0rem;
                        border-radius:10px; border-top:3px solid rgba(0,0,0,0.06);
                        box-shadow:0 6px 16px rgba(0,0,0,0.06);">
                <div style="font-size:0.7rem; letter-spacing:0.11em; 
                            text-transform:uppercase; color:#666; margin-bottom:0.15rem;">
                    Revenue Factor (RF)
                </div>
                <div style="display:flex; align-items:center; justify-content:space-between;">
                    <div style="font-size:1.4rem; font-weight:700; color:#222;">
                        {scores['rf']:.1f}
                    </div>
                    <div style="font-size:0.78rem; padding:0.16rem 0.6rem;
                                border-radius:999px; background:rgba(0,0,0,0.03);
                                font-weight:600; color:#333;">
                        {tiers['rf']}
                    </div>
                </div>
                <div style="font-size:0.78rem; color:#555; margin-top:0.25rem;">
                    Actual NRPV ({metrics['nrpv']:.2f}) vs. benchmark ({rt:.2f})
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    with c_lf:
        st.markdown(
            f"""
            <div style="background:{lf_bg}; padding:0.85rem 1.0rem;
                        border-radius:10px; border-top:3px solid rgba(0,0,0,0.06);
                        box-shadow:0 6px 16px rgba(0,0,0,0.06);">
                <div style="font-size:0.7rem; letter-spacing:0.11em;
                            text-transform:uppercase; color:#666; margin-bottom:0.15rem;">
                    Labor Factor (LF)
                </div>
                <div style="display:flex; align-items:center; justify-content:space-between;">
                    <div style="font-size:1.4rem; font-weight:700; color:#222;">
                        {scores['lf']:.1f}
                    </div>
                    <div style="font-size:0.78rem; padding:0.16rem 0.6rem;
                                border-radius:999px; background:rgba(0,0,0,0.03);
                                font-weight:600; color:#333;">
                        {tiers['lf']}
                    </div>
                </div>
                <div style="font-size:0.78rem; color:#555; margin-top:0.25rem;">
                    Benchmark LCV ({lt:.2f}) vs. actual ({metrics['lcv']:.2f})
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
            <p style="font-size:14px; color:#666; margin-top:0.5rem;">
                Risk Level: <span style="font-weight:600;">{scenario['risk_level']}</span>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
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
        <p><b>Visit Value Index™ (VVI)</b> | Version 2.3 ✨</p>
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
