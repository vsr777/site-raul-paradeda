document.addEventListener('DOMContentLoaded', function() {
    const projectListContainer = document.getElementById('project-list-container');
    const typeFilter = document.getElementById('type-filter');
    const statusFilter = document.getElementById('status-filter');
    const clearFiltersButton = document.getElementById('clear-filters');
    const loadingMessage = projectListContainer.querySelector('.no-results'); // Para "Carregando projetos..."

    let allProjects = []; // Armazenará todos os projetos carregados do backend

    async function loadProjects() {
        if (loadingMessage) {
            loadingMessage.textContent = 'Carregando projetos...';
            loadingMessage.classList.remove('hidden');
        }
        projectListContainer.innerHTML = ''; // Limpa antes de carregar

        try {
            // CORREÇÃO AQUI: A URL da API deve corresponder à rota definida no Flask
            // No flask_admin_enhanced.py, a rota pública é '/api/projetos'
            const response = await fetch('/api/projetos'); 
            if (!response.ok) {
                throw new Error(`Erro HTTP! Status: ${response.status}`);
            }
            allProjects = await response.json();
            
            if (allProjects.length === 0) {
                if (loadingMessage) {
                    loadingMessage.textContent = 'Nenhum projeto encontrado.';
                    loadingMessage.classList.remove('hidden');
                }
                return;
            }

            displayProjects(allProjects); // Exibe todos os projetos inicialmente
        } catch (error) {
            console.error('Erro ao carregar projetos:', error);
            if (loadingMessage) {
                loadingMessage.textContent = `Erro ao carregar os projetos: ${error.message}. Tente novamente.`;
                loadingMessage.classList.remove('hidden');
            } else {
                projectListContainer.innerHTML = `<p class="no-results">Erro ao carregar os projetos: ${error.message}. Tente novamente.</p>`;
            }
        } finally {
            // A mensagem de carregamento será escondida se displayProjects for bem-sucedida,
            // ou persistirá se houver erro ou nenhum projeto.
            if (loadingMessage && projectListContainer.children.length > 0) {
                 loadingMessage.classList.add('hidden');
            }
        }
    }

    function displayProjects(projectsToShow) {
        projectListContainer.innerHTML = ''; // Limpa a lista existente antes de exibir
        
        if (projectsToShow.length === 0) {
            const noResultsElement = document.getElementById('no-results');
            if (noResultsElement) {
                noResultsElement.classList.remove('hidden');
            }
            return;
        } else {
            const noResultsElement = document.getElementById('no-results');
            if (noResultsElement) {
                noResultsElement.classList.add('hidden'); // Esconde a mensagem de "nenhum resultado"
            }
        }

        // Agrupar projetos por tipo (Pesquisa, Extensão, Ensino) e manter a ordem
        const typesOrder = ['pesquisa', 'extensao', 'ensino']; // Defina a ordem desejada
        const groupedProjects = {};

        // Inicializa grupos em ordem para garantir a exibição correta
        typesOrder.forEach(type => {
            groupedProjects[type.toUpperCase()] = []; // Use uppercase para o título da categoria
        });

        projectsToShow.forEach(proj => {
            // Já esperamos que proj.tipo e proj.status estejam em minúsculas e snake_case do JSON
            const typeKey = proj.tipo ? proj.tipo.toUpperCase() : 'OUTRO'; // Transforma para maiúsculas para o título da categoria
            if (!groupedProjects[typeKey]) {
                groupedProjects[typeKey] = [];
            }
            groupedProjects[typeKey].push(proj);
        });

        // Itera sobre a ordem definida para exibir as categorias
        typesOrder.forEach(typeKey => {
            const projectsInType = groupedProjects[typeKey.toUpperCase()];

            if (projectsInType && projectsInType.length > 0) {
                const categorySection = document.createElement('div');
                categorySection.className = 'category-section'; // Usa a classe existente 'category-section'
                // Título da categoria (ex: PESQUISA, EXTENSÃO)
                categorySection.innerHTML = `<h3 class="category-title">${typeKey.toUpperCase()}</h3><div class="cards-grid"></div>`;
                const cardGrid = categorySection.querySelector('.cards-grid');

                projectsInType.forEach(proj => {
                    const langCode = document.documentElement.lang || 'pt'; // Obter o idioma atual do HTML
                    // Acessa o título e descrição com base no idioma
                    const title = proj[`titulo_${langCode}`] || proj.titulo_pt;
                    const description = (proj[`descricao_${langCode}`] || proj.descricao_pt || '').substring(0, 120) + '...';
                    
                    // Converte status para um formato amigável e para a classe CSS
                    const statusMapping = {
                        'em_andamento': langCode === 'pt' ? 'EM ANDAMENTO' : 'IN PROGRESS',
                        'concluido': langCode === 'pt' ? 'CONCLUÍDO' : 'COMPLETED',
                        'planejamento': langCode === 'pt' ? 'PLANEJAMENTO' : 'PLANNING',
                        'proposto': langCode === 'pt' ? 'PROPOSTO' : 'PROPOSED',
                        'default': langCode === 'pt' ? 'INDEFINIDO' : 'UNDEFINED'
                    };
                    const statusText = statusMapping[proj.status] || statusMapping['default'];
                    const statusClass = proj.status || 'indefinido'; // Usar o status em snake_case como classe

                    const projectCard = document.createElement('div');
                    projectCard.className = 'card project-card'; // Adiciona 'project-card'
                    projectCard.innerHTML = `
                        <h4>${title}</h4>
                        <div class="status ${statusClass}">${statusText}</div>
                        <p>${description}</p>
                        <a href="#" class="btn" data-project-id="${proj.id}">${langCode === 'pt' ? 'Ver detalhes' : 'View details'}</a>
                    `;
                    cardGrid.appendChild(projectCard);

                    // Adiciona ouvinte de evento para o botão "Ver detalhes"
                    const detailButton = projectCard.querySelector('.btn');
                    detailButton.addEventListener('click', (event) => {
                        event.preventDefault();
                        console.log('Abrir modal para:', proj);
                        // Aqui você chamaria a lógica do modal, por exemplo:
                        // openProjectDetailModal(proj); // Uma função que você implementaria
                    });
                });
                projectListContainer.appendChild(categorySection);
            }
        });
    }

    function applyFilters() {
        const selectedType = typeFilter ? typeFilter.value.toLowerCase() : '';
        const selectedStatus = statusFilter ? statusFilter.value.toLowerCase() : '';

        let filteredProjects = allProjects.filter(proj => {
            // Agora, esperamos que proj.tipo e proj.status já estejam em minúsculas e snake_case
            const projType = proj.tipo || '';
            const projStatus = proj.status || '';

            const matchesType = !selectedType || projType === selectedType;
            const matchesStatus = !selectedStatus || projStatus === selectedStatus;
            return matchesType && matchesStatus;
        });
        displayProjects(filteredProjects);
    }

    // Event Listeners for filters
    if (typeFilter) {
        typeFilter.addEventListener('change', applyFilters);
    }
    if (statusFilter) {
        statusFilter.addEventListener('change', applyFilters);
    }
    if (clearFiltersButton) {
        clearFiltersButton.addEventListener('click', () => {
            if (typeFilter) typeFilter.value = '';
            if (statusFilter) statusFilter.value = '';
            applyFilters(); // Aplica filtros novamente para limpar
        });
    }

    // Carrega projetos quando a página é carregada
    loadProjects();
});