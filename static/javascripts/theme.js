// Theme custom js methods
$(document).ready(function(){

  var addChartsAlert = function(selector){
    var str = {
      'es': 'Datos actualizados a 31 de octubre de 2017',
      'en': 'Data up to 31st October 2017'
    };
    var cont = $(selector);
    if( cont.length > 0 ){
      cont.prepend('<div class="alert alert-data-update">'+str[ $('html').attr('lang') ]+'</div>');
    }
  };

  var addYearSelectorCustomLabels = function(){
    var str2017 = {
      'es': 'prórroga 2016',
      'en': 'extended 2016',
    };

    $('.data-controllers .layout-slider .slider .slider-tick-label').each(function(){
      var val = $(this).html();
      if (val === '2017'){
        $(this).html(val + '<br/><small><i> ('+ str2017[ $('html').attr('lang') ] +')</i></small>');
      }
    });
  };

  // Custom for descriptions in some programmes
  var addCustomDescriptions = function(){
    var descriptions = {
      '/es/politicas/01': {
        'text': '<p>En el año 2013, se llevó a cabo una refinanciación por importe de 333.773.499 € con '+
          'motivo de la subrogación del Ayuntamiento en la posición deudora de la empresa municipal '+
          'Madrid Espacios y Congresos, S.A. y en parte de la deuda de la Empresa Municipal de la '+
          'Vivienda y Suelo, S.A. Este importe, 333,8 millones, no se debe considerar como amortización de 2013 '+
          'ya que no supone una carga real de 2013.</p><p>En el año 2014 se procedió a la refinanciación con '+
          'entidades de crédito privadas del saldo vivo de las operaciones concertadas a través del Fondo estatal '+
          'para la Financiación de los pagos a Proveedores; el importe de tal refinanciación ascendió a '+
          '992.333.741,92 €. Como consecuencia de ello, en los gastos por amortización del año es preciso detraer '+
          'esos 992,3 millones, ya que no suponen carga real de 2014.</p>',
      },
      '/es/programas/01111': {
        'text': '<p>En el año 2013, se llevó a cabo una refinanciación por importe de 333.773.499 € con '+
          'motivo de la subrogación del Ayuntamiento en la posición deudora de la empresa municipal '+
          'Madrid Espacios y Congresos, S.A. y en parte de la deuda de la Empresa Municipal de la '+
          'Vivienda y Suelo, S.A. Este importe, 333,8 millones, no se debe considerar como amortización de 2013 '+
          'ya que no supone una carga real de 2013.</p><p>En el año 2014 se procedió a la refinanciación con '+
          'entidades de crédito privadas del saldo vivo de las operaciones concertadas a través del Fondo estatal '+
          'para la Financiación de los pagos a Proveedores; el importe de tal refinanciación ascendió a '+
          '992.333.741,92 €. Como consecuencia de ello, en los gastos por amortización del año es preciso detraer '+
          'esos 992,3 millones, ya que no suponen carga real de 2014.</p>',
      },
    };

    var description = descriptions[ window.location.pathname.substring(0,window.location.pathname.lastIndexOf('/')) ];

    if (description) {
      $('.policies .policies-content .policies-chart').append( '<div class="policy-description">'+description.text+'</div>' );
    }
  };

  // Custom description for investments
  var addInvestmentsDescriptions = function(){
    var description = '<p>La clasificación de las inversiones del Ayuntamiento y de los Organismos Autónomos se '+
      'realiza siguiendo la estructura que establece la Orden EHA/3565/2008 de 3 de diciembre, por la que se aprueba '+
      'la estructura de los presupuestos de las entidades locales.</p><p>En el Ayuntamiento de Madrid, además, se '+
      'utiliza una clasificación por Líneas de inversión, herramienta más sencilla y simplificada para analizar y '+
      'exponer el destino de las inversiones. </p>';

    if ($('html').attr('lang') == 'es' && $('section.investment-breakdown').length) {
      $('.investments .investments-content .policies-chart').append( '<div class="policy-description">'+description+'</div>' );
    }
  };

  // Swap order of budgeted/actual totals in Overview page
  var swapTotalsInOverview = function(){
    $(".total-budgeted").prependTo(".budget-totals .panel-content");
  };


  // addYearSelectorCustomLabels();

  // Setup lang dropdown
  $('.dropdown-toggle').dropdown();

  addChartsAlert('.policies-chart');
  addChartsAlert('.sankey-container');

  swapTotalsInOverview();

  addCustomDescriptions();

  addInvestmentsDescriptions();
});