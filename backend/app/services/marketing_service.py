from app.schemas.marketing import MarketingCampaignRequest, MarketingCampaignResponse


class MarketingService:
    def generate(self, payload: MarketingCampaignRequest) -> MarketingCampaignResponse:
        campaign = (
            f"Campanha {payload.objective} para {payload.company_name}: posicionar a oferta '{payload.offer}' "
            f"para o público {payload.audience} com tom {payload.tone}."
        )
        copy = (
            f"{payload.company_name} entrega uma forma mais rápida de {payload.objective.lower()} para {payload.audience}. "
            f"A oferta central é {payload.offer}, com comunicação {payload.tone} e foco em clareza, urgência e prova."
        )
        cta = f"Quero ativar {payload.offer} agora"
        ad_structure = (
            "Hook de dor -> prova social -> mecanismo único -> oferta -> urgência -> CTA. "
            f"Abra com uma promessa curta sobre {payload.objective.lower()} e feche convidando o lead a falar com a AXI."
        )
        creative_suggestion = (
            f"Use visual limpo, contraste alto e demonstração do resultado final para {payload.audience}. "
            "Combine screenshot do painel com headline curta e selo de automação inteligente."
        )
        return MarketingCampaignResponse(
            campaign=campaign,
            copy=copy,
            cta=cta,
            ad_structure=ad_structure,
            creative_suggestion=creative_suggestion,
        )
