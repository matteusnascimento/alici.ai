import os
import logging
from typing import Optional
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content

logger = logging.getLogger(__name__)


class EmailService:
    """Serviço para envio de emails usando SendGrid."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("SENDGRID_API_KEY")
        if not self.api_key:
            logger.warning("SENDGRID_API_KEY not configured, emails will be logged only")

    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        from_email: Optional[str] = None,
        template: Optional[str] = None,
    ) -> dict[str, str]:
        """
        Envia email usando SendGrid.

        Args:
            to_email: Email do destinatário
            subject: Assunto do email
            body: Corpo do email
            from_email: Email do remetente (opcional)
            template: Template a usar (opcional)

        Returns:
            Dict com status do envio
        """
        from_email = from_email or os.getenv("FROM_EMAIL", "noreply@axi.com")

        # Aplica template se especificado
        if template:
            body = self._apply_template(template, body)

        # Se não tem API key, apenas loga
        if not self.api_key:
            logger.info(
                "Email would be sent: to=%s, subject=%s, template=%s",
                to_email, subject, template
            )
            return {
                "status": "logged",
                "message": "Email logged (SendGrid not configured)",
                "to_email": to_email,
                "subject": subject,
            }

        try:
            sg = SendGridAPIClient(self.api_key)
            from_email_obj = Email(from_email)
            to_email_obj = To(to_email)
            content = Content("text/html", body)

            mail = Mail(from_email_obj, to_email_obj, subject, content)
            response = sg.send(mail)

            logger.info(
                "Email sent successfully: to=%s, subject=%s, status=%s",
                to_email, subject, response.status_code
            )

            return {
                "status": "sent",
                "message": f"Email enviado com sucesso (status: {response.status_code})",
                "to_email": to_email,
                "subject": subject,
            }

        except Exception as e:
            logger.error("Failed to send email: %s", e)
            return {
                "status": "error",
                "message": f"Erro ao enviar email: {str(e)}",
                "to_email": to_email,
                "subject": subject,
            }

    def _apply_template(self, template: str, body: str) -> str:
        """Aplica template ao corpo do email."""
        templates = {
            "welcome": self._welcome_template,
            "proposal": self._proposal_template,
            "reminder": self._reminder_template,
        }

        template_func = templates.get(template)
        if template_func:
            return template_func(body)
        return body

    def _welcome_template(self, body: str) -> str:
        """Template de boas-vindas."""
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 20px; text-align: center; color: white;">
                <h1>🎉 Bem-vindo à AXI!</h1>
                <p>Estamos felizes em tê-lo conosco</p>
            </div>
            <div style="padding: 30px 20px; background: #f9f9f9;">
                {body}
            </div>
            <div style="background: #333; color: white; padding: 20px; text-align: center;">
                <p>© 2026 AXI Platform. Todos os direitos reservados.</p>
            </div>
        </body>
        </html>
        """

    def _proposal_template(self, body: str) -> str:
        """Template de proposta."""
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 20px; text-align: center; color: white;">
                <h1>📋 Sua Proposta Personalizada</h1>
                <p>Preparada especialmente para você</p>
            </div>
            <div style="padding: 30px 20px; background: white; border-left: 4px solid #667eea;">
                {body}
            </div>
            <div style="background: #f0f0f0; padding: 20px; text-align: center; color: #666;">
                <p>Esta proposta foi gerada automaticamente pelo nosso assistente IA.</p>
                <p>Para dúvidas, entre em contato conosco.</p>
            </div>
        </body>
        </html>
        """

    def _reminder_template(self, body: str) -> str:
        """Template de lembrete."""
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 40px 20px; text-align: center; color: white;">
                <h1>⏰ Lembrete Importante</h1>
                <p>Não esqueça desta informação</p>
            </div>
            <div style="padding: 30px 20px; background: white;">
                {body}
            </div>
            <div style="background: #333; color: white; padding: 20px; text-align: center;">
                <p>© 2026 AXI Platform</p>
            </div>
        </body>
        </html>
        """