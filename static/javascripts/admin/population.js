$(document).ready(function () {
  var config = {
    colHeaders: ['#Año', '#Población'],
    columns: [
      { data: '#Año', type: 'numeric' },
      { data: '#Población', type: 'numeric', numericFormat: { pattern: '0,000', culture: 'es-ES' } }
    ],
    width: 300,
    height: 250
  }

  renderTable('population', config)
});
