João Vitor Nascimento da Luz. RA:1134020

Na refatopração do código fornecido para melhoria, utilizei wraps para proteger rotas com autenticação, bcrypt para armazenar senhas de forma segura, jwt para autenticação segura. Também foi criada uma tabela users para gerenciar usuários.
E para a implementação de autenticação foi adicionada rota de registro (/register) para criação de usuários, adicionada rota de login (/login), que gera um token JWT válido por 1 hora e proteção da rota /data para que apenas usuários autenticados possam acessá-la.
