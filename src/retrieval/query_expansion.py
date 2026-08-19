import re
from typing import Dict, List

class MedicalQueryExpander:
    """Expands clinical queries with synonyms, standard gene symbols, and drug brand/generic names."""

    SYNONYM_MAP: Dict[str, List[str]] = {
        "sma": ["Spinal Muscular Atrophy", "SMN1", "5q SMA"],
        "spinraza": ["nusinersen", "antisense", "intrathecal"],
        "zolgensma": ["onasemnogene", "abeparvovec", "AAV9", "AVXS-101"],
        "evrysdi": ["risdiplam", "splicing"],
        "smn1": ["Survival Motor Neuron 1"],
        "smn2": ["Survival Motor Neuron 2", "copy number"],
        "long-read": ["PacBio", "HiFi", "Nanopore", "ONT", "structural variants"],
        "rearrangements": ["translocations", "inversions", "SVs"],
        "coffee": ["caffeine", "caffeine-rich", "lifestyle"],
        "coffe": ["coffee", "caffeine", "lifestyle"],
        "caffeine": ["coffee", "caffeine-rich"],
        "preasure": ["pressure"],
    }

    ARABIC_MAP: Dict[str, List[str]] = {
        "ضمور العضلات": ["SMA", "SMN1"],
        "نوسينيرسين": ["nusinersen", "Spinraza"],
        "زولجينسما": ["onasemnogene", "abeparvovec", "Zolgensma"],
        "ريسديبلام": ["risdiplam", "Evrysdi"],
        "بدء": ["initiation", "eligibility"],
        "علاج": ["treatment", "therapy"],
        "جرعة": ["dosing", "loading", "maintenance"],
        "تشخيص": ["diagnosis", "screening"],
        "كروموسوم": ["chromosomal", "rearrangements"],
        "طفرة": ["mutation", "variant", "deletion"],
        "ضغط الدم": ["hypertension", "blood pressure"],
        "القهوة": ["coffee", "caffeine"],
        "كافيين": ["caffeine", "coffee"],
    }

    def expand(self, query: str) -> str:
        """Enriches the query with domain synonyms without overriding the original intent."""
        query_lower = query.lower()
        expansions = []

        # Check English synonyms
        for key, terms in self.SYNONYM_MAP.items():
            if re.search(r'\b' + re.escape(key) + r'\b', query_lower):
                expansions.extend(terms)

        # Check Arabic clinical terms
        for ar_key, terms in self.ARABIC_MAP.items():
            if ar_key in query:
                expansions.extend(terms)

        if expansions:
            # Deduplicate added tokens so we do not inflate generic words
            existing_tokens = set(query_lower.split())
            new_tokens = [t for term in expansions for t in term.split() if t.lower() not in existing_tokens]
            unique_new = list(dict.fromkeys(new_tokens))
            if unique_new:
                return f"{query} {' '.join(unique_new)}"
        return query


