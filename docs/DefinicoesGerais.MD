# API de recebimento e centralização dos dados de controle de carga
Sistema de registro das operações de entrada e saída de pessoas e veículos,
 movimentação de carga e armazenamento de mercadorias em recintos alfandegados, 
 áreas alfandegadas ou recintos autorizados a operar com mercadorias sob controle aduaneiro  
 
# *Definições gerais*

* A modelagem das Entidades/Eventos está definida em formato OpenAPI3, versão yaml
* A modelagem dos "endpoints" (funções da API) também está definida neste arquivo.
* Os endpoints transmitirão JSON conforme especificado no arquivo OpenAPI.
* Os endpoints retornarão JSON conforme especificado no arquivo OpenAPI.
* O IDEvento é um campo transmitido pelo interveniente, e DEVE ser o identificador sequencial
 da informação no Sistema de origem.
* Alguns "endpoints especiais" não definidos ou detalhados na API estarão definidos e detalhados
 aqui na seção "endpoints especiais". Nestes haverá funcionalidade para enviar e receber
 lista de eventos. As listas são arquivos JSON que poderão ser compactados no formato gzip.
* Em caso de contingência(indisponibilidade ou falha do sistema informatizado), 
a medida de contingência adotada pelo interveniente deve prover os mesmos dados 
que seriam coletados pelo fluxo normal do sistema e devem ser alimentados 
no Sistema assim que este seja restabelecido.
* Os Eventos devem ser armazenados pelo prazo mínimo de 6 anos no sistema original,
 juntamente de dados adicionais que tenham dado origem aos Eventos. 
 A cada recepção de Evento será fornecido um recibo digital que deve ser guardado 
 no registro correspondente do Sistema do Recinto.
* Sempre que o tipo for "Data/date-time" significa data UTC no formato ISO:

    UTC Data ISO 8601 - AAAA-MM-DDThh:mmZ Ex.  2019-04-17T09:52:01Z

* Os campos com número de documento (CPF, CNPJ, CNH, etc) devem conter somente números, 
sem máscaras ou caracteres especiais

* O Servidor que recebe os eventos DEVE adicionar as seguintes informações:
1) Data e hora da transmissão do evento
2) Identificação do código do recinto que transmitiu evento
3) IP do computador que transmitiu o evento
4) Hash do JSON completo do Evento, visando prevenir modificações. Deve haver uma função para conferir o Hash do Evento 
e este deve ser transmitido na resposta, bem como gravado em um log de sistema de registro de eventos recebidos

* Haverá função no portal para representante com Certificado digital gerar chaves pública e privada
 do interveniente para acesso ao Sistema. O representante então deve baixar a chave privada e utilizar para transmissão,
 criptografando o conteúdo ou parte do conteúdo do JSON do Evento transmitido. O Servidor irá usar a chave privada 
 gerada para descriptografar no recebimento, garantindo assim sigilo, não repúdio e autenticidade.

# Endpoints especiais

* TODO Evento deve estar acessível para consulta por usuários da Receita, 
em endpoint REST com nome do evento seguido da expressão 'eventos/list'.
 O Endpoint receberá com opção de filtragem por intervalo de datas de transmissão
  ou por IDEvento inicial,
  e opcionalmente também por Unidade ou Recinto. 
  Este perfil estará disponível para cadastramento no Senha Rede/E-FAU.

Formato do filtro:
 ```json
 {
"IDEvento" : 	integer,
# IDEvento a partir do qual pesquisar (maior que) OU

"recinto":	"string",
# Codigo do Recinto a pesquisar

"tipoevento":	"string"
# Nome da classe de Evento
"datainicial":	"string($date-time)",
# Data de ocorrência física do evento - final de pesquisa IANA UTC DateTime

"datafinal"	: "string($date-time)",
# Data de ocorrência física do evento - final de pesquisa IANA UTC DateTime
}
```


* TODO Evento pode ser enviado em lista para ser processada de uma só vez,
 através do endpoint 'set_eventos_novos', que receberá um arquivo JSON, opcionalmente
 comprimido no formato gzip. O Arquivo JSON terá o formato:
 ```json
  {<TipoEvento> : [<Lista de Eventos>]}
```
Sendo que em "Lista de Eventos" cada item/evento seguirá examente o mesmo formato de JSON definido no endpoint específico
de cada Evento no arquivo OpenAPI.
 
* Arquivos multimídia terão endpoint 'upload_file' para adição a Evento existente 
e 'get_file' para recuperação do arquivo. Neste caso a transmissão de dados segue o padrão
HTTP "multipartform/data"
