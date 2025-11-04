# Resolver conflito no git pull

## Opção 1: Descartar alterações locais (use se não precisar delas)

```bash
cd /var/www/iqoptiontraderbot
git checkout -- wsgi.py
git pull origin main
```

## Opção 2: Salvar alterações locais temporariamente

```bash
cd /var/www/iqoptiontraderbot
git stash
git pull origin main
git stash pop  # Reaplica suas alterações locais (pode haver conflitos)
```

## Opção 3: Ver o que mudou localmente antes de decidir

```bash
cd /var/www/iqoptiontraderbot
git diff wsgi.py
```

Depois de ver as diferenças, você pode:
- Descartar: `git checkout -- wsgi.py`
- Ou salvar: `git stash`

## Opção 4: Fazer commit das alterações locais primeiro

```bash
cd /var/www/iqoptiontraderbot
git add wsgi.py
git commit -m "Alteracoes locais no wsgi.py"
git pull origin main
# Se houver conflitos, resolva manualmente
```

## Recomendação

Como estamos em produção e você precisa atualizar, recomendo a **Opção 1** (descartar alterações locais) ou a **Opção 2** (salvar temporariamente) para ver o que mudou.

