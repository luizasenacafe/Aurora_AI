# Betelgeuse A.I. • Prévia 0.3

O nome e a identidade visual foram atualizados de Aurora A.I. para Betelgeuse A.I., em referência à supergigante vermelha Betelgeuse.

**Novo: servidor doméstico com HTTPS e chaves de acesso.** Veja [SERVIDOR.md](SERVIDOR.md) e abra **Central do servidor.cmd** para controlar o servidor. O fluxo HTTPS substitui o acesso direto pela rede descrito abaixo quando você usa a API Betelgeuse.

Uma aplicação de IA local e privada em Python para Windows 10/11. A Betelgeuse permite conectar modelos baixados no LM Studio e executá-los no seu computador ou servidor, sem exigir que seus prompts sejam enviados às grandes plataformas. O aplicativo não inclui modelos: você escolhe e baixa o modelo no LM Studio.

## Identidade espacial

Esta versão traz um fundo espacial nativo com estrelas, nebulosas, poeira e o brilho quente de Betelgeuse, além de movimento suave. A abertura apresenta uma esfera em tons de cobre e vermelho, com navegação astronômica, cartões de sugestões, balões de conversa com botão de copiar, configuração em seções e listas com progresso de conclusão. A interface foi conferida em janelas de 1240 × 860 e 980 × 720.

Em **Configurações → Seu ritmo**, é possível reduzir as animações. A opção é salva imediatamente. O movimento da ilustração para quando ela não está visível. Os dados e perfis existentes continuam sendo usados normalmente.

## Abrir

Neste computador, abra `Abrir Betelgeuse.cmd` para executar a versão de desenvolvimento com o Python e as dependências que já foram instalados. No primeiro uso, siga o tutorial de três passos: baixar/carregar um modelo no LM Studio, conectar o servidor em Configurações e testar a conexão. Depois crie um espaço de conversa para personalizar o comportamento da IA.

Também foi gerado `Aurora.exe`, que inclui Python e suas dependências. Porém, o Smart App Control deste Windows bloqueou uma versão durante a verificação por não ter assinatura reconhecida. O empacotamento foi ajustado, mas a execução da entrega final ainda precisa ser validada em um ambiente que permita aplicativos de desenvolvimento. As proteções do Windows não foram alteradas. O arquivo `.cmd` é a opção de desenvolvimento e exige Python/PySide6 instalados; ele não substitui um executável independente no PC do seu tio.

## Conectar neste computador

1. No LM Studio, baixe um modelo de conversa compatível com seu computador e carregue-o.
2. Na área Developer do LM Studio, inicie o servidor. Confirme a porta exibida; o exemplo abaixo usa 1234.
3. Na Betelgeuse, abra **Configurações** e use `http://localhost:1234/v1`.
4. Se o LM Studio exigir autenticação, preencha o token. Nesta prévia, o token permanece apenas na memória e deve ser informado novamente ao reabrir a Aurora.
5. Clique em **Testar conexão e buscar modelos**, escolha um modelo de conversa e clique em **Salvar configurações**.
6. Abra **Conversa** e envie uma mensagem.

O botão testa o acesso à lista de modelos. A primeira conversa verifica se o modelo escolhido consegue gerar uma resposta. A lista pode incluir modelos baixados que ainda não estão carregados e modelos de embeddings, que não servem para conversar.

## Testar no computador do seu tio, na mesma rede

1. No LM Studio do computador servidor, habilite **Serve on Local Network**. Ative **Require Authentication** e crie um token de acesso.
2. Caso o Windows solicite acesso à rede, permita a conexão na rede doméstica privada. Se houver bloqueio, configure uma regra de entrada restrita à rede privada e à porta do servidor; não desative o firewall.
3. Após validar a abertura do executável, envie `Aurora.exe` ao seu tio. Se o Windows dele também exigir assinatura, a distribuição do executável dependerá de resolver essa exigência. Para testes em ambiente de desenvolvimento, é possível usar o código-fonte com Python e as dependências instalados.
4. Na Aurora dele, em **Configurações**, informe o endereço do seu PC e o token do LM Studio.
5. O endereço identificado durante a criação foi `http://192.168.1.21:1234/v1`. Confirme-o no LM Studio: o roteador pode atribuir um IP diferente depois.
6. Busque os modelos, escolha o modelo de conversa e salve.

