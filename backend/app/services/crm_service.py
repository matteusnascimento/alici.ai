import os
import logging
import requests
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class CRMService:
    """Serviço para integração com CRMs externos."""

    def __init__(self, provider: str = "pipedrive", api_key: Optional[str] = None):
        self.provider = provider.lower()
        self.api_key = api_key or os.getenv(f"{provider.upper()}_API_KEY")

        if not self.api_key:
            logger.warning(f"{provider.upper()}_API_KEY not configured, CRM integration disabled")

    def register_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Registra lead no CRM.

        Args:
            lead_data: Dados do lead (name, email, phone, company, stage, notes)

        Returns:
            Dict com resultado do registro
        """
        if not self.api_key:
            return {
                "status": "error",
                "message": f"Lead nao registrado: {self.provider} nao esta configurado",
                "lead_data": lead_data,
            }

        try:
            if self.provider == "pipedrive":
                return self._register_pipedrive(lead_data)
            elif self.provider == "hubspot":
                return self._register_hubspot(lead_data)
            else:
                raise ValueError(f"CRM provider '{self.provider}' not supported")

        except Exception as e:
            logger.error("Failed to register lead in CRM: %s", e)
            return {
                "status": "error",
                "message": f"Erro ao registrar lead: {str(e)}",
                "lead_data": lead_data,
            }

    def _register_pipedrive(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Registra lead no Pipedrive."""
        url = "https://api.pipedrive.com/v1/persons"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        # Mapeia dados para formato Pipedrive
        person_data = {
            "name": lead_data["name"],
            "email": [{"value": lead_data["email"], "primary": True}],
            "phone": [{"value": lead_data.get("phone"), "primary": True}] if lead_data.get("phone") else None,
            "org_name": lead_data.get("company"),
        }

        # Remove campos None
        person_data = {k: v for k, v in person_data.items() if v is not None}

        response = requests.post(url, json=person_data, headers=headers, timeout=10)
        response.raise_for_status()

        person = response.json()["data"]

        # Se tem notes, adiciona como nota
        if lead_data.get("notes"):
            self._add_pipedrive_note(person["id"], lead_data["notes"])

        logger.info("Lead registered in Pipedrive: id=%s, name=%s", person["id"], person["name"])

        return {
            "status": "registered",
            "crm_id": person["id"],
            "crm_provider": "pipedrive",
            "lead_data": lead_data,
        }

    def _add_pipedrive_note(self, person_id: int, content: str) -> None:
        """Adiciona nota a pessoa no Pipedrive."""
        url = "https://api.pipedrive.com/v1/notes"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        note_data = {
            "person_id": person_id,
            "content": content,
            "pinned_to_person_flag": 1,
        }

        try:
            response = requests.post(url, json=note_data, headers=headers, timeout=10)
            response.raise_for_status()
        except Exception as e:
            logger.warning("Failed to add note to Pipedrive person: %s", e)

    def _register_hubspot(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Registra lead no HubSpot."""
        url = "https://api.hubapi.com/crm/v3/objects/contacts"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        # Mapeia dados para formato HubSpot
        contact_data = {
            "properties": {
                "firstname": lead_data["name"].split()[0] if " " in lead_data["name"] else lead_data["name"],
                "lastname": " ".join(lead_data["name"].split()[1:]) if " " in lead_data["name"] else "",
                "email": lead_data["email"],
                "phone": lead_data.get("phone", ""),
                "company": lead_data.get("company", ""),
                "lifecyclestage": self._map_stage_to_hubspot(lead_data.get("stage", "lead")),
                "notes_last_contacted": lead_data.get("notes", ""),
            }
        }

        response = requests.post(url, json=contact_data, headers=headers, timeout=10)
        response.raise_for_status()

        contact = response.json()

        logger.info("Lead registered in HubSpot: id=%s, name=%s", contact["id"], lead_data["name"])

        return {
            "status": "registered",
            "crm_id": contact["id"],
            "crm_provider": "hubspot",
            "lead_data": lead_data,
        }

    def _map_stage_to_hubspot(self, stage: str) -> str:
        """Mapeia stage para valores do HubSpot."""
        mapping = {
            "lead": "lead",
            "qualified": "marketingqualifiedlead",
            "proposal": "salesqualifiedlead",
            "negotiation": "opportunity",
            "closed": "customer",
        }
        return mapping.get(stage, "lead")
