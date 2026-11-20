#!/usr/bin/env python3
"""Gera locuções pt-PT-RaquelNeural para a Montanha da Tabuada."""
from __future__ import annotations
import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
import edge_tts

VOICE = 'pt-PT-RaquelNeural'
OUT = Path(__file__).resolve().parent.parent / 'tabuada-quest' / 'audio' / 'raquel'
TEXT = {
    'intro': 'Bem-vindo à Montanha da Tabuada! Vamos chegar ao Topo dos Mestres.',
    'correct': 'Muito bem!',
    'incorrect': 'Tenta novamente na próxima vez.',
    'timeout': 'Tempo esgotado!',
    'recovery_success': 'Muito bem! Recuperaste os pontos!',
    'recovery_fail': 'Ainda não recuperaste os pontos. Podes tentar de novo.',
    'session_up': 'Muito bem, o alpinista subiu!',
    'session_down': 'O alpinista desceu um pouco. Vamos continuar a aprender.',
    'session_stay': 'O alpinista manteve a posição.',
}
for a in range(2,13):
    TEXT[f'recovery_{a}'] = f'Agora vamos recuperar a tabuada do {a}. Coloca os dez resultados nos espaços certos.'
    for b in range(1,13):
        TEXT[f'q_{a}_{b}'] = f'Quanto é {a} vezes {b}?'

async def write_clip(sema:asyncio.Semaphore,key:str,phrase:str):
    target=OUT / f'{key}.mp3'
    if target.is_file() and target.stat().st_size>100:
        return
    async with sema:
        last=None
        for trial in range(4):
            try:
                tmp=OUT / f'{key}.working.mp3'
                reader=edge_tts.Communicate(text=phrase,voice=VOICE,rate='-4%')
                await reader.save(str(tmp))
                if tmp.stat().st_size<100: raise RuntimeError('Audio vazio')
                tmp.replace(target)
                print('OK',key,target.stat().st_size,flush=True)
                return
            except Exception as exc:
                last=exc
                try:tmp.unlink(missing_ok=True)
                except Exception:pass
                await asyncio.sleep(2+trial*2)
        raise RuntimeError(f'Não foi possível gerar {key}: {last}')

async def main():
    OUT.mkdir(parents=True,exist_ok=True)
    semaphore=asyncio.Semaphore(3)
    await asyncio.gather(*(write_clip(semaphore,key,phrase) for key,phrase in TEXT.items()))
    manifest={
        'voice':VOICE,
        'format':'mp3',
        'clips':len(TEXT),
        'generated_at':datetime.now(timezone.utc).isoformat(),
        'file_names':sorted(f'{key}.mp3' for key in TEXT),
    }
    (OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Gerados {len(TEXT)} MP3s com {VOICE}')

if __name__=='__main__':
    asyncio.run(main())
