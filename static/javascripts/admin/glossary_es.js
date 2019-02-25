$(document).ready(function () {
  var config = {
    colHeaders: ['#Título', '#Descripción'],
    width: 950,
    height: 800,
    className: "htLeft",
    autoRowSize: true,
    colWidths: [350, 550],
    stretchH: 'all'
  }

  renderTable('es', config)
});
