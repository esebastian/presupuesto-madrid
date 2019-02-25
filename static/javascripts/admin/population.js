$(document).ready(function () {
  var config = {
    colHeaders: ['#Id', '#Entidad', '#Año', '#Población'],
    columns: [
      { data: '#Id', type: 'numeric' },
      { data: '#Entidad' },
      { data: '#Año', type: 'numeric' },
      { data: '#Población', type: 'numeric', numericFormat: { pattern: '0,000', culture: 'es-ES' } }
    ],
    width: 400,
    height: 400
  }

  renderTable('population', config)
});
