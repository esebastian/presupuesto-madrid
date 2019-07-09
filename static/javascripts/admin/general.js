$(document).ready(function () {
  $('#data-download').submit(function(e) {
    e.preventDefault();

    disableButtons();
    clearResult('download');
    clearResult('review');
    clearResult('load');
    showSpinner('download');

    $.ajax({
      url: "general/retrieve",
      data: {
        year:  $('#year').val()
      },
      contentType: 'application/json; charset=utf-8',
      success: onDownloadSuccess,
      error: onDownloadError,
      complete: enableButtons
    });
  });

  $('#data-review').submit(function(e) {
    e.preventDefault();

    disableButtons();
    clearResult('review');
    clearResult('load');
    showSpinner('review');

    $.ajax({
      url: "general/review",
      contentType: 'application/json; charset=utf-8',
      success: onReviewSuccess,
      error: onReviewError,
      complete: enableButtons
    });
  });

  $('#data-load').submit(function(e) {
    e.preventDefault();

    disableButtons();
    clearResult('load');
    showSpinner('load');

    $.ajax({
      url: "general/load",
      contentType:    'application/json; charset=utf-8',
      success: onLoadSuccess,
      error: onLoadError,
      complete: enableButtons
    });
  });
});
