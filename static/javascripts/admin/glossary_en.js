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
  var url = 'en/retrieve';
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
        colHeaders: ['#Título', '#Descripción'],
        contextMenu: true,
        width: 950,
        height: 800,
        className: "htLeft",
        autoRowSize: true,
        colWidths: [350, 550],
        stretchH: 'all',
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
      url: 'en/save',
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
      url: 'en/load',
      success: onLoadSuccess,
      error: onLoadError,
      complete: enableButtons
    });
  });
});
