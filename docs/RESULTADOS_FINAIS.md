# Resultados finais — auditoria agregada da coleta encerrada

> Survey pré-registrado: “O paradoxo da produtividade no desenvolvimento de software com inteligência artificial”  
> PUC Minas, Medição e Experimentação em Engenharia de Software · 2026/2  
> Análise do **CSV oficial**, 60 respostas com carimbos entre **13 e 22/11/2026**.  
> **Não contém respostas individuais nem dados pessoais.**

## Auditoria e amostragem

| Indicador | Resultado |
|---|---:|
| Respostas recebidas | 60 |
| Respostas válidas | 50 |
| Excluídas por falha de atenção AT01 | 7 |
| Excluídas por perfil inelegível E01 | 3 |
| Taxa de aproveitamento | 83,3% |
| Margem de erro **nominal** de proporção (n=50, 95%, p=0,5) | ±13,9 p.p. |

A margem acima usa a fórmula fornecida no enunciado. Como a amostragem é por conveniência e bola de neve, **não é uma garantia de precisão populacional** e não estabelece um intervalo de confiança válido para todos os desenvolvedores. O estudo descreve percepções autorrelatadas e não estabelece causalidade.

## Consistência interna e indicadores

| Construto | Alfa de Cronbach | Regra pré-registrada efetivamente aplicada |
|---|---:|---|
| Produtividade (P01–P03) | 0,536 | Alfa <0,70 → item P03 |
| Retrabalho (R01–R03) | 0,676 | Alfa <0,70 → item R02 |
| Confiança (C01–C03) | 0,907 | Alfa ≥0,70 → média dos três itens |

Os alfas são determinados **uma vez na amostra válida de 50 pessoas**, antes de filtrar. Indicadores não mudam ao segmentar por perfil, experiência ou frequência de uso de IA.

## QP1 — Produtividade e retrabalho percebidos

- **Coexistência P≥4 e R≥4:** 31/50 = **62,0%**.
- **Spearman bicaudal:** ρ = **−0,162**; n=50; p bruto=**0,2604**; p Holm=**1,0000**.
- **Conclusão:** coexistência descritiva frequente na amostra; associação monotônica estimada negativa e muito fraca, **não significativa** (α=0,05). Não afirmar “produtividade causa retrabalho”, “retrabalho reduz produtividade” nem “não existe associação”.

A matriz de quadrantes da amostra completa contém 0 pessoas com P<4/R≥4; 31 com P≥4/R≥4; 1 com P<4/R<4; 18 com P≥4/R<4.

## QP2 — Esforço de compreensão, correção, adaptação e integração

- n completo-pareado=**49**. Resposta “Não se aplica” não vira esforço zero.
- Friedman χ²≈**3,811**; p=**0,2826**; Kendall W≈**0,026**.
- Medianas A01/A02/A03/A04: **3/3/3/3**.
- Esforço 4–5: compreensão **24,0%**; correção **30,0%**; adaptação **32,7%**; integração **24,0%**.
- **Conclusão:** ausência de evidência de diferenças sistemáticas globalmente significativas; por isso não há pós-hoc de Wilcoxon.

## QP3 — Confiança e frequência de verificação

A confiança utiliza a média C01–C03 (α≈0,907). Correlaciona-se separadamente com frequência de revisão da lógica, execução de testes e validação de requisitos.

| Comparação | Spearman ρ | p bruto | p Holm | Resultado |
|---|---:|---:|---:|---|
| Confiança × revisão da lógica | +0,067 | 0,6452 | 1,0000 | Não significativo |
| Confiança × execução de testes | +0,062 | 0,6669 | 1,0000 | Não significativo |
| Confiança × validação dos requisitos | −0,119 | 0,4120 | 1,0000 | Não significativo |

A correção de Holm foi aplicada à **família de quatro correlações** (uma QP1 + três QP3), conforme pré-registro.

## OA01 e evidências

A questão aberta é opcional: houve **4 respostas não vazias entre os 50 válidos**. Conforme declaração do grupo, **Islayder e Bárbara** classificaram os quatro relatos separadamente e informaram **classificações idênticas, sem divergências**. O consenso registrado é **T1=4, T2=0, T3=1, T4=0, T5=2, T6=0 e T7=2**; respostas podiam receber vários códigos. O resumo agregado está no PDF final e no CSV de consenso do ZIP de entrega. Os cadernos individuais não foram anexados; textos OA01 são mantidos restritos. Quatro relatos não permitem generalização.

A exportação bruta com timestamps, a captura do Forms encerrado em 22/11 e **quatro capturas datadas dos canais de divulgação** (13 e 15/11) foram incluídas no pacote restrito do Canvas; o GitHub mantém apenas documentação agregada. Dados individuais de OA01 continuam fora do repositório.

## Pontos para a defesa

- **Islayder:** visão geral e QP1; diferenciar coexistência de correlação/significância.
- **Bárbara:** QP2, esforço ordinal, Friedman, W e limpeza/confiabilidade.
- **Vinícius:** QP3, Holm, limitação da amostragem e conclusão.
- **Todos:** justificar a mudança de cenário com filtros e lembrar que a classificação dos construtos é fixada na amostra completa.

O protocolo pré-registrado permanece inalterado (originalmente cinco nomes). O grupo atual tem três integrantes, uma mudança administrativa documentada, que não modifica itens, regras de elegibilidade ou análise estatística.
