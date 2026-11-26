# Parte 2 — Entrega, evidências e defesa (checklist)

> PUC Minas · Medição e Experimentação em Engenharia de Software · 2026/2  
> Estudo: paradoxo da produtividade com IA · Equipe atual: Islayder, Bárbara e Vinícius

## O que a aplicação demonstra

- [x] Importa XLSX/CSV brutos do formulário, com data/hora; não usa screenshots estáticas como dados.
- [x] Audita elegibilidade: 60 recebidas, 50 válidas, 10 descartadas (7 AT01, 3 E01).
- [x] Mostra perfil e experiência, distribuições Likert divergentes e filtros E01, E04 e E05.
- [x] Mostra QP1: coexistência 31/50 (62%), matriz de quadrantes e heatmap, Spearman ρ = −0,162, p bruto ≈ 0,2604 e p Holm = 1,0000, com n e resultado da inferência.
- [x] Mostra QP2: comparações ordinais, Friedman, Kendall W e pós-hoc apenas se significativo.
- [x] Mostra QP3: três Spearman, n, p bruto/p Holm, efeitos e significância.
- [x] Mostra alfa de Cronbach na **amostra integral** e mantém indicadores P/R/C constantes ao filtrar.
- [x] Mostra margem de erro **nominal** para proporções (±13,9 p.p. quando n=50), sem afirmar representatividade.
- [x] Documenta planejamento versus execução, critérios, limitações e pendências na página de metodologia.

## Evidências reais — completar antes de entregar

- [x] **Planilha bruta de respostas** com timestamp, guardada em ambiente privado da equipe. Arquivo de referência: exportação oficial de 22/11/2026; não versionar no GitHub.
- [x] **Captura do painel Google Forms encerrado**, feita em 22/11, mostrando 60 respostas e 'não está aceitando respostas'.
- [ ] **Capturas datadas de convites/publicações** dos canais usados (por exemplo, WhatsApp, LinkedIn ou comunidade de TI). Excluir/ocultar números telefônicos, nomes e fotos de terceiros.
- [ ] **Comprovação da entrega do pré-registro antes da primeira resposta oficial** (registro de envio no Canvas ou commit datado e verificável).
- [ ] **Codificação independente da OA01 por dois integrantes**, mais tabela de consenso. Manual: [CODIFICACAO_OA01.md](CODIFICACAO_OA01.md).
- [ ] **Confirmar se o Canvas pede arquivo, link ou ambos** e enviar no prazo exibido na tarefa, não apenas no cronograma.
- [ ] **Preparar um computador/ambiente confiável com a exportação autorizada** para a demonstração.
- [ ] **Confirmar com a docência, se necessário, a alteração de cinco nomes pré-registrados para três integrantes atuais.**

Não declarar itens pendentes como realizados. Os registros de recrutamento e codificações individuais não devem ser publicados em repositório aberto.

## Demonstração em 10 minutos

1. Abrir a aplicação e **importar a exportação oficial pela barra lateral** (o painel público não traz as respostas brutas).
2. Verificar o resumo: 60 recebidas, 50 válidas, 10 excluídas; filtros em **Todos**.
3. Islayder: visão geral e QP1, mencionando o contraste entre coexistência elevada e Spearman não significativo.
4. Bárbara: QP2, Friedman, Kendall W, cuidados com respostas 'Não se aplica' e qualidade dos dados.
5. Vinícius: QP3, interpretação dos três efeitos, correção de Holm, margem nominal e limitações.
6. Na arguição, demonstrar cenário alternativo com filtro, observando que o indicador escolhido **não muda** e que o n efetivo diminui; os testes de subgrupo são exploratórios.
7. Abrir **Método e qualidade**: auditoria, alfa de Cronbach, execução versus protocolo e registro dos documentos da equipe.

**Não confundir:** os 62% são uma **proporção descritiva da amostra**, e ρ = −0,162 com p ajustado = 1,0000 **não** demonstra associação monotônica estatisticamente significativa. Não há evidência causal.

## Proteção de dados

A exportação integral pode conter informações inseridas voluntariamente em OA01. Restringir acesso aos integrantes autorizados, evitar compartilhamento público e apagar ou anonimizar identificadores em screenshots. O GitHub recebe apenas código, documentação genérica e testes com dados fictícios. O arquivo carregado no Streamlit é processado pelo servidor de hospedagem; decidir com o grupo se o ambiente atende ao compromisso de armazenamento restrito do TCLE antes de enviar a exportação real. Para maior controle, executar localmente com `streamlit run app.py`.
