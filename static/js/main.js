// Delete confirmation for any form with data-confirm attribute
document.querySelectorAll('form[data-confirm]').forEach(function(form) {
  form.addEventListener('submit', function(e) {
    var msg = this.dataset.confirm || 'Are you sure?';
    if (!confirm(msg)) {
      e.preventDefault();
    }
  });
});

// Auto-dismiss flash messages after 5 seconds
document.querySelectorAll('.flash').forEach(function(el) {
  setTimeout(function() {
    el.style.transition = 'opacity 0.5s ease';
    el.style.opacity = '0';
    setTimeout(function() {
      if (el.parentNode) el.parentNode.removeChild(el);
    }, 500);
  }, 5000);
});

// Decision search + tag filter (character detail page)
(function () {
  var searchInput   = document.getElementById('decision-search');
  var decisionsList = document.getElementById('decisions-list');
  var noResultsMsg  = document.getElementById('no-decisions-msg');
  var countBadge    = document.getElementById('decisions-visible-count');

  if (!searchInput || !decisionsList) return;

  var entries     = Array.from(decisionsList.querySelectorAll('.decision-entry'));
  var activeTag   = '';   // '' = All
  var searchTerm  = '';

  function normalise(str) {
    return (str || '').toLowerCase();
  }

  function applyFilters() {
    var visible = 0;

    entries.forEach(function (entry) {
      var text    = normalise(entry.dataset.text  || '');
      var tags    = normalise(entry.dataset.tags  || '');

      var matchesSearch = !searchTerm || text.indexOf(searchTerm) !== -1;
      var matchesTag    = !activeTag  || tags.split(',').map(function(t){ return t.trim(); }).indexOf(activeTag) !== -1;

      var show = matchesSearch && matchesTag;
      entry.style.display = show ? '' : 'none';
      if (show) visible++;
    });

    // Update count badge
    if (countBadge) countBadge.textContent = visible;

    // Show/hide no-results message
    if (noResultsMsg) noResultsMsg.style.display = (visible === 0) ? '' : 'none';
  }

  // Search input listener
  searchInput.addEventListener('input', function () {
    searchTerm = normalise(this.value.trim());
    applyFilters();
  });

  // Tag filter button listeners
  document.querySelectorAll('.tag-filter-btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      document.querySelectorAll('.tag-filter-btn').forEach(function (b) {
        b.classList.remove('active');
      });
      this.classList.add('active');
      activeTag = normalise(this.dataset.tag || '');
      applyFilters();
    });
  });
}());
