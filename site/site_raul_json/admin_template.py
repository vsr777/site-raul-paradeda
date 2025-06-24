def get_admin_template():
    return '''
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Painel Administrativo</title>
        <link rel="stylesheet" href="{{ url_for('static', filename='admin_style.css') }}">
        <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
        <script src="{{ url_for('static', filename='admin.js') }}"></script>
    </head>
    <body x-data="adminApp()" x-init="init()">
        <div x-show="!isAuthenticated" class="login-container">
            <h1>Login Administrativo</h1>
            <div x-show="error" class="message error" x-text="error"></div>
            <form @submit.prevent="login()">
                <label>Usuário: <input type="text" x-model="loginForm.username" required></label>
                <label>Senha: <input type="password" x-model="loginForm.password" required></label>
                <button type="submit" :disabled="loading">
                    <span x-show="!loading">Entrar</span>
                    <span x-show="loading">Carregando...</span>
                </button>
            </form>
        </div>

        <div x-show="isAuthenticated">
            <h1>Painel Administrativo</h1>
            <nav>
                <a href="#" @click="activeTab = 'dashboard'">Dashboard</a>
                <a href="#" @click="activeTab = 'professor'">Professor</a>
                <a href="#" @click="activeTab = 'publicacoes'">Publicações</a>
                <a href="#" @click="activeTab = 'projetos'">Projetos</a>
                <a href="#" @click="activeTab = 'orientacoes'">Orientações</a>
                <a href="#" @click="activeTab = 'mensagens'">Mensagens</a>
                <button @click="logout()">Sair</button>
            </nav>

            <div x-show="message" :class="['message', messageType]" x-text="message"></div>

            <div x-show="activeTab === 'dashboard'">
                <h2>Dashboard</h2>
                <p>Bem-vindo(a), <span x-text="user && user.email ? user.email : ''"></span>!</p>
                <div id="professor-info">
                    <h3>Informações do Professor</h3>
                    <p>Nome: <span x-text="professorData.nome"></span></p>
                    <p>Email: <span x-text="professorData.email"></span></p>
                </div>
                <div class="stats">
                    <p>Total de Publicações: <span x-text="stats.total_publicacoes"></span></p>
                    <p>Total de Projetos: <span x-text="stats.total_projetos"></span></p>
                    <p>Total de Orientações: <span x-text="stats.total_orientacoes"></span></p>
                    <p>Mensagens Não Lidas: <span x-text="stats.mensagens_nao_lidas"></span></p>
                </div>
            </div>

            <div x-show="activeTab === 'professor'">
                <h2>Editar Informações do Professor</h2>
                <form @submit.prevent="saveProfessorData()">
                    <label>Nome: <input type="text" x-model="professorData.nome" required></label>
                    <label>Email: <input type="email" x-model="professorData.email" required></label>
                    <label>Titulação: <input type="text" x-model="professorData.titulacao"></label>
                    <label>URL Lattes: <input type="url" x-model="professorData.lattes_url"></label>
                    <label>URL da Foto: <input type="text" x-model="professorData.foto_path"></label>
                    <label>ORCID: <input type="text" x-model="professorData.orcid"></label>
                    <label>Bio (Português): <textarea x-model="professorData.bio_pt"></textarea></label>
                    <label>Bio (Inglês): <textarea x-model="professorData.bio_en"></textarea></label>
                    <button type="submit">Salvar Informações do Professor</button>
                </form>
            </div>

            <div x-show="activeTab === 'publicacoes'">
                <h2>Publicações</h2>
                <button @click="openModal('publicacao')">Adicionar Publicação</button>
                <table border="1">
                    <thead><tr><th>Título</th><th>Revista</th><th>Data</th><th>Ações</th></tr></thead>
                    <tbody>
                        <template x-for="pub in publicacoes" :key="pub.id">
                            <tr>
                                <td x-text="pub.titulo_pt"></td>
                                <td x-text="pub.revista"></td>
                                <td x-text="formatDate(pub.data_publicacao)"></td>
                                <td>
                                    <button @click="openModal('publicacao', pub)">Editar</button>
                                    <button class="delete-btn" @click="deleteItem('publicacoes', pub.id)">Excluir</button>
                                </td>
                            </tr>
                        </template>
                        <tr x-show="publicacoes.length === 0"><td colspan="4">Nenhuma publicação encontrada.</td></tr>
                    </tbody>
                </table>
            </div>

            <div x-show="activeTab === 'projetos'">
                <h2>Projetos</h2>
                <button @click="openModal('projeto')">Adicionar Projeto</button>
                <table border="1">
                    <thead><tr><th>Título</th><th>Tipo</th><th>Status</th><th>Ações</th></tr></thead>
                    <tbody>
                        <template x-for="proj in projetos" :key="proj.id">
                            <tr>
                                <td x-text="proj.titulo_pt"></td>
                                <td x-text="proj.tipo"></td>
                                <td x-text="proj.status"></td>
                                <td>
                                    <button @click="openModal('projeto', proj)">Editar</button>
                                    <button class="delete-btn" @click="deleteItem('projetos', proj.id)">Excluir</button>
                                </td>
                            </tr>
                        </template>
                        <tr x-show="projetos.length === 0"><td colspan="4">Nenhum projeto encontrado.</td></tr>
                    </tbody>
                </table>
            </div>

            <div x-show="activeTab === 'orientacoes'">
                <h2>Orientações</h2>
                <button @click="openModal('orientacao')">Adicionar Orientação</button>
                <table border="1">
                    <thead><tr><th>Aluno</th><th>Nível</th><th>Status</th><th>Ações</th></tr></thead>
                    <tbody>
                        <template x-for="ori in orientacoes" :key="ori.id">
                            <tr>
                                <td x-text="ori.aluno_nome"></td>
                                <td x-text="ori.nivel"></td>
                                <td x-text="ori.status"></td>
                                <td>
                                    <button @click="openModal('orientacao', ori)">Editar</button>
                                    <button class="delete-btn" @click="deleteItem('orientacoes', ori.id)">Excluir</button>
                                </td>
                            </tr>
                        </template>
                        <tr x-show="orientacoes.length === 0"><td colspan="4">Nenhuma orientação encontrada.</td></tr>
                    </tbody>
                </table>
            </div>

            <div x-show="activeTab === 'mensagens'">
                <h2>Mensagens</h2>
                <table border="1">
                    <thead><tr><th>Nome</th><th>Email</th><th>Mensagem</th><th>Ações</th></tr></thead>
                    <tbody>
                        <template x-for="msg in contatos" :key="msg.id">
                            <tr :class="{ 'unread': !msg.lido }">
                                <td x-text="msg.nome"></td>
                                <td x-text="msg.email"></td>
                                <td>
                                    <span x-text="msg.mensagem.substring(0, 50) + (msg.mensagem.length > 50 ? '...' : '')"></span>
                                    <button x-show="msg.mensagem.length > 50" @click="viewMessage(msg)">Ver Mais</button> </td>
                                <td>
                                    <button class="read-btn" @click="markAsRead(msg.id, msg.lido)" x-text="msg.lido ? 'Marcar como Não Lida' : 'Marcar como Lida'"></button>
                                    <button class="delete-btn" @click="deleteItem('contatos', msg.id)">Excluir</button>
                                </td>
                            </tr>
                        </template>
                        <tr x-show="contatos.length === 0"><td colspan="5">Nenhuma mensagem encontrada.</td></tr>
                    </tbody>
                </table>
            </div>

       <div x-show="showModal" class="modal">
                <div class="modal-content">
                    <span class="close-button" @click="closeModal()">&times;</span>
                    <h2 x-text="modalTitle"></h2>
                    <form @submit.prevent="saveItem()">
                        <template x-if="modalType === 'publicacao'">
                            <div>
                                <label>Título (PT): <input type="text" x-model="newItem.publicacao.titulo_pt" required></label>
                                <label>Revista: <input type="text" x-model="newItem.publicacao.revista" required></label>
                                <label>Resumo (PT): <textarea x-model="newItem.publicacao.resumo_pt"></textarea></label>
                                <label>Título (EN): <input type="text" x-model="newItem.publicacao.titulo_en"></label>
                                <label>Abstract (EN): <textarea x-model="newItem.publicacao.abstract_en"></textarea></label>
                                <label>Data de Publicação (AAAA-MM-DD): <input type="date" x-model="newItem.publicacao.data_publicacao"></label>
                                <label>DOI: <input type="text" x-model="newItem.publicacao.doi"></label>
                                <label>URL Lattes: <input type="text" x-model="newItem.publicacao.lattes_url"></label>
                                <label>Destacado: <input type="checkbox" x-model="newItem.publicacao.is_featured"></label>
                            </div>
                        </template>

                        <template x-if="modalType === 'projeto'">
                            <div>
                                <label>Título (PT): <input type="text" x-model="newItem.projeto.titulo_pt" required></label>
                                <label>Tipo: <input type="text" x-model="newItem.projeto.tipo" required></label>
                                <label>Status: <input type="text" x-model="newItem.projeto.status" required></label>
                                <label>Descrição (PT): <textarea x-model="newItem.projeto.descricao_pt"></textarea></label>
                                <label>Título (EN): <input type="text" x-model="newItem.projeto.titulo_en"></label>
                                <label>Descrição (EN): <textarea x-model="newItem.projeto.descricao_en"></textarea></label>
                                <label>Data de Início (AAAA-MM-DD): <input type="date" x-model="newItem.projeto.data_inicio"></label>
                                <label>Data de Término (AAAA-MM-DD): <input type="date" x-model="newItem.projeto.data_termino"></label>
                            </div>
                        </template>

                        <template x-if="modalType === 'orientacao'">
                            <div>
                                <label>Nome do Aluno: <input type="text" x-model="newItem.orientacao.aluno_nome" required></label>
                                <label>Nível: <input type="text" x-model="newItem.orientacao.nivel" required></label>
                                <label>Status: <input type="text" x-model="newItem.orientacao.status" required></label>
                                <label>Título da Tese (PT): <textarea x-model="newItem.orientacao.titulo_tese_pt"></textarea></label>
                                <label>Título da Tese (EN): <textarea x-model="newItem.orientacao.titulo_tese_en"></textarea></label>
                                <label>Data de Início (AAAA-MM-DD): <input type="date" x-model="newItem.orientacao.data_inicio"></label>
                                <label>Data de Defesa (AAAA-MM-DD): <input type="date" x-model="newItem.orientacao.data_defesa"></label>
                            </div>
                        </template>
                        <button type="submit">Salvar</button>
                    </form>
                </div>
            </div>
            <div x-show="showMessageModal" class="modal">
                <div class="modal-content">
                    <span class="close-button" @click="closeMessageModal()">&times;</span>
                    <h2>Mensagem Completa</h2>
                    <p><b>De:</b> <span x-text="currentMessage.nome"></span> (<span x-text="currentMessage.email"></span>)</p>
                    <p><b>Assunto:</b> <span x-text="currentMessage.assunto"></span></p>
                    <p><b>Data:</b> <span x-text="formatDateTime(currentMessage.data_envio)"></span></p>
                    <hr>
                    <p x-text="currentMessage.mensagem"></p>
                </div>
            </div>

        </div>
    </body>
    </html>
    '''