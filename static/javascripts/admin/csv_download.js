function disableButtons() {
  disableButton('download');
  disableButton('review');
  disableButton('load');
}

function enableButtons() {
  enableButton('download');
  enableButton('review');
  enableButton('load');
}

function onDownloadSuccess(response) {
  showSuccess('download', response);
}

function onDownloadError(response) {
  showError('download', response);
}

function onReviewSuccess(response) {
  showSuccess('review', response);
}

function onReviewError(response) {
  showError('review', response);
}

function onLoadSuccess(response) {
  showSuccess('load', response);
}

function onLoadError(response) {
  showError('load', response);
}
