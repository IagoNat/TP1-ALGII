# Relatório Final - Trabalho Prático 1: Geometria Computacional e Visualização

## 1. Introdução
Este tabalho tem como objetivo explorar aspectos práticos de algoritmos de geometria computacional, com ênfase na implementação e uso de árvores k-dimensionais (k-d trees) para consultas ortogonais em conjuntos de pontos geográficos. Para isso, desenvolvemos um sistema iterativo de visualização e filtragem de bares e restaurantes em Belo Horizonte, com base em dados reais da Prefeitura (PBH) e integração com dados adicionais do festival Comida di Buteco.

---

## 2. Etapas de Implementação

### 2.1. Coleta e filtragem dos dados

- A base original foi obtida do portal [dados.pbh.gov.br](https://dados.pbh.gov.br).
- Foi feita a filtragem por descrição do CNAE principal, mantendo apenas estabelecimentos com atividade relacionada a alimentação e bebidas.
- Endereços foram compostos a partir de colunas separadas do CSV (logradouro, número, bairro, etc).

### 2.2. Geocodificação

- Foi utilizada a biblioteca `geopy` com a API do OpenStreetMap para obter coordenadas geográficas dos estabelecimentos a partir dos endereços.
- Um mecanismo de cache local em JSON foi implementado para evitar requisições repetidas e reduzir tempo de processamento.
- Endereços com geocodificação duplicada e nulos foram identificados e removidos.

### 2.3. Estrutura de dados: k-d tree

- Implementamos uma árvore k-d bidimensional para indexação espacial dos pontos (latitude, longitude).
- Utilizamos busca ortogonal para seleção eficiente de pontos dentro de retângulos definidos interativamente no mapa.

### 2.4. Visualização interativa

- Utilizamos as bibliotecas `Dash`, `dash-leaflet` e `Plotly` para compor um sistema de visualização com:
  - Marcadores no mapa
  - Tabela de informações detalhadas
  - Ferramenta de seleção retangular
  - Filtro com reset e interação coordenada com a árvore k-d

### 2.5. Integração com o Comida di Buteco (Funcionalidade Extra)

- Dados dos bares participantes foram adicionados manualmente (nome, endereço, prato e descrição).
- Foram destacados com ícones e popups personalizados no mapa.

---

## 3. Decisões de Projeto

- **Linguagem**: Python
- **Bibliotecas principais**: `pandas`, `geopy`, `dash`, `dash-leaflet`
- **Estrutura modular**: projeto foi dividido em múltiplos arquivos Python no diretório `src/` para organização.
- **Geocodificação com cache**: melhora de performance e controle local.

---

## 4. Exemplo de Funcionamento

### 🗺️ Mapa com marcadores
![Demo](https://github.com/IagoNat/TP1-ALGII/blob/d4d416d4bf5556a104378ad1d466345f27c24423/assets/map_gif.gif)

### 🔍 Seleção retangular e Tabela


---

## 5. Instruções para execução local

```bash
git clone https://github.com/IagoNat/TP1-ALGII.git
cd TP1-ALGII
pip install -r requirements.txt
python main.py

