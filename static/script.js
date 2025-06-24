document.addEventListener('DOMContentLoaded', function () {

    // Seleciona os elementos do DOM
    const increaseButton = document.getElementById('font-increase');
    const decreaseButton = document.getElementById('font-decrease');
    const resetButton = document.getElementById('font-reset');
    const contentToResize = document.getElementById('main-content');

    // Define os limites e o passo da alteração da fonte
    const minFontSize = 12; // em pixels
    const maxFontSize = 22; // em pixels
    const step = 1; // em pixels

    /**
     * Altera o tamanho da fonte do elemento de conteúdo.
     * @param {number} change - O valor a ser adicionado ao tamanho da fonte atual (pode ser positivo ou negativo).
     */
    function changeFontSize(change) {
        // Pega o estilo computado atual do elemento
        const currentSize = parseFloat(window.getComputedStyle(contentToResize, null).getPropertyValue('font-size'));
        
        let newSize = currentSize + change;

        // Limita o tamanho da fonte aos valores mínimo e máximo
        if (newSize < minFontSize) {
            newSize = minFontSize;
        } else if (newSize > maxFontSize) {
            newSize = maxFontSize;
        }
        
        // Aplica o novo tamanho da fonte
        contentToResize.style.fontSize = newSize + 'px';
    }

    /**
     * Reseta o tamanho da fonte para o valor padrão (removendo o estilo inline).
     */
    function resetFontSize() {
        contentToResize.style.fontSize = '';
    }

    // Adiciona os ouvintes de evento aos botões
    if (increaseButton && decreaseButton && resetButton && contentToResize) {
        increaseButton.addEventListener('click', () => changeFontSize(step));
        decreaseButton.addEventListener('click', () => changeFontSize(-step));
        resetButton.addEventListener('click', resetFontSize);
    }

    // --- CONTROLE DE ALTO CONTRASTE ---
    const contrastButton = document.getElementById('contrast-toggle');
    const body = document.body;

    // Verifica se o modo de alto contraste já está salvo no localStorage
    function loadContrastPreference() {
        if (localStorage.getItem('highContrast') === 'true') {
            body.classList.add('high-contrast');
        }
    }

    // Alterna o modo de alto contraste
    function toggleContrast() {
        const isHighContrast = body.classList.toggle('high-contrast');
        localStorage.setItem('highContrast', isHighContrast);
    }

    // Adiciona os ouvintes de evento
    if (contrastButton) {
        contrastButton.addEventListener('click', toggleContrast);
    }

    // Os ouvintes de evento para os botões de fonte já estão definidos acima.
    // removi a duplicação dos listeners de fonte aqui.

    // Carrega as preferências ao iniciar a página
    loadContrastPreference();

    // --- Melhorias de Acessibilidade (Próximos Passos) ---
    // Adicionar atalhos de teclado (ex: Alt+A para aumentar fonte, Alt+D para diminuir)
    document.addEventListener('keydown', function(event) {
        if (event.altKey) {
            if (event.key === 'a' || event.key === 'A') { // Alt + A para aumentar fonte
                changeFontSize(step);
            } else if (event.key === 'd' || event.key === 'D') { // Alt + D para diminuir fonte
                changeFontSize(-step);
            } else if (event.key === 'r' || event.key === 'R') { // Alt + R para resetar fonte
                resetFontSize();
            } else if (event.key === 'c' || event.key === 'C') { // Alt + C para contraste
                toggleContrast();
            }
        }
    });

    // Melhorar foco visível (já é geralmente tratado pelo CSS padrão do navegador, mas pode ser customizado)
    // Exemplo em CSS: button:focus { outline: 2px solid blue; outline-offset: 2px; }

    // Considerar ARIA attributes para elementos que precisam de semântica adicional
    // Ex: botões de acessibilidade já têm aria-label

});