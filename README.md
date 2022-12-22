# Consulta car

## Setup


 1. Crie e entre no ambiente virtual

		python -m venv ENV
	
	Para acessar:
	* No Windows:
	 
			ENV/Scripts/activate
	
	* No Linux:
		
			source ./ENV/bin/activate
	

2. Instale as dependências

		pip install -r requirements.txt

  
3. Configure o config.json

	O `config.json` mudará de acordo com o ambiente em que a API está rodando.
```json
{
    "DEV": 1, //mudar para 0 em ambiente de produção
    "LETRA_DISCO_LOCAL_E": "letra referente ao E:/ na máquina (maiusculo)",
    "SERVIDOR": "servidor_onde_a_api_esta (maiusculo)",
    "CONEXOES_MONGO_API": {
        "SERVIDOR": "mongodb://username:senha@host:porta/database"
    },
    "CONEXOES_MONGO_SOFTURBANO": {
        "SERVIDOR": "mongodb://username:senha@host:porta/database"
    },
    "CONEXOES_SQL": {
        "SERVIDOR": "Driver={ODBC Driver 17 for SQL Server};Server=myServerAddress;Database=myDataBase;Uid=myUsername;Pwd=myPassword;"
    }
}
```
	
## Rodar a aplicação
	
	flask run


## Setup do IIS

Levando em consideração que a máquina está com a aplicação configurada e o web site já está criado no IIS.
    
1. Habilite o FastCGI no IIS (se já estiver habilitado, pode ignorar esta etapa)
    1. Pesquise por Server Manager
    2. Add Role and Features
    3. Vá em Server Roles
    4. Web Server (IIS)/Web Server/Application Development/CGI
    5. Conclua a instalação
2. Instale o `wfastcgi` na máquina (não no env). Obs: Guarde o caminho que foi printado no final da instalação.
    
    >pip install wfastcgi
    
    E habilite o `wfastcgi`
    
    >wfastcgi-enable
    
3. Cria o `web.config` e o coloque na pasta raiz do projeto
```xml
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <handlers>
      <add name="PythonHandler"
         path="*"
         verb="*"
         modules="FastCgiModule"
         scriptProcessor={caminho que é printado ao instalar o wfastcgi na máquina}
         resourceType="Unspecified"
         requireAccess="Script" />
    </handlers>
  </system.webServer>
  <!-- <system.web>
  <httpRuntime executionTimeout="14400" />
</system.web> -->
  <appSettings>
    <!-- Required settings -->
    <add key="WSGI_HANDLER" value="app.app" />
    <add key="PYTHONPATH" value={o que é printado ao rodar print(sys.path)} />
  </appSettings>
</configuration>
```

Obs.: O valor de `PYTHONPATH` tem que ser printado dentro do ambiente virtual. Ignore qualquer string vazia (''), copie todos os valores, substitua as vírgulas por ; e exclua todos os espaços e aspas simples.


### Para desabilitar o timeout da requisição

1. Vá em FastCGI Settings
2. Caminho da pasta Python39
3. Na parte superior direita, clique em Edit
4. Coloque 3600 em Idle Timeout, Activity Timeout e Request Timeout. 
 