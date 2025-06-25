Site Acadêmico Professor Raul Benites Paradeda
Uma plataforma web moderna e bilíngue (PT/EN) para o gerenciamento e apresentação do trabalho acadêmico e informações pessoais do Professor Raul Benites Paradeda. O site é focado em acessibilidade, dinamismo de conteúdo e responsividade em diversos dispositivos.
🌟 Funcionalidades
Páginas Públicas: Homepage, Áreas de Pesquisa, Projetos, Publicações, Orientações, Contato e Sobre Mim.
Conteúdo Dinâmico: Informações do professor, publicações, projetos e orientações são carregadas via APIs do backend.
Acessibilidade:
Modo de Alto Contraste: Alternância de tema para melhor legibilidade.
Ajuste de Fonte: Botões para aumentar, diminuir e resetar o tamanho da fonte do conteúdo principal.
Navegação por Teclado: Suporte a atalhos de teclado e navegação intuitiva.
Interface Bilíngue (PT/EN): Alternância de idioma com URLs localizadas e formatação de datas.
Filtros de Projetos: Filtragem dinâmica de projetos por tipo (Pesquisa, Extensão, Ensino) e status (Em Andamento, Concluído, Planejamento, Proposto).
Formulário de Contato: Envio de mensagens com feedback visual e notificação por e-mail configurável para o administrador.
Painel Administrativo:
Autenticação segura (login/logout).
CRUD (Criar, Ler, Atualizar, Excluir) para Professor, Publicações, Projetos, Orientações, Áreas de Pesquisa e Mensagens de Contato.
Dashboard com estatísticas básicas (contagem de itens).
💡 Arquitetura
O sistema segue uma arquitetura monolítica com frontend e backend servidos pela mesma aplicação Flask.
Frontend: Desenvolvido com HTML, CSS (com variáveis para tema e responsividade Flexbox/Grid) e JavaScript puro para dinamismo e acessibilidade.
Backend: Implementado em Flask (Python), servindo as páginas HTML e as APIs RESTful.
Persistência de Dados: Os dados acadêmicos e de contato são armazenados em um arquivo JSON (academic_data.json), facilitando a configuração e o deploy inicial.
APIs RESTful: Endpoints padronizados para todas as entidades, permitindo o consumo de dados pelo frontend e o gerenciamento via painel administrativo.
Segurança: Implementação de Content-Security-Policy (CSP) para mitigar ataques como XSS e controle de acesso para o painel administrativo.
🛠️ Tecnologias Utilizadas
Backend:
Python 3.9+
Flask
Flask-Babel (para internacionalização)
Werkzeug (para segurança e utilitários)
Gunicorn (servidor WSGI para produção)
smtplib (para envio de e-mails)
Frontend:
HTML5
CSS3 (com variáveis CSS e Media Queries para responsividade)
JavaScript (ES6+)
Font Awesome (para ícones)
Desenvolvimento/Outros:
Git / GitHub (controle de versão)
pip (gerenciamento de pacotes Python)
Render (plataforma de deploy)
🚀 Configuração e Instalação (Desenvolvimento Local)
Siga estes passos para configurar e rodar o projeto em seu ambiente local.
Clone o repositório:
git clone https://github.com/vsr777/site-raul-paradeda
cd site-raul-paradeda # Navegue até a pasta raiz do projeto


Crie e ative um ambiente virtual (altamente recomendado):
python -m venv venv
# No Windows:
.\venv\Scripts\activate
# No Linux/macOS:
source venv/bin/activate


Instale as dependências:
pip install -r requirements.txt


Configure as variáveis de ambiente:
Crie um arquivo chamado .env na raiz do seu projeto (na mesma pasta de flask_admin_enhanced.py). Este arquivo não deve ser adicionado ao controle de versão (.gitignore) por questões de segurança.
SECRET_KEY='sua_chave_secreta_aqui_e_bem_longa_e_aleatoria'
EMAIL_USERNAME='seu_email@gmail.com' # Email do remetente para notificações
EMAIL_PASSWORD='sua_senha_de_aplicativo_do_gmail' # Use uma senha de aplicativo para Gmail
ADMIN_RECEIVER_EMAIL='email_do_admin@exemplo.com' # Email que receberá as mensagens do formulário de contato

