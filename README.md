# Classes para o consumo de APIs
O objetivo deste projeto é a implementação de classes para o consumo de APIs, sendo essas classes uma espécie de 
*wrappers* da biblioteca requests.

O projeto ainda está em andamento. A idéia é ir adicionando novas features e classes com o tempo à medida que novas 
necessidades forem aparecendo.

## Classes

- **API**: Classe que implementa as requisições utilizando a biblioteca
requests. ***Atualmente estão implementadas apenas requisições dos tipos: GET e POST***.
- **Pipedrive**: Classe responsável pelas interações com a API do CRM Pipedrive, 
[para mais informações acesse.](https://www.pipedrive.com/pt)
- **Proxycurl**: Classe responsável pela interação com a API do Proxycurl. Uma plataforma com dados de perfis e 
páginas do LinkedIn. [Para mais informações acesse.](https://nubela.co/proxycurl/)


### *Importante!*
A classe API foi criada com a intenção de servir como a classe "mãe" de todas as outras que serão implementadas. 
Por isso, toda a interação com a biblioteca requests deve estar nela. 