No PC dele, `localhost` aponta para o próprio computador dele. Use o IP do computador que está executando o modelo. Seu PC deve permanecer ligado, acordado e com o servidor disponível. Os dois precisam estar na mesma rede; redes de convidados podem bloquear a comunicação entre dispositivos.

## Personalidade e dados

- **Configurações → Personalidade geral**: instruções usadas para todos os perfis.
- **Editar meu perfil**: informações e preferências daquela pessoa.
- As mudanças passam a valer nas próximas mensagens. O histórico anterior continua salvo.
- Isso configura o contexto de atendimento; não treina nem altera os pesos do modelo.
- Perfis, histórico e itens ficam em `%LOCALAPPDATA%\AuroraAI\aurora.db` em cada computador.
- O perfil ativo e parte recente da conversa são enviados ao servidor escolhido. Não há sincronização de cadastros, listas ou históricos entre computadores.
- Os perfis são uma organização da casa, sem senha individual ou isolamento contra outros usuários do mesmo aplicativo.
- O contexto enviado é limitado para reduzir o uso de memória. A Aurora não tem memória ilimitada de conversas antigas.

## Compras e lembretes

Em **Organização**, escolha **Lista de compras** ou **Lembretes**, escreva o item e clique em **Adicionar à lista**. Para lembretes, escolha uma data e horário futuros. Marque a caixa quando concluir.

O chat pode ajudar a escrever listas e planejar lembretes. Nesta versão, você precisa cadastrá-los na aba Organização; mensagens no chat não criam ações automaticamente.

Lembretes são verificados a cada 15 segundos enquanto a Aurora está aberta. O aplicativo exibe um aviso e tenta enviar uma notificação do Windows. O Windows pode ocultar notificações conforme suas preferências. Fechar o aplicativo encerra a verificação. Ao reabrir, lembretes vencidos e não concluídos voltam a ser avisados. Não há serviço em segundo plano ou inicialização automática.

## Guardar o projeto

A pasta `source` contém o código-fonte. Faça uma cópia desta pasta e do banco de dados em outro local antes de formatar o PC. Para copiar o banco com segurança, feche a Aurora antes. O executável sozinho não contém seus cadastros.

Para desenvolvimento: instale Python 3.13 e as dependências de `source/requirements.txt`. Execute `python aurora.py` dentro da pasta source. Execute `python -m unittest -v test_aurora.py` para os testes.

Para gerar o executável dentro da pasta source:

```powershell
python -m PyInstaller --noconfirm Aurora.spec
```

## Verificação desta entrega

Foram testados: gravação e separação de histórico por perfil, edição das instruções, normalização do endereço, envio e recebimento com um servidor de teste, recuperação de mensagem após falha de conexão, cadastro de compras e lembretes e troca do endereço pela interface. A interface foi renderizada para revisão visual.

A abertura da versão Python foi testada no Windows e terminou sem erro. A validação do executável ficou limitada pelo bloqueio do Smart App Control. A resposta de um modelo real e a conexão a partir do PC do seu tio dependem do LM Studio estar configurado. Durante a preparação, não havia API disponível em `localhost:1234`.

Referências oficiais: [servidor na rede local](https://lmstudio.ai/docs/developer/core/server/serve-on-network), [conversas via API](https://lmstudio.ai/docs/developer/openai-compat/chat-completions), [lista de modelos](https://lmstudio.ai/docs/developer/openai-compat/models).