Para Gmail, você precisará gerar uma senha de aplicativo se a Verificação em Duas Etapas estiver ativada.
Gere e compile os dicionários de tradução (se for fazer alterações ou adicionar novas traduções):
flask babel extract -F babel.cfg -o translations/messages.pot --input-paths .
flask babel init -i translations/messages.pot -d translations -l en # Para inicializar inglês
flask babel update -i translations/messages.pot -d translations # Para atualizar existentes
flask babel compile -d translations

Certifique-se de ter um babel.cfg na raiz do projeto com o conteúdo correto para Flask-Babel. Este arquivo deve ser adicionado manualmente, se não estiver visível no seu repositório.
Inicie o servidor Flask:
flask run --port 3001

O site estará acessível em http://127.0.0.1:3001/ ou http://localhost:3001/.
🖥️ Uso
Site Público
Acesse http://localhost:3001/pt/ para a versão em português.
Acesse http://localhost:3001/en/ para a versão em inglês.
Utilize o alternador de idioma no cabeçalho para alternar entre PT/EN.
Use os botões A-, A, A+ para ajustar o tamanho da fonte e o ícone 🌑/☀️ para alternar o modo de alto contraste.
Navegue pelas páginas de Projetos e utilize os filtros de tipo e status.
Painel Administrativo
Acesse http://localhost:3001/admin/login para a página de login.
Credenciais Padrão (local): Usuário: admin, Senha: admin123 (se o academic_data.json não possuir usuários, ele será criado automaticamente).
Após o login, você poderá gerenciar o conteúdo do site.
☁️ Deploy (Render)
Este projeto está configurado para ser implantado na plataforma Render.com.
Crie uma conta no Render: https://render.com/
Conecte seu repositório Git: No painel do Render, crie um novo "Web Service" e conecte-o ao seu repositório GitHub/GitLab.
Configurações do Serviço Web:
Name: seu-site-professor (ou um nome de sua escolha)
Root Directory: . (se flask_admin_enhanced.py estiver na raiz do seu repositório)
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: gunicorn flask_admin_enhanced:app (certifique-se de que flask_admin_enhanced é o nome do seu arquivo Flask principal)
Environment Variables: Adicione as variáveis de ambiente que você configurou no .env local (SECRET_KEY, EMAIL_USERNAME, EMAIL_PASSWORD, ADMIN_RECEIVER_EMAIL).
Deploy: Clique em "Create Web Service". O Render fará o build e deploy.
Atenção: No plano gratuito do Render, o serviço "dormirá" após 15 minutos de inatividade. A primeira requisição após o "sono" pode ter um pequeno atraso.
📁 Estrutura do Projeto
A estrutura do projeto na raiz do repositório https://github.com/vsr777/site-raul-paradeda é a seguinte:
.
├── .gitattributes       # Atributos Git para configuração de arquivos
├── academic_data.json   # Base de dados em JSON
├── admin_template.py    # Template HTML para o painel administrativo
├── flask_admin_enhanced.py # Aplicação Flask principal (backend e rotas)
├── requirements.txt     # Dependências Python do projeto
├── README.md            # Este arquivo
├── static/              # Arquivos estáticos (CSS, JS, Imagens)
│   ├── css/             # Contém style.css, admin_style.css
│   ├── img/             # Imagens do site
│   └── js/              # Contém script.js, admin.js, contato.js, projetos.js
└── templates/           # Templates HTML das páginas públicas
    ├── areas_pesquisa.html
    ├── contato.html
    ├── index.html
    ├── orientacoes.html
    ├── projetos.html
    ├── publicacoes.html
    └── sobre_mim.html


Observação: Arquivos como .gitignore, Procfile e a pasta translations/ (com babel.cfg dentro ou na raiz) são essenciais para o gerenciamento de versionamento, deploy e internacionalização. Eles geralmente estão presentes em um projeto Flask completo, mesmo que não apareçam em todas as capturas de tela do repositório principal. Se não estiverem no seu repositório, recomenda-se adicioná-los.
🤝 Contribuindo
Se você deseja contribuir para este projeto, por favor, faça um fork do repositório e crie um pull request com suas alterações.
