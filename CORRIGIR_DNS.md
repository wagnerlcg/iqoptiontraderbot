# Corrigir DNS e Configuração Conflitante

## 🔴 Problema Identificado

1. **DNS incorreto**: `nomadtradersystem.com` aponta para `10.16.0.104` (IP interno)
2. **IP correto do servidor**: `200.9.22.250` (IP externo)
3. **Configuração conflitante**: Aviso sobre "seu-dominio.com" na porta 80

## ✅ Solução

### Passo 1: Corrigir DNS

Você precisa atualizar o DNS para apontar para o IP externo correto:

**Configure no seu provedor de DNS:**
```
Tipo: A
Nome: nomadtradersystem.com
Valor: 200.9.22.250
TTL: 3600 (ou padrão)

Tipo: A
Nome: www.nomadtradersystem.com
Valor: 200.9.22.250
TTL: 3600 (ou padrão)
```

**Aguarde propagação DNS** (pode levar de alguns minutos a algumas horas).

### Passo 2: Limpar Configuração Conflitante

```bash
# Procurar configurações com "seu-dominio.com"
sudo grep -r "seu-dominio.com" /etc/nginx/sites-available/
sudo grep -r "seu-dominio.com" /etc/nginx/sites-enabled/

# Remover ou comentar essas configurações
sudo nano /etc/nginx/sites-available/iqoptiontraderbot
# Procure por "seu-dominio.com" e remova ou comente
```

### Passo 3: Verificar Propagação DNS

```bash
# Verificar se DNS já propagou
nslookup nomadtradersystem.com
dig nomadtradersystem.com

# Deve mostrar: 200.9.22.250
```

### Passo 4: Tentar Criar Certificados Novamente

**Após DNS propagar:**

```bash
# Verificar DNS primeiro
nslookup nomadtradersystem.com
# Deve mostrar 200.9.22.250

# Tentar criar certificados
sudo certbot --nginx -d nomadtradersystem.com -d www.nomadtradersystem.com
```

## 🔄 Solução Temporária: Usar DNS-01 Challenge

Se não conseguir corrigir DNS imediatamente ou quiser criar certificados agora:

```bash
# Criar certificados usando DNS-01 (não precisa de porta 80)
sudo certbot certonly --manual --preferred-challenges dns -d nomadtradersystem.com -d www.nomadtradersystem.com
```

**Durante a execução:**
1. Certbot vai pedir para adicionar registro TXT no DNS
2. Adicione o registro TXT no seu provedor de DNS
3. Aguarde propagação (alguns minutos)
4. Pressione Enter para continuar
5. Certificados serão criados

**Depois configure Nginx manualmente com os certificados criados.**

## 📝 Resumo dos Problemas

1. ✅ **Nginx**: Rodando corretamente na porta 80
2. ✅ **Firewall**: Não está bloqueando (inactive)
3. ❌ **DNS**: Aponta para IP interno (10.16.0.104) ao invés de externo (200.9.22.250)
4. ⚠️ **Configuração**: Há conflito com "seu-dominio.com"

## 🎯 Próximos Passos

1. **Corrigir DNS** para apontar para `200.9.22.250`
2. **Aguardar propagação DNS** (use `nslookup` para verificar)
3. **Limpar configuração conflitante** do "seu-dominio.com"
4. **Tentar criar certificados novamente**

**OU** usar DNS-01 challenge enquanto aguarda correção do DNS.

