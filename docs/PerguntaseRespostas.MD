# API de recebimento e centralização dos dados de controle de carga
Sistema de registro das operações de entrada e saída de pessoas e veículos,
 movimentação de carga e armazenamento de mercadorias em recintos alfandegados, 
 áreas alfandegadas ou recintos autorizados a operar com mercadorias sob controle aduaneiro  
 
# *Perguntas e respostas*

## 1. Devo guardar os dados transmitidos?

A API de dados de controle de carga e áreas sob controle aduaneiro foi
modelada de forma a capturar os eventos que ocorrem fisicamente e precisam ser controlados
nas diversas etapas da logística/controle de cargas, veículos e pessoas. Assim, as informações
são as mínimas necessárias para este tipo de controle e procuram espelhar o que seria necessário
nos sistemas de controle diversos.

* O interveniente que envia eventos para esta API deve possuir estes dados em seus sistemas de
controle, o que é necessário para operar o seu negócio. 
* A prova de cumprimento da obrigação de transmitir o Evento se dá pelo recebimento 
de um recibo formado por um hash matemático das informações transmitidas
* O controle de Eventos é pelo próprio identificador de cada registro/evento do sistema interno.

Assim, o Recinto deve guardar os dados transmitidos pelo prazo mínimo de seis anos mais o corrente,
além de ser recomendado guardar também o número de recibo fornecido pelo Sistema em cada registro.
Isto não deve gerar custo adicional para o interveniente, visto que estas informações transmitidas 
são necessárias para seu próprio sistema de controle.

Em caso da correspondência das entidades no sistema do interveniente não ser exata com a informação 
transmitida, o interveniente, ao montar pacote de transmissão, deve enviar o identificador do
registro da entidade com maior coincidência de informação, e gravar o recibo também nesta mesma
entidade de seu sistema de controle.

## 2. Como será a autenticação?

Haverá função no portal para representante com Certificado digital gerar chaves pública e privada
 do interveniente para acesso ao Sistema. O representante então deve baixar a chave privada e utilizar para transmissão,
 criptografando o conteúdo. O Servidor irá usar a chave privada gerada para descriptografar no recebimento,
 garantindo assim sigilo, não repúdio e autenticidade.


## 3. Continuará existindo a Auditoria de Sistemas obrigatória e periódica?

Com a nova sistemática, a necessidade de auditoria de sistemas diminui, portanto as normas serão revisadas.
Será recomendada a diminuição da periodicidade e complexidade da auditoria de sistemas. Em contrapartida,
será necessário uma auditoria simplificada feita durante a própria avaliação de alfandegamento e a vigilância
da Receita Federal poderá, a qualquer momento, solicitar acesso aos Sistemas dos intervenientes para
cotejar os dados destes com os dados transmitidos.

### 4. Como ficam os sistemas atuais que possuem funções desenvolvidas especificamente para a Unidade Local (bloqueios, mensagerias e outras comunicações)?

As realidades locais devem ser avaliadas localmente. Sendo funcṍes possíveis de serem transferidas para a API,
recomenda-se a centralização. É necessário que a Unidade Local avalie o caso específico.

