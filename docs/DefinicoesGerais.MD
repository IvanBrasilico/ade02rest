# API de recebimento e centralização dos dados de controle de carga
Sistema de registro das operações de entrada e saída de pessoas e veículos,
 movimentação de carga e armazenamento de mercadorias em recintos alfandegados, 
 áreas alfandegadas ou recintos autorizados a operar com mercadorias sob controle aduaneiro  
 
# *Definições gerais*

* A modelagem das Entidades/Eventos está definida em formato OpenAPI3, versão yaml
* A modelagem dos "endpoints" (funções da API) também está definida neste arquivo.
* Os endpoints transmitirão JSON conforme especificado no arquivo OpenAPI.
* Os endpoints retornarão JSON conforme especificado no arquivo OpenAPI.
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
