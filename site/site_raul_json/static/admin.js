document.addEventListener('alpine:init', () => {
    Alpine.data('adminApp', () => ({
        isAuthenticated: false,
        user: null,
        loading: false,
        error: null,
        message: null,
        messageType: 'success',
        activeTab: 'dashboard',
        professorData: {},
        publicacoes: [],
        projetos: [],
        orientacoes: [],
        contatos: [],
        stats: {},
        showModal: false,
        modalTitle: '',
        modalType: '',
        newItem: {
            publicacao: { titulo_pt: '', revista: '', resumo_pt: '', titulo_en: '', abstract_en: '', data_publicacao: '', doi: '', lattes_url: '', is_featured: false },
            projeto: { titulo_pt: '', tipo: '', status: '', descricao_pt: '', titulo_en: '', descricao_en: '', data_inicio: '', data_termino: '' },
            orientacao: { aluno_nome: '', nivel: '', status: '', titulo_tese_pt: '', titulo_tese_en: '', data_inicio: '', data_defesa: '' }
        },
        currentEditItem: null,
        showMessageModal: false,
        currentMessage: {},
        loginForm: { username: '', password: '' },

        init() {
            this.checkAuthentication();
        },

        async checkAuthentication() {
            try {
                const res = await fetch('/api/admin/check-auth');
                const data = await res.json();
                if (data.authenticated) {
                    this.isAuthenticated = true;
                    this.user = { email: data.user };
                    await this.loadAllData();
                } else {
                    this.isAuthenticated = false;
                    this.user = null;
                }
            } catch (err) {
                console.error('Erro ao verificar autenticação:', err);
                this.error = 'Não foi possível verificar o status de login.';
                this.isAuthenticated = false;
                this.user = null;
            }
        },

        async login() {
            this.loading = true;
            this.error = null;
            try {
                const res = await fetch('/api/admin/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username: this.loginForm.username, password: this.loginForm.password })
                });
                const data = await res.json();
                if (data.success) {
                    this.isAuthenticated = true;
                    this.user = { email: data.user.email };
                    await this.loadAllData();
                } else {
                    this.error = data.error;
                    this.isAuthenticated = false;
                    this.user = null;
                }
            } catch (err) {
                this.error = 'Erro ao conectar ao servidor para login.';
                console.error('Login error:', err);
                this.isAuthenticated = false;
                this.user = null;
            } finally {
                this.loading = false;
            }
        },

        async logout() {
            try {
                await fetch('/api/admin/logout', { method: 'POST' });
                this.isAuthenticated = false;
                this.user = null;
                this.loginForm = { username: '', password: '' };
                this.showMessage('Você foi desconectado.', 'success');
            } catch (err) {
                console.error('Logout error:', err);
                this.showMessage('Erro ao fazer logout.', 'error');
            }
        },

        async loadAllData() {
            try {
                this.loading = true;
                const [professor, publicacoes, projetos, orientacoes, contatos] = await Promise.all([
                    fetch('/api/admin/professor').then(res => res.json()),
                    fetch('/api/admin/publicacoes').then(res => res.json()),
                    fetch('/api/admin/projetos').then(res => res.json()),
                    fetch('/api/admin/orientacoes').then(res => res.json()),
                    fetch('/api/admin/contatos').then(res => res.json())
                ]);
                this.professorData = professor;
                this.publicacoes = publicacoes;
                this.projetos = projetos;
                this.orientacoes = orientacoes;
                this.contatos = contatos;
                this.updateStats();

            } catch (err) {
                console.error('Erro ao carregar dados:', err);
                this.showMessage('Erro ao carregar dados do painel.', 'error');
            } finally {
                this.loading = false;
            }
        },

        updateStats() {
            this.stats = {
                total_publicacoes: this.publicacoes.length,
                total_projetos: this.projetos.length,
                total_orientacoes: this.orientacoes.length,
                mensagens_nao_lidas: this.contatos.filter(c => !c.lido).length
            };
        },

        async saveProfessorData() {
            this.loading = true;
            try {
                if (!this.professorData.id) {
                    this.showMessage('Erro: ID do professor não encontrado para atualização.', 'error');
                    this.loading = false;
                    return;
                }
                const res = await fetch(`/api/admin/professor/${this.professorData.id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(this.professorData)
                });
                const data = await res.json();
                if (data.success) {
                    this.showMessage('Dados do professor atualizados com sucesso!', 'success');
                    await this.loadAllData();
                } else {
                    this.showMessage(`Erro ao atualizar dados do professor: ${data.error}`, 'error');
                }
            } catch (err) {
                this.showMessage('Erro ao conectar ao servidor para salvar dados do professor.', 'error');
                console.error('Save professor data error:', err);
            } finally {
                this.loading = false;
            }
        },

        openModal(type, item = null) {
            this.modalType = type;
            this.currentEditItem = item;
            this.newItem = JSON.parse(JSON.stringify({
                publicacao: { titulo_pt: '', revista: '', resumo_pt: '', titulo_en: '', abstract_en: '', data_publicacao: '', doi: '', lattes_url: '', is_featured: false },
                projeto: { titulo_pt: '', tipo: '', status: '', descricao_pt: '', titulo_en: '', descricao_en: '', data_inicio: '', data_termino: '' },
                orientacao: { aluno_nome: '', nivel: '', status: '', titulo_tese_pt: '', titulo_tese_en: '', data_inicio: '', data_defesa: '' }
            }));

            if (item) {
                this.modalTitle = `Editar ${type.charAt(0).toUpperCase() + type.slice(1)}`;
                Object.assign(this.newItem[type], JSON.parse(JSON.stringify(item)));

                if (type === 'publicacao' && this.newItem[type].data_publicacao) {
                    this.newItem[type].data_publicacao = this.newItem[type].data_publicacao.split('T')[0];
                }
                if (type === 'projeto' && this.newItem[type].data_inicio) {
                    this.newItem[type].data_inicio = this.newItem[type].data_inicio.split('T')[0];
                }
                if (type === 'projeto' && this.newItem[type].data_termino) {
                    this.newItem[type].data_termino = this.newItem[type].data_termino.split('T')[0];
                }
                if (type === 'orientacao' && this.newItem[type].data_inicio) {
                    this.newItem[type].data_inicio = this.newItem[type].data_inicio.split('T')[0];
                }
                if (type === 'orientacao' && this.newItem[type].data_defesa) {
                    this.newItem[type].data_defesa = this.newItem[type].data_defesa.split('T')[0];
                }
                if (type === 'publicacao' && 'is_featured' in this.newItem[type]) {
                    this.newItem[type].is_featured = !!this.newItem[type].is_featured;
                }

            } else {
                this.modalTitle = `Nova ${type.charAt(0).toUpperCase() + type.slice(1)}`;
            }
            this.showModal = true;
        },

        closeModal() {
            this.showModal = false;
            this.modalTitle = '';
            this.modalType = '';
            this.currentEditItem = null;
            this.newItem = {
                publicacao: { titulo_pt: '', revista: '', resumo_pt: '', titulo_en: '', abstract_en: '', data_publicacao: '', doi: '', lattes_url: '', is_featured: false },
                projeto: { titulo_pt: '', tipo: '', status: '', descricao_pt: '', titulo_en: '', descricao_en: '', data_inicio: '', data_termino: '' },
                orientacao: { aluno_nome: '', nivel: '', status: '', titulo_tese_pt: '', titulo_tese_en: '', data_inicio: '', data_defesa: '' }
            };
        },

        async saveItem() {
            let endpointSuffix;
            if (this.modalType === 'publicacao') {
                endpointSuffix = 'publicacoes';
            } else if (this.modalType === 'projeto') {
                endpointSuffix = 'projetos';
            } else if (this.modalType === 'orientacao') {
                endpointSuffix = 'orientacoes';
            } else {
                console.error('Tipo de modal desconhecido:', this.modalType);
                this.showMessage('Erro interno: Tipo de item desconhecido.', 'error');
                return;
            }

            const endpoint = `/api/admin/${endpointSuffix}`;
            const method = this.currentEditItem ? 'PUT' : 'POST';
            const itemId = this.currentEditItem ? `/${this.currentEditItem.id}` : '';

            const itemToSave = JSON.parse(JSON.stringify(this.newItem[this.modalType]));
            for (const key in itemToSave) {
                if (itemToSave[key] === '') {
                    itemToSave[key] = null;
                }
                if (key === 'is_featured') {
                     itemToSave[key] = !!itemToSave[key];
                }
            }

            try {
                const res = await fetch(`${endpoint}${itemId}`, {
                    method: method,
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(itemToSave)
                });
                const data = await res.json();
                if (data.success) {
                    this.showMessage(`Item ${this.currentEditItem ? 'atualizado' : 'adicionado'} com sucesso!`);
                    this.closeModal();
                    await this.loadAllData();
                } else {
                    this.showMessage(`Erro ao ${this.currentEditItem ? 'atualizar' : 'adicionar'} item: ${data.error}`, 'error');
                }
            } catch (err) {
                this.showMessage(`Erro ao conectar ao servidor para salvar ${this.modalType}.`, 'error');
                console.error(`Save ${this.modalType} error:`, err);
            }
        },

        async deleteItem(type, id) {
            let endpointSuffix;
            if (type === 'publicacoes') {
                endpointSuffix = 'publicacoes';
            } else if (type === 'projetos') {
                endpointSuffix = 'projetos';
            } else if (type === 'orientacoes') {
                endpointSuffix = 'orientacoes';
            } else if (type === 'contatos') {
                endpointSuffix = 'contatos';
            } else {
                console.error('Tipo de item desconhecido para exclusão:', type);
                this.showMessage('Erro interno: Tipo de item desconhecido para exclusão.', 'error');
                return;
            }

            if (confirm('Deseja realmente excluir?')) {
                try {
                    const res = await fetch(`/api/admin/${endpointSuffix}/${id}`, { method: 'DELETE' });
                    const data = await res.json();
                    if (data.success) {
                        this.showMessage('Item excluído com sucesso!');
                        await this.loadAllData();
                    } else {
                        this.showMessage(`Erro ao excluir item: ${data.error}`, 'error');
                    }
                } catch (err) {
                    this.showMessage('Erro ao conectar ao servidor para excluir item.', 'error');
                    console.error('Delete item error:', err);
                }
            }
        },

        async markAsRead(id, currentStatus) {
            try {
                const res = await fetch(`/api/admin/contatos/${id}/read`, { method: 'POST' });
                const data = await res.json();
                if (data.success) {
                    this.showMessage('Mensagem marcada como ' + (currentStatus ? 'não lida' : 'lida'));
                    await this.loadAllData();
                } else {
                    this.showMessage('Erro ao marcar mensagem.', 'error');
                }
            } catch (err) {
                this.showMessage('Erro ao conectar ao servidor para marcar mensagem.', 'error');
                console.error('Mark as read error:', err);
            }
        },

        viewMessage(message) {
            this.currentMessage = message;
            this.showMessageModal = true;
        },

        closeMessageModal() {
            this.showMessageModal = false;
            this.currentMessage = {};
        },

        showMessage(msg, type = 'success') {
            this.message = msg;
            this.messageType = type;
            setTimeout(() => { this.message = null; }, 3000);
        },

        formatDate(dateStr) {
            if (!dateStr) return '';
            const date = new Date(dateStr);
            if (isNaN(date.getTime())) {
                const parts = dateStr.split('-');
                if (parts.length === 3) {
                    const parsedDate = new Date(parseInt(parts[0]), parseInt(parts[1]) - 1, parseInt(parts[2]));
                    if (!isNaN(parsedDate.getTime())) {
                        return parsedDate.toLocaleDateString('pt-BR');
                    }
                }
                return dateStr;
            }
            return date.toLocaleDateString('pt-BR');
        },

        formatDateTime(dateTimeStr) {
            if (!dateTimeStr) return '';
            try {
                let date = new Date(dateTimeStr);
                if (isNaN(date.getTime())) {
                    return dateTimeStr;
                }
                const options = { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' };
                return date.toLocaleDateString('pt-BR', options);
            } catch (e) {
                return dateTimeStr;
            }
        }
    }));
});