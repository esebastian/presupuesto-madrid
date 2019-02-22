/* global FileReader, Papa, Handsontable, Base64 */

function disableButtons() {
  disableButton('save');
  disableButton('load');
}

function enableButtons() {
  enableButton('save');
  enableButton('load');
}

function onSaveSuccess(response) {
  showSuccess('save', response);
}

function onSaveError(response) {
  showError('save', response);
}

function onLoadSuccess(response) {
  showSuccess('load', response);
}

function onLoadError(response) {
  showError('load', response);
}

function onDataChange(changes) {
  clearResult('save');
  clearResult('load');
}

$(document).ready(function () {
  var handsontableTable = {};
  var url = 'population/retrieve';
  var tableContainer = $('#handsontable-container').get(0);

  tableContainer.innerHTML = '';
  tableContainer.className = '';

  Papa.parse(url, {
    download: true,
    header: true,
    skipEmptyLines: true,
    complete: function (results) {
      handsontableTable = new Handsontable(tableContainer, {
        data: results.data,
        rowHeaders: true,
        columnSorting: true,
        colHeaders: ['#Id', '#Entidad', '#Año', '#Población'],
        columns: [
          { data: '#Id', type: 'numeric' },
          { data: '#Entidad' },
          { data: '#Año', type: 'numeric' },
          { data: '#Población', type: 'numeric', numericFormat: { pattern: '0,000', culture: 'es-ES' } }
        ],
        contextMenu: true,
        width: 400,
        height: 400,
        afterChange: onDataChange
      });
    }
  });

  $('#data-save').submit(function(e) {
    e.preventDefault();

    disableButtons();
    clearResult('save');
    showSpinner('save');

    var data = exportAsString(handsontableTable);
    var content = Base64.encode(data);

    $.ajax({
      url: 'population/save',
      method: 'POST',
      data: {
        content: content,
      },
      contentType: 'application/json; charset=utf-8',
      success: onSaveSuccess,
      error: onSaveError,
      complete: enableButtons
    });
  });

  $('#data-load').submit(function(e) {
    e.preventDefault();

    disableButtons();
    clearResult('load');
    showSpinner('load');

    $.ajax({
      url: 'population/load',
      success: onLoadSuccess,
      error: onLoadError,
      complete: enableButtons
    });
  });
});
