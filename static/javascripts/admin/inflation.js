$(document).ready(function () {
  var config = {
    colHeaders: ['#Año', '#Variación'],
    columns: [
      { data: '#Año', type: 'numeric' },
      { data: '#Variación', type: 'numeric', numericFormat: { pattern: '0.0', culture: 'es-ES' } }
    ],
    width: 300,
    height: 300
  }

  renderTable('inflation', config)
});
