---
applyTo: "backend/app/**/*.py"
---

# Padrões Backend — alici.ai

## Serviços
- Classe `XxxService(db: Session)`; validações privadas com prefixo `_` retornam o objeto ou levantam `HTTPException`
- `db.commit()` + `db.refresh()` após cada write; nunca retornar objeto antes do refresh

## Rotas FastAPI
- Sempre `response_model=XxxRead`; serializar com `XxxRead.model_validate(obj)`
- Dependências via `Depends(get_current_user)` e `Depends(get_db)` — nunca construir sessão manualmente na rota

## Modelos SQLAlchemy
- Usar estilo 2.0: `Mapped[T]` / `mapped_column`; timestamps com `timezone=True`
- FK com `ondelete="CASCADE"`; relações com `cascade="all, delete-orphan"` e `back_populates`

## Schemas Pydantic
- Separar `*Create` (entrada), `*Read` (saída com `from_attributes=True`), `*Update` (patch parcial)
- Validações de entrada em schemas, não em serviços

## Segurança
- Nunca expor senha ou token em respostas
- Toda rota que acessa dados do usuário deve ter `Depends(get_current_user)`
- Não usar `eval()`, `exec()`, ou deserialização insegura
