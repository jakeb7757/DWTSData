// Search and navigation work as ordinary links and GET forms without this file.
// This enhancement adds debounced, keyboard-accessible search suggestions.
(() => {
    const input = document.getElementById('search-input');
    if (!input) return;
    const list = document.getElementById('autocomplete-list');
    const status = document.getElementById('search-status');
    const form = input.closest('form');
    let timer;
    let controller;
    let generation = 0;
    let focused = -1;

    input.setAttribute('role', 'combobox');
    input.setAttribute('aria-autocomplete', 'list');
    input.setAttribute('aria-controls', list.id);
    input.setAttribute('aria-expanded', 'false');

    function close() {
        clearTimeout(timer);
        controller?.abort();
        generation += 1;
        focused = -1;
        list.replaceChildren();
        list.hidden = true;
        input.setAttribute('aria-expanded', 'false');
        input.removeAttribute('aria-activedescendant');
        status.textContent = '';
    }

    function select(name) {
        input.value = name;
        close();
        form.requestSubmit();
    }

    input.addEventListener('input', () => {
        close();
        const query = input.value.trim();
        if (!query) return;
        const requestGeneration = generation;
        timer = setTimeout(async () => {
            controller = new AbortController();
            try {
                const response = await fetch(`${input.dataset.namesUrl}?q=${encodeURIComponent(query)}`, { signal: controller.signal });
                if (!response.ok) throw new Error(`Search returned ${response.status}`);
                const names = await response.json();
                if (requestGeneration !== generation || document.activeElement !== input) return;
                if (!Array.isArray(names)) throw new Error('Invalid search response');
                const suggestions = [...new Set(names)].slice(0, 6);
                for (const [index, name] of suggestions.entries()) {
                    const option = document.createElement('div');
                    option.id = `search-option-${index}`;
                    option.className = 'autocomplete-option';
                    option.setAttribute('role', 'option');
                    option.setAttribute('aria-selected', 'false');
                    option.textContent = name;
                    // Keep focus on the combobox when selecting with a pointer.
                    option.addEventListener('pointerdown', event => event.preventDefault());
                    option.addEventListener('click', () => select(name));
                    list.append(option);
                }
                list.hidden = suggestions.length === 0;
                input.setAttribute('aria-expanded', String(suggestions.length > 0));
                status.textContent = suggestions.length ? `${suggestions.length} suggestions available. Use up and down arrows to choose.` : 'No suggestions. You can still submit your search.';
            } catch (error) {
                if (error.name !== 'AbortError' && requestGeneration === generation) {
                    status.textContent = 'Suggestions are unavailable. Press Enter to search.';
                }
            }
        }, 250);
    });

    input.addEventListener('keydown', event => {
        const options = [...list.children];
        if (event.key === 'Escape') {
            event.preventDefault();
            close();
        } else if ((event.key === 'ArrowDown' || event.key === 'ArrowUp') && options.length) {
            event.preventDefault();
            focused = event.key === 'ArrowDown' ? (focused + 1) % options.length : (focused <= 0 ? options.length - 1 : focused - 1);
            options.forEach((option, index) => option.setAttribute('aria-selected', String(index === focused)));
            input.setAttribute('aria-activedescendant', options[focused].id);
        } else if (event.key === 'Enter' && focused >= 0 && options[focused]) {
            event.preventDefault();
            select(options[focused].textContent);
        } else if (event.key === 'Tab') {
            close();
        }
    });
    input.addEventListener('blur', close);
    form.addEventListener('submit', close);
    document.addEventListener('pointerdown', event => {
        if (!form.contains(event.target)) close();
    });
})();
