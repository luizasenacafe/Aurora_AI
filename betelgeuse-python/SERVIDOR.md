# Betelgeuse A.I. • Seu PC como servidor

## O que está pronto

A API, a fila de geração, a gestão de chaves, a supervisão dos processos e a central de controle foram escritas em Python. O LM Studio já fornece a API do modelo; o servidor Betelgeuse fica entre ela e os aplicativos das pessoas.

Fluxo: **Aurora da pessoa → HTTPS da Cloudflare → API Aurora no seu PC → LM Studio → resposta de volta à pessoa**.

O componente oficial `cloudflared` fornece o túnel HTTPS. Ele não é Python; é a infraestrutura de rede usada pela aplicação Python. O modelo continua rodando no seu computador. As mensagens transitam pela Cloudflare para chegar ao servidor.

## Usar agora

1. Abra **Central do servidor.cmd** nesta pasta.
2. O servidor foi deixado ligado durante a configuração. Se estiver parado, clique em **Ligar API + HTTPS**.
3. Copie o endereço que aparece na central. Use o endereço atual: ele pode mudar após um reinício.
4. Clique em **Criar acesso**, dê um nome à pessoa e copie a chave exibida. Ela aparece uma única vez. Se a perder, revogue o acesso e crie outro.
5. No aplicativo Aurora da pessoa, abra **Configurações**, cole o endereço no campo de servidor e a chave no campo de token.
6. Clique em **Testar conexão e buscar modelos**, escolha o modelo de conversa e salve.

Pessoas dentro e fora de casa podem usar o mesmo endereço HTTPS. Não precisam instalar VPN nem LM Studio. Cada pessoa precisa de uma chave; o endereço sozinho não autoriza conversas. Nesta versão do cliente, o token só permanece enquanto o aplicativo está aberto.

A criação de chaves e o controle do servidor são locais: a API pública não tem painel administrativo. Na lista da central, **Revogar selecionado** bloqueia a chave nas próximas solicitações. Use uma chave por pessoa ou computador; duas instâncias com a mesma chave compartilham o limite de uma resposta em andamento.

## LM Studio

O servidor espera o LM Studio em `http://127.0.0.1:1234/v1`. Mantenha **Serve on Local Network** desativado: o túnel chega à API Aurora, e somente ela conversa com o LM Studio local. Não é necessário abrir portas no roteador ou desligar o firewall.

Na verificação desta entrega, o LM Studio respondeu, mas só expôs `text-embedding-nomic-embed-text-v1.5`. Esse modelo transforma textos em representações numéricas e não serve para o chat. A API Aurora o filtra da lista. Quando o download do modelo de conversa terminar, carregue-o e atualize a lista na Aurora.

Se a autenticação do LM Studio estiver ativada, configure a variável de ambiente `AURORA_LM_TOKEN` no processo do servidor e reinicie-o. Essa chave do LM Studio é diferente das chaves entregues aos clientes.

## Funcionamento contínuo

- A inicialização automática foi ativada **ao entrar na sua conta do Windows**. Ela pode ser desligada na central.
- Não é um serviço que começa antes do login. Depois de reiniciar o PC, entre no Windows para iniciar a API e o túnel.
- O supervisor reinicia a API e o túnel se esses processos encerrarem. Ele verifica o LM Studio a cada minuto e tenta iniciar a API pelo `lms.exe` instalado se ela estiver indisponível. Isso não baixa nem escolhe um modelo.
- Enquanto o supervisor estiver ativo, ele solicita que o Windows mantenha o PC acordado. A tela ainda pode apagar. Essa solicitação é liberada ao parar o servidor; o plano de energia permanente não foi alterado.
- Fechar a central não encerra o servidor. Use **Parar servidor** para desligá-lo.
- Desligamento, suspensão manual, falha do próprio supervisor, reinicialização do Windows, falta de luz ou queda de internet podem interromper o acesso.
- **Não há garantia de 24 horas ininterruptas nesta configuração de testes.** O endereço temporário do TryCloudflare pode mudar e não tem garantia de disponibilidade. Para uso estável, migre depois para um túnel nomeado com domínio fixo e valide a recuperação após reinícios.

## Limites da primeira versão

Há uma geração por vez para preservar os recursos do PC, até oito solicitações pendentes no total e uma solicitação pendente por chave. Solicitações adicionais recebem uma mensagem para tentar novamente. O limite de submissões/consultas de modelos é de 30 por minuto por chave.

O cliente atualizado envia a conversa e consulta o resultado em intervalos de dois segundos. Isso evita depender de uma única conexão HTTPS longa. A resposta aparece quando estiver completa; ainda não há transmissão palavra por palavra. O prazo inclui o tempo na fila, portanto uma fila demorada pode expirar.

As respostas ficam temporariamente na memória da API, associadas à chave que as solicitou. Outra chave não pode recuperá-las. Respostas terminadas expiram após cerca de dez minutos, com uma verificação a cada 30 segundos; há também limite de quantidade. Reiniciar o servidor perde respostas em andamento e os limites de frequência em memória.

Perfis e históricos continuam nos computadores clientes. A API encaminha as instruções e o histórico enviado naquela solicitação, sem treinar novamente o modelo. Ela não registra prompts, respostas ou tokens nos logs; o próprio LM Studio e a infraestrutura de túnel têm seus próprios comportamentos de registro.

## Arquivos e manutenção

- `server/`: código Python da API, central e supervisor.
- `server/requirements.txt`: dependências do servidor.
- `%LOCALAPPDATA%\AuroraServer\`: configurações, verificadores das chaves, logs e componente do túnel.
- `config.json`: endereço do LM Studio, porta local, limite da fila e modelo permitido. O campo `model` vazio permite os modelos de conversa visíveis no LM Studio. Para restringir a um único modelo, preencha seu identificador e reinicie o servidor.
- O backup do projeto não inclui as chaves nem os dados privados em AppData.

Para desativar a instalação automática: desmarque a opção na central e clique em **Parar servidor**. A opção remove apenas o atalho de inicialização da Aurora Server.

## Verificação

Passaram os seis testes da API, os quatro testes existentes do cliente e um teste integrado do cliente com a fila da API e um modelo simulado. Foram verificados autenticação, revogação, separação de respostas por chave, limite de fila, validação de dados, indisponibilidade do LM Studio e compatibilidade com a API de conversas.

O endereço HTTPS real respondeu ao teste de saúde, negou consultas sem chave e completou uma geração real com `prism-ml/bonsai-27b`: “Betelgeuse conectada.”. O modelo usa bastante tempo de raciocínio no Ryzen 5; respostas curtas podem levar mais de um minuto. O uso a partir de outro PC ainda depende da configuração do token no cliente.

Referências: [API do LM Studio](https://lmstudio.ai/docs/developer/core/server), [limites do túnel temporário](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/do-more-with-tunnels/trycloudflare/).
