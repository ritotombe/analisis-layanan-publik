"""
Demographic Detector — deteksi kelompok warga terdampak.

Menjawab pertanyaan riset D:
"Siapa kelompok warga yang paling terkena dampak?"
"""

from config.classifiers import DEMOGRAPHIC_GROUPS


class DemographicDetector:
    """Deteksi kelompok demografis yang disebutkan dalam teks."""

    def detect(self, text: str) -> dict:
        """
        Deteksi semua kelompok demografis yang disebutkan.
        
        Returns:
            {
                "groups": [
                    {"key": "lansia", "name": "Lansia", "icon": "👴", "matches": [...]},
                    ...
                ],
                "group_keys": ["lansia", "disabilitas", ...]
            }
        """
        if not text:
            return {"groups": [], "group_keys": []}

        text_lower = text.lower()
        found = []

        for group_key, group_data in DEMOGRAPHIC_GROUPS.items():
            matches = []
            for pattern in group_data["patterns"]:
                if pattern.lower() in text_lower:
                    matches.append(pattern)

            if matches:
                found.append({
                    "key": group_key,
                    "name": group_data["name"],
                    "icon": group_data["icon"],
                    "matches": matches,
                })

        return {
            "groups": found,
            "group_keys": [g["key"] for g in found],
        }

    def get_demographic_summary(self, results: list[dict]) -> dict:
        """
        Agregasi deteksi demografis dari banyak artikel.
        
        Returns:
            {
                "by_group": {
                    "lansia": {"count": 23, "name": "Lansia", "icon": "👴"},
                    ...
                },
                "total_with_demographics": int,
                "ranking": [(group_key, count), ...],
            }
        """
        group_counts = {}
        total_with = 0

        for result in results:
            groups = result.get("groups", [])
            if groups:
                total_with += 1

            for group in groups:
                key = group["key"]
                if key not in group_counts:
                    group_counts[key] = {
                        "count": 0,
                        "name": group["name"],
                        "icon": group["icon"],
                    }
                group_counts[key]["count"] += 1

        return {
            "by_group": group_counts,
            "total_with_demographics": total_with,
            "ranking": sorted(
                group_counts.items(),
                key=lambda x: x[1]["count"],
                reverse=True,
            ),
        }
