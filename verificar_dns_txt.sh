#!/bin/bash
# Script para verificar registros DNS TXT
# Execute: bash verificar_dns_txt.sh

echo "=========================================="
echo "  Verificar Registros DNS TXT"
echo "=========================================="
echo ""

# Valores esperados do Certbot
EXPECTED_MAIN="LuxBwM8MtAFwTgvLpYAIs_SD-B6NLY2IcyDPsizEdnQ"
EXPECTED_WWW="EhoG1jlvTwP9mItvXLDCvx_Y1xrTURS1iU5LO6BvvLY"

echo "Valores esperados pelo Certbot:"
echo "  _acme-challenge.nomadtradersystem.com = $EXPECTED_MAIN"
echo "  _acme-challenge.www.nomadtradersystem.com = $EXPECTED_WWW"
echo ""

# Verificar registro para domínio principal
echo "1. Verificando _acme-challenge.nomadtradersystem.com..."
MAIN_RESULT=$(dig TXT _acme-challenge.nomadtradersystem.com +short 2>/dev/null | tr -d '"' || echo "NÃO ENCONTRADO")
echo "   Encontrado: $MAIN_RESULT"

if echo "$MAIN_RESULT" | grep -q "$EXPECTED_MAIN"; then
    echo "   ✅ Valor correto!"
elif [ "$MAIN_RESULT" != "NÃO ENCONTRADO" ]; then
    echo "   ❌ Valor incorreto! Esperado: $EXPECTED_MAIN"
    echo "   ⚠️  Remova o registro antigo e adicione o valor correto no DNS"
else
    echo "   ❌ Registro não encontrado!"
    echo "   ⚠️  Crie o registro TXT no DNS"
fi
echo ""

# Verificar registro para www
echo "2. Verificando _acme-challenge.www.nomadtradersystem.com..."
WWW_RESULT=$(dig TXT _acme-challenge.www.nomadtradersystem.com +short 2>/dev/null | tr -d '"' || echo "NÃO ENCONTRADO")
echo "   Encontrado: $WWW_RESULT"

if echo "$WWW_RESULT" | grep -q "$EXPECTED_WWW"; then
    echo "   ✅ Valor correto!"
elif [ "$WWW_RESULT" != "NÃO ENCONTRADO" ]; then
    echo "   ❌ Valor incorreto! Esperado: $EXPECTED_WWW"
    echo "   ⚠️  Remova o registro antigo e adicione o valor correto no DNS"
else
    echo "   ❌ Registro não encontrado!"
    echo "   ⚠️  Crie o registro TXT no DNS"
fi
echo ""

# Resumo
echo "=========================================="
echo "  Resumo"
echo "=========================================="
echo ""

ALL_OK=true

if ! echo "$MAIN_RESULT" | grep -q "$EXPECTED_MAIN"; then
    ALL_OK=false
    echo "❌ _acme-challenge.nomadtradersystem.com precisa ser corrigido"
fi

if ! echo "$WWW_RESULT" | grep -q "$EXPECTED_WWW"; then
    ALL_OK=false
    echo "❌ _acme-challenge.www.nomadtradersystem.com precisa ser criado/corrigido"
fi

if [ "$ALL_OK" = true ]; then
    echo "✅ Todos os registros DNS estão corretos!"
    echo ""
    echo "Você pode continuar o Certbot pressionando Enter."
else
    echo ""
    echo "⚠️  Corrija os registros DNS primeiro!"
    echo ""
    echo "Após corrigir, aguarde alguns minutos e execute este script novamente"
    echo "para verificar propagação."
fi
echo ""

