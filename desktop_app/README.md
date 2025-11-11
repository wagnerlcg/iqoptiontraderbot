# IQ Option Bot — Aplicação Desktop

Esta pasta contém a base da interface desktop moderna do robô. A arquitetura foi montada em camadas para facilitar evolução e reutilização:

- `bot_service.py`: camada core (compartilhada com web e desktop)
- `desktop_app/controllers`: integra a UI com o serviço, usando `QThreadPool`
- `desktop_app/ui`: componentes PySide6 (janela principal, páginas, estilos)

## Pré-requisitos

```bash
pip install PySide6 python-dotenv
```

## Executando em modo desenvolvimento

```bash
python -m iqoptionapi.desktop_app.main
```

## Próximos passos

- Conectar as ações de configuração, upload de sinais, histórico completo etc.
- Refinar o layout com gráficos e indicadores.
- Empacotar com PyInstaller / Briefcase / Flet (a definir).


