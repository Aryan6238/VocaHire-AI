from dataclasses import dataclass
import re
import fitz  # PyMuPDF is better than PyPDF2 for text layout
from typing import List, Dict

@dataclass
class ResumeAnalysis:
    name: str
    skills: List[str]
    education: List[str]
    experience: List[str]
    contact: Dict[str, str]

class ResumeParser:
    def analyze(self, file_path: str) -> ResumeAnalysis:
        text = self._extract_text(file_path)

        name = self._extract_name(text)
        skills = self._extract_skills(text)
        education = self._extract_education(text)
        experience = self._extract_experience(text)
        contact = self._extract_contact(text)

        return ResumeAnalysis(
            name=name,
            skills=skills,
            education=education,
            experience=experience,
            contact=contact
        )

    def _extract_text(self, file_path: str) -> str:
        doc = fitz.open(file_path)
        return " ".join(page.get_text() for page in doc)

    def _extract_name(self, text: str) -> str:
        lines = text.strip().split('\n')
        for line in lines[:5]:  # Assume name is in the top 5 lines
            line = line.strip()
            if re.match(r"^[A-Z][a-z]+(?:\s[A-Z][a-z]+)*$", line):
                return line
        return "Name Not Found"

    def _extract_skills(self, text: str) -> List[str]:
        keywords = ['python', 'java', 'c++', 'sql', 'ml', 'ai', 'tensorflow', 'pytorch', 'flask', 'react', 'django', 'html', 'css', 'javascript']
        found = [kw for kw in keywords if kw.lower() in text.lower()]
        return list(set(found))

    def _extract_education(self, text: str) -> List[str]:
        patterns = [
            r"(B\.?Tech|M\.?Tech|Bachelor|Master).*?(Computer|Technology|Engineering)",
            r"(University|College)\s+\w+.*?",
            r"(BCA|MCA|B\.?Sc|M\.?Sc)"
        ]
        return self._find_matches(text, patterns)

    def _extract_experience(self, text: str) -> List[str]:
        lines = text.split('\n')
        experience_lines = [line.strip() for line in lines if re.search(r"(intern|experience|developer|engineer)", line, re.IGNORECASE)]
        return list(set(experience_lines))

    def _extract_contact(self, text: str) -> Dict[str, str]:
        email = re.search(r'[\w\.-]+@[\w\.-]+', text)
        phone = re.search(r'(\+91[\-\s]?)?[6-9]\d{9}', text)
        return {
            "email": email.group(0) if email else "N/A",
            "phone": phone.group(0) if phone else "N/A"
        }

    def _find_matches(self, text: str, patterns: List[str]) -> List[str]:
        matches = []
        for pattern in patterns:
            found = re.findall(pattern, text, re.IGNORECASE)
            if found:
                for match in found:
                    if isinstance(match, tuple):
                        matches.append(" ".join(match))
                    else:
                        matches.append(match)
        return list(set(matches))
