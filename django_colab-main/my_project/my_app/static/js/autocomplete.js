document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('search-input');
    const searchForm = document.getElementById('search-form');
    const suggestionsBox = document.getElementById('search-suggestions');

    searchInput.addEventListener('input', function() {
        const query = searchInput.value.trim();
        if (query.length > 2) {
            fetch(`${SEARCH_SUGGESTIONS_URL}?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    suggestionsBox.innerHTML = '';
                    if (data.suggestions.length > 0) {
                        suggestionsBox.style.display = 'block';
                        data.suggestions.forEach(suggestion => {
                            const suggestionItem = document.createElement('div');
                            suggestionItem.textContent = suggestion.title;
                            suggestionItem.style.cursor = 'pointer';
                            suggestionItem.style.padding = '5px';
                            suggestionItem.style.pointerEvents = 'auto';

                            // Use 'mousedown' to prevent the blur from killing the click.
                            suggestionItem.addEventListener('mousedown', function(event) {
                                // Construct the target URL:
                                const targetUrl = `${BLOG_POST_DETAIL_URL_PREFIX}${suggestion.id}/`;
                                console.log("Autocomplete redirect ->", targetUrl);

                                // Immediately go to that detail page:
                                window.location.href = targetUrl;
                            });

                            suggestionsBox.appendChild(suggestionItem);
                        });
                    } else {
                        suggestionsBox.style.display = 'none';
                    }
                })
                .catch(error => {
                    console.error('Error fetching suggestions:', error);
                });
        } else {
            suggestionsBox.style.display = 'none';
        }
    });

    // Hide suggestions on blur, but wait briefly to allow mousedown to happen:
    searchInput.addEventListener('blur', function() {
        setTimeout(() => {
            // Only hide if the newly focused element is NOT inside suggestionsBox
            if (!suggestionsBox.contains(document.activeElement)) {
                suggestionsBox.style.display = 'none';
            }
        }, 200);
    });

    // Fallback: if user presses Enter or Search button
    searchForm.addEventListener('submit', function(event) {
        event.preventDefault();
        const query = searchInput.value.trim();
        if (query) {
            // If your 'search' route is /my_app/search/, then:
            // window.location.href = `/my_app/search/?q=${encodeURIComponent(query)}`;
            // Otherwise, if it's just /search/:
            window.location.href = `/search/?q=${encodeURIComponent(query)}`;
        }
    });
});
