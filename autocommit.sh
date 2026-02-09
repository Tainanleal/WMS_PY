#!/bin/bash
# Script para automaticamente adicionar, commitar e dar push de alterações.

echo "Salvando progresso automaticamente..."

# Adiciona todos os arquivos ao stage
git add .

# Faz o commit com uma mensagem padrão.
# O timestamp é adicionado para tornar cada commit único.
git commit -m "feat: autocommit em $(date)"

# Envia as alterações para o repositório remoto
git push

echo "Progresso salvo com sucesso!"
