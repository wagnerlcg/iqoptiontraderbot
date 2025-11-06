# Corrigir Registros DNS TXT para Certificados SSL

## 🔴 Problemas Identificados

1. **nomadtradersystem.com**: Registro TXT existe mas com valor errado
   - Esperado: `LuxBwM8MtAFwTgvLpYAIs_SD-B6NLY2IcyDPsizEdnQ`
   - Encontrado: `cDpaPxcxcqvvyKgk5jtg746up1dnn5aFnM1GQovwvdI`

2. **www.nomadtradersystem.com**: Registro TXT não encontrado
   - Esperado: `EhoG1jlvTwP9mItvXLDCvx_Y1xrTURS1iU5LO6BvvLY`

## ✅ Solução

### Passo 1: Verificar Registros DNS Atuais

No seu provedor de DNS, verifique os registros TXT existentes:

**Registros necessários:**
```
Tipo: TXT
Nome: _acme-challenge.nomadtradersystem.com
Valor: LuxBwM8MtAFwTgvLpYAIs_SD-B6NLY2IcyDPsizEdnQ

Tipo: TXT
Nome: _acme-challenge.www.nomadtradersystem.com
Valor: EhoG1jlvTwP9mItvXLDCvx_Y1xrTURS1iU5LO6BvvLY
```

### Passo 2: Corrigir/Criar Registros TXT

**No seu provedor de DNS:**

1. **Para `nomadtradersystem.com`:**
   - Encontre o registro TXT existente: `_acme-challenge.nomadtradersystem.com`
   - **Remova o valor antigo**: `cDpaPxcxcqvvyKgk5jtg746up1dnn5aFnM1GQovwvdI`
   - **Adicione o valor correto**: `LuxBwM8MtAFwTgvLpYAIs_SD-B6NLY2IcyDPsizEdnQ`

2. **Para `www.nomadtradersystem.com`:**
   - **Crie novo registro TXT**:
     - Nome: `_acme-challenge.www.nomadtradersystem.com`
     - Valor: `EhoG1jlvTwP9mItvXLDCvx_Y1xrTURS1iU5LO6BvvLY`

### Passo 3: Verificar Propagação DNS

Após criar/corrigir os registros, aguarde alguns minutos e verifique:

```bash
# Verificar registro TXT para nomadtradersystem.com
dig TXT _acme-challenge.nomadtradersystem.com +short

# Verificar registro TXT para www.nomadtradersystem.com
dig TXT _acme-challenge.www.nomadtradersystem.com +short

# Ou usar nslookup
nslookup -type=TXT _acme-challenge.nomadtradersystem.com
nslookup -type=TXT _acme-challenge.www.nomadtradersystem.com
```

**Os valores devem corresponder exatamente aos solicitados pelo Certbot.**

### Passo 4: Tentar Novamente

Após verificar que os registros estão corretos e propagados:

```bash
# Tentar criar certificados novamente
sudo certbot certonly --manual --preferred-challenges dns -d nomadtradersystem.com -d www.nomadtradersystem.com
```

**Durante a execução:**
- O Certbot vai pedir os mesmos registros TXT novamente
- Use os valores que ele solicitar (podem ser diferentes desta vez)
- Crie/corrija os registros DNS
- Aguarde propagação
- Pressione Enter

## 🔍 Verificação Online

Você pode usar ferramentas online para verificar:

1. **Google Admin Toolbox:**
   - https://toolbox.googleapps.com/apps/dig/#TXT/_acme-challenge.nomadtradersystem.com
   - https://toolbox.googleapps.com/apps/dig/#TXT/_acme-challenge.www.nomadtradersystem.com

2. **DNS Checker:**
   - https://dnschecker.org/#TXT/_acme-challenge.nomadtradersystem.com

## ⚠️ Importante

- **Remova registros TXT antigos** antes de adicionar novos
- **Aguarde propagação DNS** (geralmente 5-30 minutos)
- **Use valores exatos** - sem espaços extras
- **Ambos os registros** devem existir simultaneamente

## 📝 Nota

Se os valores solicitados pelo Certbot forem diferentes na próxima tentativa, use os novos valores. O Let's Encrypt pode gerar novos valores a cada tentativa.

