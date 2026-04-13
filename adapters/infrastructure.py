from .base import BaseAdapter
from core import DataPoint, Target
from typing import List
import whois
import re
import socket

class InfrastructureAdapter(BaseAdapter):
    def __init__(self):
        super().__init__(name="WHOIS/Infrastructure", category="Technical Infrastructure")

    def _derive_domains(self, company_name: str) -> List[str]:
        """Simple heuristic to guess potential domains based on company name."""
        clean_name = re.sub(r'[^a-zA-Z0-9]', '', company_name.lower())
        if not clean_name:
            return []
        return [f"{clean_name}.com", f"{clean_name}.org", f"{clean_name}.io", f"{clean_name}.ai"]

    def execute(self, target: Target) -> List[DataPoint]:
        results = []
        if not target.company:
            return results

        domains = self._derive_domains(target.company)
        
        for domain in domains:
            self._apply_opsec_delay(1.5, 3.5) # delays between whois lookups
            try:
                # 1. Resolve IP addresses first to fulfill IP addressing requirements
                ip_addresses = []
                try:
                    ip_addresses.append(socket.gethostbyname(domain))
                except socket.gaierror:
                    pass
                    
                w = whois.whois(domain)
                if w and w.domain_name:
                    status = w.status
                    if isinstance(status, list):
                        status = status[0]
                    
                    desc = f"Domain is registered. Associated emails: {w.emails if w.emails else 'None'}. Resolved IPs: {ip_addresses}"
                    
                    pt = DataPoint(
                        source_module=self.name,
                        category=self.category,
                        value=f"Domain: {domain}",
                        description=desc,
                        url=f"whois://{domain}"
                    )
                    results.append(pt)
            except Exception as e:
                pass

        return results
