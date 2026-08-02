# v0.2.17
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

import json
import urllib.request
from genlayer import *

class GenAudit(gl.Contract):
    last_project: str
    last_trust_score: u256
    last_risk_level: str
    last_summary: str
    last_audit_json: str
    total_audits: u256

    def __init__(self):
        self.last_project = ""
        self.last_trust_score = u256(0)
        self.last_risk_level = "Unknown"
        self.last_summary = ""
        self.last_audit_json = "{}"
        self.total_audits = u256(0)

    @gl.public.write
    def audit_project(self, project_name: str, target_url: str) -> str:
        p_name = project_name.strip()
        url = target_url.strip()
        if not url.startswith("http"):
            url = "https://" + url

        # Fetching live context from the web securely
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                web_context = response.read().decode('utf-8')[:4000]
        except Exception:
            # Fallback live financial endpoint for crypto/Web3 context
            fallback_url = f"https://www.coingecko.com/en/coins/{p_name.lower().replace(' ', '-')}"
            try:
                req_fb = urllib.request.Request(fallback_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req_fb, timeout=10) as resp_fb:
                    web_context = resp_fb.read().decode('utf-8')[:4000]
            except Exception:
                web_context = f"Autonomous Web3 project audit context for {p_name} at {url}."

        prompt = f"""
        You are an expert Web3 smart contract auditor and security risk analyst. Conduct a comprehensive security and trust assessment of the project: {p_name} based on the live fetched source context below.

        Project URL: {url}
        Live Source Context:
        {web_context}

        Evaluation Rules for Multi-Validator Consensus:
        - "project_name": string
        - "trust_score": integer from 0 to 100 representing overall reliability and security.
        - "risk_level": string strictly ("Low", "Medium", "High", or "Critical").
        - "security_findings": list of strings detailing key observations (e.g., audits, documentation, transparency).
        - "summary": a concise 2-sentence executive summary of the audit.

        Respond strictly in valid JSON format with keys: "project_name", "trust_score", "risk_level", "security_findings", and "summary".
        """

        res = gl.eq_principle.prompt_non_comparative(
            lambda: prompt,
            task=f"Conduct autonomous Web3 audit for {p_name} using live web context",
            criteria="Validators must independently agree on the trust score, risk level, and security findings derived from the actual fetched source evidence, returning a valid JSON object with project_name, trust_score, risk_level, security_findings, and summary."
        )

        try:
            parsed = json.loads(str(res))
            t_score = int(parsed.get("trust_score", 50))
            r_level = str(parsed.get("risk_level", "Medium"))
            summary_val = str(parsed.get("summary", ""))
        except Exception:
            t_score = 50
            r_level = "Medium"
            summary_val = str(res)

        self.last_project = p_name
        self.last_trust_score = u256(t_score)
        self.last_risk_level = r_level
        self.last_summary = summary_val
        self.last_audit_json = str(res)
        self.total_audits = self.total_audits + u256(1)

        return str(res)

    @gl.public.view
    def get_last_audit(self) -> str:
        return self.last_audit_json

    @gl.public.view
    def get_stats(self) -> u256:
        return self.total_audits
