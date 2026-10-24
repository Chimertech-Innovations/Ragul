# -*- coding: utf-8 -*-
"""
NASEM 2021 Unified Dairy Feed, Water, Energy, Mineral & Ration Optimization Engine.
Standard: NASEM 2021, Nutrient Requirements of Dairy Cattle, 8th Revised Edition.
Ruleset ID: dairy_feed_calculation_nasem2021_consistent_v1
"""

import os
import json
import math
import logging
from typing import Dict, Any, Optional, List, Tuple

logger = logging.getLogger("ragul_nasem_engine")

class NASEM2021Calculator:
    def __init__(self):
        self.rules_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "data", "knowledge_base", "nasem_feed_nutrition_rules.json"
        )
        self.rules: Dict[str, Any] = {}
        self.load_rules()

    def load_rules(self):
        try:
            if os.path.exists(self.rules_path):
                with open(self.rules_path, "r", encoding="utf-8") as f:
                    self.rules = json.load(f)
                logger.info(f"[NASEM] Loaded NASEM 2021 ruleset '{self.rules.get('ruleset_id')}' successfully.")
            else:
                logger.warning(f"[NASEM] Ruleset JSON not found at {self.rules_path}")
        except Exception as e:
            logger.error(f"[NASEM] Failed to load NASEM ruleset: {e}")

    # ---------------- 1. DMI (Dry Matter Intake) ---------------- #

    def calculate_dmi_lactating(
        self,
        bw_kg: float,
        parity: int = 1,
        dim: int = 100,
        bcs: float = 3.0,
        milk_yield_kg: float = 15.0,
        fat_percent: float = 4.0,
        true_protein_percent: Optional[float] = None,
        lactose_percent: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        NASEM 2021 Equation 2-1 for lactating dairy cow DMI.
        DMI = (3.7 + 5.7*Parity + 0.305*MilkE + 0.022*BW + (-0.689 - 1.87*Parity)*BCS) * (1 - (0.212 + 0.136*Parity)*exp(-0.053*DIM))
        """
        p_factor = 1.0 if parity >= 2 else 0.0

        # Milk energy output
        milk_e_res = self.calculate_milk_energy(milk_yield_kg, fat_percent, true_protein_percent, lactose_percent)
        milk_e = milk_e_res["milk_e_mcal_day"]

        # Bracket 1: Base intake potential
        base = (3.7 + 5.7 * p_factor + 0.305 * milk_e + 0.022 * bw_kg + (-0.689 - 1.87 * p_factor) * bcs)
        # Bracket 2: DIM lag adjustment
        dim_lag = (1.0 - (0.212 + 0.136 * p_factor) * math.exp(-0.053 * max(1, dim)))
        dmi_val = max(1.0, round(base * dim_lag, 2))

        return {
            "equation_id": "NASEM_2021_EQ_2_1",
            "scientific_status": "authoritative_equation",
            "reference": "NASEM 2021 Chapter 2, Dry Matter Intake",
            "inputs": {
                "BW_kg": bw_kg,
                "Parity": parity,
                "Parity_factor": p_factor,
                "DIM": dim,
                "BCS": bcs,
                "Milk_Yield_kg_day": milk_yield_kg,
                "Fat_percent": fat_percent,
                "MilkE_Mcal_day": round(milk_e, 2)
            },
            "result": {
                "dmi_kg_dm_day": dmi_val,
                "unit": "kg DM/day"
            },
            "notes": "Official NASEM Eq 2-1 without arbitrary heat multipliers. For total as-fed feed, divide by ration dry matter percentage."
        }

    def calculate_dmi_heifer(
        self,
        bw_kg: float,
        mature_bw_kg: float = 550.0,
        ration_ndf_percent: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        NASEM 2021 Equation 2-3 (NDF unknown) or Equation 2-4 (NDF known) for growing heifers.
        """
        mat_bw = max(100.0, mature_bw_kg)
        bw_ratio = min(1.0, bw_kg / mat_bw)

        if ration_ndf_percent is not None and ration_ndf_percent > 0:
            # NASEM Eq 2-4
            ndf_target = 23.1 + 56.0 * bw_ratio - 30.6 * (bw_ratio ** 2)
            dmi_val = 0.0226 * mat_bw * (1.0 - math.exp(-1.47 * bw_ratio)) - 0.082 * (ration_ndf_percent - ndf_target)
            eq_id = "NASEM_2021_EQ_2_4"
        else:
            # NASEM Eq 2-3
            dmi_val = 0.022 * mat_bw * (1.0 - math.exp(-1.54 * bw_ratio))
            eq_id = "NASEM_2021_EQ_2_3"

        dmi_val = max(1.0, round(dmi_val, 2))
        return {
            "equation_id": eq_id,
            "scientific_status": "authoritative_equation",
            "reference": "NASEM 2021 Chapter 2",
            "inputs": {
                "BW_kg": bw_kg,
                "Mature_BW_kg": mat_bw,
                "BW_MatBW_ratio": round(bw_ratio, 3),
                "Ration_NDF_percent": ration_ndf_percent
            },
            "result": {
                "dmi_kg_dm_day": dmi_val,
                "unit": "kg DM/day"
            }
        }

    def calculate_dmi_dry_cow(
        self,
        bw_kg: float,
        week_before_calving: int = -2,
        ration_ndf_percent: float = 42.0,
        is_heifer: bool = False,
        bcs: float = 3.25
    ) -> Dict[str, Any]:
        """
        NASEM 2021 Equation 12-1 (dry cows) or Equation 12-2 (heifers) for late gestation.
        """
        week = max(-3, min(0, week_before_calving))
        ndf = max(30.0, min(55.0, ration_ndf_percent))

        # Eq 12-1: DMI_kg_per_100kg_BW = 1.47 - ((0.365 - 0.0028*NDF)*Week) - 0.035*(Week^2)
        dmi_per_100kg = 1.47 - ((0.365 - 0.0028 * ndf) * week) - 0.035 * (week ** 2)

        if is_heifer:
            # Eq 12-2 applies 0.88 factor
            dmi_per_100kg *= 0.88
            eq_id = "NASEM_2021_EQ_12_2"
        else:
            eq_id = "NASEM_2021_EQ_12_1"

        if bcs > 4.0:
            dmi_per_100kg *= 0.92  # 8% reduction for overconditioned dry cows

        dmi_kg = round(bw_kg * dmi_per_100kg / 100.0, 2)
        return {
            "equation_id": eq_id,
            "scientific_status": "authoritative_equation",
            "reference": "NASEM 2021 Chapter 12, Dry and Transition Cows",
            "inputs": {
                "BW_kg": bw_kg,
                "Week_Prepartum": week,
                "Ration_NDF_percent": ndf,
                "Is_Pregnant_Heifer": is_heifer,
                "BCS": bcs
            },
            "result": {
                "dmi_kg_dm_day": dmi_kg,
                "dmi_percent_bw": round(dmi_per_100kg, 3),
                "unit": "kg DM/day"
            }
        }

    # ---------------- 2. Milk Energy Engine ---------------- #

    def calculate_milk_energy(
        self,
        milk_yield_kg: float,
        fat_percent: float = 4.0,
        true_protein_percent: Optional[float] = None,
        lactose_percent: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        NASEM 2021 Equation 3-14b (Component-based) or Equation 3-14c (Fat fallback).
        """
        if true_protein_percent is not None and true_protein_percent > 0:
            lac = lactose_percent if (lactose_percent is not None and lactose_percent > 0) else 4.85
            # Eq 3-14b
            fat_kg_per_kg = fat_percent / 100.0
            tp_kg_per_kg = true_protein_percent / 100.0
            lac_kg_per_kg = lac / 100.0
            nel_per_kg = 9.29 * fat_kg_per_kg + 5.85 * tp_kg_per_kg + 3.95 * lac_kg_per_kg
            eq_id = "NASEM_2021_EQ_3_14b"
        else:
            # Fallback Eq 3-14c
            nel_per_kg = 0.360 + 0.0969 * fat_percent
            eq_id = "NASEM_2021_EQ_3_14c"

        milk_e = milk_yield_kg * nel_per_kg
        return {
            "equation_id": eq_id,
            "scientific_status": "authoritative_equation",
            "milk_nel_mcal_per_kg": round(nel_per_kg, 4),
            "milk_e_mcal_day": round(milk_e, 3)
        }

    # ---------------- 3. Water Intake Engine ---------------- #

    def calculate_water_intake(
        self,
        category: str = "lactating_cow",
        dmi_kg: Optional[float] = None,
        ambient_temp_c: float = 27.0,
        diet_dm_percent: float = 45.0,
        diet_cp_percent: float = 16.5,
        diet_na_percent: float = 0.30,
        diet_k_percent: float = 1.30,
        milk_yield_kg: Optional[float] = None,
        dim: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        NASEM 2021 Chapter 9 Free Water Intake (FWI).
        Lactating Primary: Eq 9-1: FWI = -91.1 + 2.93*DMI + 0.61*DM% + 0.062*NaK + 2.49*CP% + 0.76*Temp
        Lactating Fallback: Eq 9-2: FWI = -60.2 + 1.43*Milk + 0.064*NaK + 0.83*DM% + 0.54*Temp + 0.08*DIM
        Dry Cow: Eq 9-3: FWI = 1.16*DMI + 0.23*DM% + 0.44*Temp + 0.061*((Temp - 16.4)^2)
        Note: Ambient temperature is already explicitly accounted for. Do NOT double-multiply by 1.44!
        """
        # Dietary Na + K concentration in mEq/kg DM: NaK = ((Na% / 0.023) + (K% / 0.039)) * 10
        nak = ((diet_na_percent / 0.023) + (diet_k_percent / 0.039)) * 10.0

        if category in ["dry_cow", "pregnant_dry_cow"]:
            dmi = dmi_kg or 11.5
            # Eq 9-3
            fwi = 1.16 * dmi + 0.23 * diet_dm_percent + 0.44 * ambient_temp_c + 0.061 * ((ambient_temp_c - 16.4) ** 2)
            eq_id = "NASEM_2021_EQ_9_3"
        elif category == "lactating_cow":
            if dmi_kg and dmi_kg > 0:
                # Primary Eq 9-1
                fwi = -91.1 + 2.93 * dmi_kg + 0.61 * diet_dm_percent + 0.062 * nak + 2.49 * diet_cp_percent + 0.76 * ambient_temp_c
                eq_id = "NASEM_2021_EQ_9_1"
            else:
                # Fallback Eq 9-2
                m = milk_yield_kg or 15.0
                d = dim or 90
                fwi = -60.2 + 1.43 * m + 0.064 * nak + 0.83 * diet_dm_percent + 0.54 * ambient_temp_c + 0.08 * d
                eq_id = "NASEM_2021_EQ_9_2"
        else:
            return {
                "equation_id": "NASEM_2021_HEIFER_WATER_NOTE",
                "scientific_status": "no_validated_NASEM_FWI_equation",
                "result": {
                    "water_fwi_l_day": None,
                    "unit": "L/day"
                },
                "rule": "Provide free-choice clean drinking water 24/7. NASEM 2021 notes older heifers/calves do not have validated FWI empirical equations; do not apply arbitrary BW*0.08 multiplier as an official NASEM standard."
            }

        fwi_l = max(10.0, round(fwi, 1))
        return {
            "equation_id": eq_id,
            "scientific_status": "authoritative_equation",
            "reference": "NASEM 2021 Chapter 9, Water",
            "inputs": {
                "category": category,
                "DMI_kg_DM_day": dmi_kg,
                "diet_dm_percent": diet_dm_percent,
                "diet_cp_percent": diet_cp_percent,
                "mean_ambient_temp_c": ambient_temp_c,
                "diet_NaK_mEq_kg_DM": round(nak, 1)
            },
            "result": {
                "water_fwi_l_day": fwi_l,
                "unit": "L/day"
            },
            "water_guidelines": [
                "Water must be freely available ad libitum (24/7 access).",
                "No arbitrary 1.44 heat multiplier is applied because ambient temperature is already an explicit scientific term in NASEM Eq 9-1/9-3."
            ]
        }

    # ---------------- 4. Energy Requirements Engine ---------------- #

    def calculate_energy_adult(
        self,
        bw_kg: float,
        milk_yield_kg: float = 0.0,
        fat_percent: float = 4.0,
        gestation_day: Optional[int] = None,
        calf_birth_weight_kg: float = 38.0
    ) -> Dict[str, Any]:
        """
        NASEM 2021 Adult Cow Net Energy of Lactation (NEL) System.
        Maintenance: NASEM Eq 3-13: NEL_maint = 0.10 * (BW^0.75) Mcal/day
        Milk: NASEM Eq 3-14b/c: NEL_milk = MilkE Mcal/day
        Gestation: NASEM Eq 3-15a to 3-18
        """
        # 1. Maintenance
        nel_maint = 0.10 * (bw_kg ** 0.75)

        # 2. Milk Energy
        nel_milk = 0.0
        if milk_yield_kg > 0:
            m_res = self.calculate_milk_energy(milk_yield_kg, fat_percent)
            nel_milk = m_res["milk_e_mcal_day"]

        # 3. Gestation (if applicable between Day 12 and 280)
        nel_gest = 0.0
        gr_uter_wt = 0.0
        if gestation_day and 12 <= gestation_day <= 280:
            # Eq 3-15a: GrUter_Wt_parturition = CalfBirthWeight * 1.825
            gr_uter_part = calf_birth_weight_kg * 1.825
            # Eq 3-16a: GrUter_Wt = GrUter_Wt_parturition * exp(-(0.0243 - 0.0000245*DayGest)*(280-DayGest))
            exp_factor = -(0.0243 - 0.0000245 * gestation_day) * (280 - gestation_day)
            gr_uter_wt = gr_uter_part * math.exp(exp_factor)
            # Eq 3-17a: GrUter_Wt_Gain = (0.0243 - 0.0000245*DayGest)*GrUter_Wt
            gr_gain = (0.0243 - 0.0000245 * gestation_day) * gr_uter_wt
            # Eq 3-18: NEL_gestation = GrUter_Wt_Gain * 4.16
            nel_gest = gr_gain * 4.16

        total_nel = nel_maint + nel_milk + nel_gest

        return {
            "energy_basis": "NEL",
            "unit": "Mcal/day",
            "breakdown": {
                "nel_maintenance_mcal_day": round(nel_maint, 2),
                "nel_milk_mcal_day": round(nel_milk, 2),
                "nel_gestation_mcal_day": round(nel_gest, 2),
                "total_nel_required_mcal_day": round(total_nel, 2)
            },
            "equations_used": [
                {"component": "maintenance", "equation_id": "NASEM_2021_EQ_3_13", "formula": "0.10 * (BW^0.75)"},
                {"component": "milk", "equation_id": "NASEM_2021_EQ_3_14c", "formula": "Milk_kg * (0.360 + 0.0969*fat%)"},
                {"component": "gestation", "equation_id": "NASEM_2021_EQ_3_18", "formula": "GrUter_Wt_Gain * 4.16"}
            ]
        }

    def calculate_energy_heifer(
        self,
        bw_kg: float,
        mature_bw_kg: float = 550.0,
        adg_kg_day: float = 0.75
    ) -> Dict[str, Any]:
        """
        NASEM 2021 Growing Heifer Metabolizable Energy (ME) System.
        Maintenance: NASEM Eq 11-2: ME_maint = 0.15 * (BW^0.75) Mcal/day
        Frame Growth: NASEM Eq 3-20a to 3-20d
        """
        # Eq 11-2
        me_maint = 0.15 * (bw_kg ** 0.75)

        # Growth components
        mat_bw = max(100.0, mature_bw_kg)
        bw_ratio = min(1.0, bw_kg / mat_bw)
        ebg = 0.85 * adg_kg_day  # Empty body weight gain
        ebg_ratio = ebg / adg_kg_day

        # Eq 3-20a: Fat_ADG = (0.067 + 0.375*(BW/MatBW))*(EBG/ADG)
        fat_adg = (0.067 + 0.375 * bw_ratio) * ebg_ratio
        # Eq 3-20b: Protein_ADG = (0.201 - 0.081*(BW/MatBW))*(EBG/ADG)
        protein_adg = (0.201 - 0.081 * bw_ratio) * ebg_ratio
        # Eq 3-20c: RE_FADG = 9.4*Fat_ADG + 5.55*Protein_ADG
        re_fadg = 9.4 * fat_adg + 5.55 * protein_adg
        # Eq 3-20d: ME_FADG = RE_FADG / 0.40
        me_fadg = re_fadg / 0.40
        me_growth = me_fadg * adg_kg_day

        total_me = me_maint + me_growth

        return {
            "energy_basis": "ME",
            "unit": "Mcal/day",
            "breakdown": {
                "me_maintenance_mcal_day": round(me_maint, 2),
                "me_growth_mcal_day": round(me_growth, 2),
                "total_me_required_mcal_day": round(total_me, 2)
            },
            "equations_used": [
                {"component": "maintenance", "equation_id": "NASEM_2021_EQ_11_2", "formula": "0.15 * (BW^0.75)"},
                {"component": "frame_growth", "equation_id": "NASEM_2021_EQ_3_20d", "formula": "RE_FADG / 0.40 * ADG"}
            ],
            "critical_distinction": "Heifer requirements use ME basis; adult lactating cow requirements use NEL basis. Never combine them into an unlabeled total."
        }

    # ---------------- 5. Mineral Factorial Requirements Engine ---------------- #

    def calculate_factorial_minerals(
        self,
        dmi_kg: float,
        bw_kg: float,
        milk_yield_kg: float = 0.0
    ) -> Dict[str, Any]:
        """
        NASEM 2021 Factorial Mineral Requirements:
        Calcium: Eq 7-1: Ca_maint_absorbed = 0.90 * DMI g/day + lactation & pregnancy
        Phosphorus: P_maint = 1.0 * DMI + 0.0006 * BW g/day; P_lactation = 0.90 * MilkYield g/day
        """
        # Calcium
        ca_maint_abs = 0.90 * dmi_kg
        ca_milk_abs = milk_yield_kg * 1.22 if milk_yield_kg > 0 else 0.0
        ca_total_absorbed = ca_maint_abs + ca_milk_abs

        # Phosphorus
        p_maint = 1.0 * dmi_kg + 0.0006 * bw_kg
        p_milk = 0.90 * milk_yield_kg if milk_yield_kg > 0 else 0.0
        p_total_absorbed = p_maint + p_milk

        return {
            "standards": "NASEM 2021 Factorial Mineral System (Chapter 7)",
            "calcium_ca": {
                "absorbed_maintenance_g_day": round(ca_maint_abs, 2),
                "absorbed_milk_g_day": round(ca_milk_abs, 2),
                "total_absorbed_ca_required_g_day": round(ca_total_absorbed, 2),
                "equation_maintenance": "NASEM_2021_EQ_7_1: 0.90 * DMI"
            },
            "phosphorus_p": {
                "maintenance_g_day": round(p_maint, 2),
                "milk_g_day": round(p_milk, 2),
                "total_absorbed_p_required_g_day": round(p_total_absorbed, 2),
                "equation_maintenance": "1.0 * DMI + 0.0006 * BW"
            },
            "mineral_mixture_protocol": [
                "1. Calculate natural feed mineral supply from feed-specific composition.",
                "2. Calculate animal factorial mineral requirements (Ca, P, Mg, etc.).",
                "3. Calculate mineral deficits (Requirement - Natural Feed Supply).",
                "4. Optimize supplement/mineral mixture dose to bridge deficits without violating upper tolerable limits.",
                "RULE: Never auto-prescribe a flat 50-130g without calculating the exact deficit."
            ]
        }

    # ---------------- 6. Query NASEM Ruleset Knowledge ---------------- #

    def query_nasem_rules(self, query: str) -> Dict[str, Any]:
        """
        Searches the NASEM 2021 Unified Feed & Nutrition Ruleset for relevant equations,
        policies, constraints, and deprecated formulas.
        """
        q_lower = query.lower()
        results: Dict[str, Any] = {
            "title": self.rules.get("title"),
            "scientific_basis": self.rules.get("scientific_basis"),
            "matches": []
        }

        # Check DMI
        if any(w in q_lower for w in ["dmi", "dry matter intake", "intake", "feed intake", "eat"]):
            results["matches"].append({
                "category": "Dry Matter Intake (DMI)",
                "rules": self.rules.get("dmi_engine")
            })

        # Check Water
        if any(w in q_lower for w in ["water", "fwi", "thirst", "drink", "free water"]):
            results["matches"].append({
                "category": "Water Intake (FWI)",
                "rules": self.rules.get("water_engine")
            })

        # Check Energy
        if any(w in q_lower for w in ["energy", "nel", "me", "mcal", "calories", "lactation energy"]):
            results["matches"].append({
                "category": "Energy Requirements (NEL / ME)",
                "rules": self.rules.get("energy_requirement_engine")
            })

        # Check Minerals
        if any(w in q_lower for w in ["mineral", "calcium", "phosphorus", "ca", "salt", "macro"]):
            results["matches"].append({
                "category": "Mineral Engine (Factorial Ca/P)",
                "rules": self.rules.get("mineral_engine")
            })

        # Check Optimization & Ration Balance
        if any(w in q_lower for w in ["balance", "balanced", "ration", "optimize", "inventory", "protein", "mp"]):
            results["matches"].append({
                "category": "Ration Optimization & Balance Status",
                "rules": {
                    "joint_optimizer": self.rules.get("joint_ration_optimizer"),
                    "balance_status": self.rules.get("balance_status_engine"),
                    "fiber_starch": self.rules.get("fiber_and_starch_policy")
                }
            })

        # Always include deprecated formulas if looking for rules
        if any(w in q_lower for w in ["deprecated", "rule", "formula", "standard", "nasem"]):
            results["deprecated_rules_to_avoid"] = self.rules.get("deprecated_rules_to_remove_from_code")

        if not results["matches"]:
            # If broad question, provide top-level executive overview of NASEM 2021 ruleset
            results["matches"].append({
                "category": "Unified NASEM 2021 Rules Overview",
                "core_architecture_rules": self.rules.get("core_architecture_rules"),
                "calculation_sequence": self.rules.get("calculation_sequence")
            })

        return results

nasem_calculator = NASEM2021Calculator()
