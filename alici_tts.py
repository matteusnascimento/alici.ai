#!/usr/bin/env python3
"""
🔊 MÓDULO DE TEXT-TO-SPEECH - ALICI™
Converte respostas em áudio usando gTTS (Google Text-to-Speech)

Criador: Mateus Nascimento dos Santos
Data: 2026-01-24
"""

import os
import tempfile
from pathlib import Path

try:
    from gtts import gTTS
    GTTS_DISPONIVEL = True
except ImportError:
    GTTS_DISPONIVEL = False
    print("⚠️  gTTS não instalado. Use: pip install gtts")


class AliciTTS:
    """Text-to-Speech para ALICI™"""
    
    def __init__(self, idioma="pt", velocidade_lenta=False):
        """
        Inicializa o TTS
        
        Args:
            idioma: 'pt' (português), 'en' (english), 'es' (español)
            velocidade_lenta: True para áudio mais lento
        """
        self.idioma = idioma
        self.velocidade_lenta = velocidade_lenta
        self.disponivel = GTTS_DISPONIVEL
        
        if not self.disponivel:
            print("⚠️  TTS desativado. Instale: pip install gtts")
    
    def converter(self, texto: str, arquivo_saida: str = None) -> str:
        """
        Converte texto em áudio
        
        Args:
            texto: Texto a converter
            arquivo_saida: Caminho para salvar MP3 (default: temp)
        
        Returns:
            Caminho do arquivo de áudio gerado
        """
        
        if not self.disponivel:
            print("❌ gTTS não disponível")
            return None
        
        if not texto or len(texto) == 0:
            print("❌ Texto vazio")
            return None
        
        try:
            print(f"🔊 Convertendo para áudio ({len(texto)} caracteres)...")
            
            # Criar TTS
            tts = gTTS(texto, lang=self.idioma, slow=self.velocidade_lenta)
            
            # Salvar
            if arquivo_saida is None:
                # Usar arquivo temporário
                arquivo_saida = os.path.join(tempfile.gettempdir(), "alici_audio.mp3")
            
            tts.save(arquivo_saida)
            
            tamanho_kb = Path(arquivo_saida).stat().st_size / 1024
            print(f"✅ Áudio gerado: {arquivo_saida} ({tamanho_kb:.1f} KB)")
            
            return arquivo_saida
        
        except Exception as e:
            print(f"❌ Erro ao converter: {e}")
            return None
    
    def converter_em_memoria(self, texto: str) -> bytes:
        """
        Converte texto em áudio (retorna bytes)
        Útil para streaming
        
        Args:
            texto: Texto a converter
        
        Returns:
            Bytes do arquivo MP3
        """
        
        if not self.disponivel:
            return None
        
        try:
            tts = gTTS(texto, lang=self.idioma, slow=self.velocidade_lenta)
            
            # Salvar em buffer de memória
            import io
            buffer = io.BytesIO()
            tts.write_to_fp(buffer)
            buffer.seek(0)
            
            return buffer.getvalue()
        
        except Exception as e:
            print(f"❌ Erro: {e}")
            return None


# ============================================================================
# INTEGRAÇÃO COM ALICI™
# ============================================================================

def converter_resposta_audio(resposta: str, idioma: str = "pt") -> str:
    """
    Converte uma resposta da Alici em áudio
    
    Args:
        resposta: Texto da resposta
        idioma: Código do idioma
    
    Returns:
        Caminho do arquivo de áudio
    """
    
    tts = AliciTTS(idioma=idioma)
    
    if not tts.disponivel:
        print("⚠️  TTS não disponível")
        return None
    
    # Limpar resposta (remover links, símbolos especiais)
    resposta_limpa = resposta.replace("http", "").replace("@", "").replace("#", "")
    resposta_limpa = resposta_limpa[:500]  # Máximo 500 caracteres
    
    # Converter
    arquivo = tts.converter(resposta_limpa)
    
    return arquivo


# ============================================================================
# SCRIPT DE TESTE
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("🔊 TESTE DE TEXT-TO-SPEECH - ALICI™")
    print("=" * 70)
    print()
    
    if not GTTS_DISPONIVEL:
        print("❌ gTTS não instalado")
        print("   Instale: pip install gtts")
        print()
        exit(1)
    
    # Criar TTS
    tts = AliciTTS(idioma="pt", velocidade_lenta=False)
    
    # Textos de teste
    textos = [
        "Olá! Eu sou a Alici, uma inteligência artificial desenvolvida para aprender e evoluir.",
        "Posso ajudar você com perguntas, conselhos e conversas.",
        "Meu criador é Mateus Nascimento dos Santos.",
    ]
    
    print("🔊 Gerando áudios de teste...\n")
    
    for i, texto in enumerate(textos, 1):
        arquivo = tts.converter(
            texto,
            f"alici_audio_{i}.mp3"
        )
        if arquivo:
            print(f"✅ Arquivo {i}: {arquivo}")
        print()
    
    print("=" * 70)
    print("✅ TESTE CONCLUÍDO")
    print("=" * 70)
