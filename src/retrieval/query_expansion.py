import re
from typing import Dict, List

class MedicalQueryExpander:
    """Expands clinical queries with synonyms, standard gene symbols, and drug brand/generic names."""

    SYNONYM_MAP: Dict[str, List[str]] = {
        "sma": ["Spinal Muscular Atrophy", "SMN1 deficiency", "5q SMA"],
        "spinraza": ["nusinersen", "antisense oligonucleotide", "intrathecal nusinersen"],
        "zolgensma": ["onasemnogene abeparvovec", "AAV9 gene therapy", "AVXS-101"],
        "evrysdi": ["risdiplam", "oral SMN2 splicing modifier"],
        "smn1": ["Survival of Motor Neuron 1", "telomeric SMN"],
        "smn2": ["Survival of Motor Neuron 2", "centromeric SMN", "SMN2 copy number"],
        "long-read": ["long-read sequencing", "PacBio HiFi", "Oxford Nanopore ONT", "structural variants"],
        "rearrangements": ["chromosomal rearrangements", "balanced translocations", "inversions", "complex SVs"],
    }

    ARABIC_MAP: Dict[str, List[str]] = {
        "ضمور العضلات": ["Spinal Muscular Atrophy", "SMA", "SMN1"],
        "نوسينيرسين": ["nusinersen", "Spinraza", "antisense oligonucleotide"],
        "زولجينسما": ["onasemnogene abeparvovec", "Zolgensma", "gene therapy"],
        "ريسديبلام": ["risdiplam", "Evrysdi"],
        "بدء": ["treatment initiation", "eligibility criteria"],
        "علاج": ["treatment", "therapy", "management recommendations"],
        "جرعة": ["dosing", "dose", "loading doses", "maintenance"],
        "تشخيص": ["diagnosis", "screening", "genetic testing", "exome"],
        "كروموسوم": ["chromosomal rearrangements", "structural variants"],
        "طفرة": ["mutation", "variant", "deletion", "duplication"]
    }

    def expand(self, query: str) -> str:
        """Enriches the query with domain synonyms without overriding the original intent."""
        query_lower = query.lower()
        expansions = []

        # Check English synonyms
        for key, terms in self.SYNONYM_MAP.items():
            if re.search(r'\b' + re.escape(key) + r'\b', query_lower):
                expansions.extend(terms[:2])

        # Check Arabic clinical terms
        for ar_key, terms in self.ARABIC_MAP.items():
            if ar_key in query:
                expansions.extend(terms[:2])

        if expansions:
            unique_expansions = list(dict.fromkeys(expansions))
            expanded_query = f"{query} {' '.join(unique_expansions)}"
            return expanded_query
        return query

