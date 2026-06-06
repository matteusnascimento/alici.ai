from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NotificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tipo: str
    titulo: str
    descricao: str
    horario: datetime
    lida: bool
    destino: str

